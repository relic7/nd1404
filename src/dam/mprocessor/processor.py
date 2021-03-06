####################################################################################
#
# Functionalities
# 
# 0.1
# Read the list of items id and the pipeline to operate upon them.
# Create the DAG of the pipeline and request a schedule of single actions.
# Loop over all items and for each item loop over pipeline.
#     On success, execute next actions.
#     On error, log the error, delete all dependent actions from pipeline and 
#     execute next actions.
# 
# 0.2
# Keep the total number of outstanding requests under a predefined limit.
# (Congestion control)
# 
# 0.3
# Invert loop order, looping over pipeline and for each stage on all items.
# This avoids issuing consecutive requests for the same item, avoid stalling
# on NFS locking.
# 
# 0.4
# Paginate the items lookup, to decrease the memory footprint of the mprocessor
# and allow scaling to very large jobs.
# 
# 0.5
# Randomize schedules, associating a schedule to each item. This can help improve
# servers load. Not useful is schedules are natively totally ordered.
# 
#####################################################################################


import os
import datetime
import re
import threading

from django.db.models import Q
from django.db import transaction
from json import loads
from config import Configurator
from . import log
from dam.mprocessor.models import Process, ProcessTarget
from dam.mprocessor.pipeline import DAG
from dam.mprocessor.schedule import Schedule

from dam.kb.tinykb.util import decorators # FIXME: move somewhere else?

from celery.task import task as celery_task

class BatchError(Exception):
    pass

# Guard for process scheduling
_process_run_lock = threading.RLock()

@decorators.synchronized(_process_run_lock)
@transaction.commit_on_success
def run(restarting=False):
    """Run waiting process.
        
    This task tries to run all the waiting processes.

    If restarting=True, processes that were started in the past and
    did not terminate will be run again (useful e.g. in case of crash
    recovery).
    """
    if restarting:
        running_processes = Process.objects.filter(Q(end_date=None) & ~Q(start_date=None))
        log.info("Number of running processes: %d" % len(running_processes))
        for p in running_processes:
            log.info("Restarting processes %s" % (p.pk, ))
            p.start_date = datetime.datetime.now()
            p.save()
            _async_res = run_batch.delay(p.pk)

    waiting_processes = Process.objects.filter(start_date=None)
    log.info("Number of waiting processes: %d" % len(waiting_processes))
    for p in waiting_processes:
        log.info("Running the waiting processes %s" % (p.pk, ))
        p.start_date = datetime.datetime.now()
        p.save()
        _async_res = run_batch.delay(p.pk)

    return 'ok'

@celery_task
def run_batch(process_pk):
    Batch(process_pk).run()

class Batch:
    def __init__(self, process_pk):
        process = Process.objects.get(pk=process_pk)
        self.cfg = Configurator()
        self.max_outstanding = self.cfg.getint('MPROCESSOR', 'max_outstanding')
        self.batch_size = self.cfg.getint('MPROCESSOR', 'batch_size') # how many items to load
        self.pipeline = loads(process.pipeline.params)
        self.dag = DAG(self.pipeline)
        self.schedule_length = len(self.pipeline)
        self.process = process
        self.scripts = self._get_scripts(self.pipeline)
        self.all_targets_read = False      # True when all targets have been read
        self.gameover = False              # True when all targets are done
        self.outstanding = 0               # number of not yet answered requests
        self.cur_batch = 0                 # index in batch
        self.cur_task = 0                  # index in tasks
        self.totals = {'update':0, 'passed':0, 'failed':0, 'targets': 0, None: 0} 
        self.results = {}

    def run(self):
        "Start the iteration initializing state so that the iteration starts correctly"
        log.debug('### Running batch for process %s' % (str(self.process.pk),))
        self.process.targets = ProcessTarget.objects.filter(process=self.process).count()
        self.tasks = []
        self._iterate()

    def stop(self, seconds_offset=0):
        log.info('stopping process %s' % self.process.pk)
        with transaction.commit_on_success():
            when = datetime.datetime.now() + datetime.timedelta(seconds=seconds_offset)
            self.process.end_date = when
            self.process.save()
        self.gameover = True

    def _update_item_stats(self, item, action, result, success, failure, cancelled):
        #log.debug('_update_item_stats: item=%s action=%s success=%s, failure=%s, cancelled=%s' % (item.target_id, action, success, failure, cancelled)) #d
        item.actions_passed += success
        item.actions_failed += failure
        item.actions_cancelled += cancelled
        item.actions_todo -= (success + failure + cancelled)
        if item.pk not in self.results:
            self.results[item.pk] = {}
        self.results[item.pk][action] = (success, result)
        if item.actions_todo <= 0 or failure > 0:
            item.result = dumps(self.results[item.pk])
        if item.actions_todo <= 0:
            #log.debug('_update_item_stats: finalizing item %s' % item.target_id) #d
            del self.results[item.pk]
        
    def _get_scripts(self, pipeline):
        """Load scripts from plugin directory. 
        
           Returns the dictionary
           {'script_name': (callable, params)}
           Throws an exception if not all scripts can be loaded.
        """
        plugins_module = self.cfg.get("MPROCESSOR", "plugins")
        scripts = {}
        for script_key, script_dict in pipeline.items():
            script_name = script_dict['script_name']
            full_name = plugins_module + '.' + script_name + '.run'
            p = full_name.split('.')
            log.info('<$> loading script: %s' % '.'.join(p[:-1]))
            m = __import__('.'.join(p[:-1]), fromlist = p[:-1])
            f = getattr(m, p[-1], None)
            if not f or not callable(f):
                raise BatchError('Plugin %s has no callable run method' % script_name)
            else:
                scripts[script_key] = (f, script_dict.get('params', {}))
        return scripts

    def _new_batch(self):
        "Loads from db the next batch of items and associate a schedule to each item"
        if self.all_targets_read:
            return []

        targetset = ProcessTarget.objects.filter(process=self.process.pk)[self.cur_batch:self.cur_batch + self.batch_size]
        if targetset:
            self.cur_batch += self.batch_size
            ret = [{'item':x, 'schedule':Schedule(self.dag, x.target_id)} for x in targetset]   # item, index of current action, schedule
        else:
            self.all_targets_read = True
            ret = []
        return ret

    def _get_action(self):
        """returns the first action found or None. Delete tasks with no actions left"""
        #log.debug("_get_action on num_tasks=%s" % len(self.tasks)) #d
        to_delete = []
        action = ''
        for n in xrange(len(self.tasks)):
            idx = (self.cur_task + n) % len(self.tasks)
            task = self.tasks[idx]
            action = task['schedule'].action_to_run()
            if action is None:
                to_delete.append(task)
            elif action:
                break

        #log.debug('to_delete %s' % to_delete) #d

        for t in to_delete:                   
            #log.debug('deleting done target %s' % t['item'].target_id) #d
            self.tasks.remove(t)

        # update cur_task so that we do not always start querying the same task for new actions
        if action:
            idx = self.tasks.index(task)
            self.cur_task = (idx + 1) % len(self.tasks)
        else:
            self.cur_task = 0

        # if action is None or empy there is no action ready to run
        # if there are new targets available try to read some and find some new action
        if action:
            return action, task
        else:
            if not self.all_targets_read and self.outstanding < self.max_outstanding:
                new_tasks = self._new_batch()
                if new_tasks:
                    self.cur_task = len(self.tasks)
                    self.tasks.extend(new_tasks)
            if self.all_targets_read and not self.tasks:
                log.debug("_get_action: gameover")
                self.stop()
            return  None, None


    def _iterate(self):
        """ Run the actions listed in schedule on the items returned by _new_batch """
        #log.debug('_iterate: oustanding=%s' % self.outstanding) #d
        while True:
            if self.gameover:
                log.debug('_iterate: gameover')
                return
            action, task = self._get_action()
            if action:
                log.debug('processing action: "%s"' % (action, ))
                item, schedule = task['item'], task['schedule']
                method, params = self.scripts[action]
                try:
                    item_params = loads(item.params)
    
                    # tmp bug fixing starts here
                    for k in params.keys():
                        if params[k] == '' and (k in item_params[action]):
                            params[k] = item_params[action][k]
                    # tmp bug fixing ends here
    
                    params.update(item_params.get('*', {}))
                    x = re.compile('^[a-z_]+' ) # cut out digits from action name
                    params.update(item_params.get(x.match(action).group(), {}))
                    self.outstanding += 1
                    #params = {u'source_variant_name': u'original'}
                    res = method(self.process.workspace, item.target_id, **params)
                    self._handle_ok(res, item, schedule, action, params)
                except Exception, e:
                    log.error('ERROR in %s: %s %s' % (str(method), type(e), str(e)))
                    self._handle_err(str(e), item, schedule, action, params)
            # If _get_action did not find anything and there are no more targets, no action
            # will be available until an action completes and allows more actions to go ready.
            if not (self.outstanding < self.max_outstanding and (action or not self.all_targets_read)):
                break

    def _handle_ok(self, result, item, schedule, action, params):
        #log.info("_handle_ok: target %s: action %s: %s" % (item.target_id, action, result)) #d
        self.outstanding -= 1
        schedule.done(action)
        self._update_item_stats(item, action, result, 1, 0, 0)
        item.save()

    def _handle_err(self, result, item, schedule, action, params):
        log.error('_handle_err action %s on target_id=%s: %s (params: %s)' % (action, item.target_id, str(result), str(params)))
        self.outstanding -= 1
        cancelled = schedule.fail(action)
        self._update_item_stats(item, action, str(result), 0, 1, 0)
        for a in cancelled:
            self._update_item_stats(item, a, "cancelled on failed %s" % action, 0, 0, 1)
        item.save()

##############################################################################################
# 
# Test

import sys
from django.contrib.auth.models import User
from dam.mprocessor.make_plugins import pipeline as test_pipe
from dam.mprocessor.make_plugins import simple_pipe as test_pipe2
from dam.mprocessor.models import Pipeline, TriggerEvent
from dam.workspace.models import DAMWorkspace
from json import dumps

##
## Class used to test MProcessor.mq_run 
##
class Batch_test:
    def __init__(self, process):
        self.process = process

    def run(self, seconds_offset = 0):
        log.info('starting process %s' % self.process.pk)
        when = datetime.datetime.now() + datetime.timedelta(seconds=seconds_offset)
        self.process.start_date = when
        self.process.save()

    def stop(self, seconds_offset=0):
        log.info('stopping process %s' % self.process.pk)
        when = datetime.datetime.now() + datetime.timedelta(seconds=seconds_offset)
        self.process.end_date = when
        self.process.save()
        self.gameover = True


class fake_config:
    dictionary = {
        'MPROCESSOR': {
            'plugins': 'dam.mprocessor.plugins',
            'max_outstanding': '17',
            'batch_size': '5',
        },
    }
    def get(self, section, option):
        return self.dictionary[section][option]

    def getint(self, section, option):
        return int(self.dictionary[section][option])

gameover = False

def end_test(result, process):
    global gameover
    gameover = True
    print_stats(process, False)
    log.debug('end of test %s' % result)

def print_stats(process, redo=True):
    if process.targets == 0:
        print >>sys.stderr, 'Process stats: not initialized'
    else:
        print >>sys.stderr, 'Process stats: completed=%d/%d failed=%d/%d' % (process.get_num_target_completed(), process.targets,
                                   process.get_num_target_failed(), process.targets)

    pt = ProcessTarget.objects.filter(process=process, actions_todo=0, actions_failed=0)
    print >>sys.stderr, 'Process stats: completed successfully: %s' % ' '.join([x.target_id for x in pt])
    if not gameover and redo:
        print_stats(process)

def test():
    global Configurator
    Configurator = fake_config
    ws = DAMWorkspace.objects.get(pk=1)
    user = User.objects.get(username='admin')
    t = TriggerEvent.objects.get_or_create(name="test")[0]
    print 't.pk=', t.pk
    try: 
        print 'attempting to reuse pipeline'
        pipeline = Pipeline.objects.get(name='test4', workspace=ws)
    except:
        print 'creating new pipeline'
        pipeline = Pipeline.objects.create(name="test4", description='', params=dumps(test_pipe2), workspace=ws)
        print 'ok'
        pipeline.triggers.add(t)
        print 'ok2'
        pipeline.save()
        print 'done'
    process = Process.objects.create(pipeline=pipeline, workspace=ws, launched_by=user)
    for n in xrange(15):
        print 'adding target %d' % n
        process.add_params(item = 'item%d' % n)
    try:
        batch = Batch(process)
        d = batch.run()
        d.addBoth(end_test, process)
    except Exception, e:
        log.error("Fatal initialization error: %s" % str(e))
        raise
    print_stats(process)
