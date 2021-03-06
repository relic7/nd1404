#########################################################################
#
# NotreDAM, Copyright (C) 2011, Sardegna Ricerche.
# Email: labcontdigit@sardegnaricerche.it
# Web: www.notre-dam.org
#
# This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#########################################################################

from django.contrib.auth.decorators import login_required
from django.http import (HttpRequest, HttpResponse, HttpResponseNotFound,
                         HttpResponseNotAllowed, HttpResponseBadRequest)
from django.utils import simplejson
import tinykb.session as kb_ses
import tinykb.errors as kb_exc
import util
from dam.core.dam_workspace.models import WorkspacePermission, WorkspacePermissionsGroup, WorkspacePermissionAssociation
from dam.workspace.models import DAMWorkspace as Workspace
import kb.views as views_kb # Using the "dam." prefix causes double loading!
import dam.treeview.views as tree_view
from dam.treeview.models import Node
from django.contrib.auth.models import User
from dam.repository.models import Component
import time

import logging
logger = logging.getLogger('dam')

def _get_root_tree(request,ws_id):
    """
    Return root tree for GUI
    """
    logger.debug("_get_root_tree")

    result = []
    spr = [] 
    try:
        with views_kb._kb_session() as ses:
            ws = ses.workspace(ws_id)
            cls_dicts = [views_kb._kbclass_to_dict(o, ses) for o in ses.classes(ws=ws, parent=None, recurse=False)]
        
        logger.debug("Dictionary")
        logger.debug(cls_dicts)
        for n in cls_dicts:
            tmp = {'text' : n['name'],  
               'id': n['id'], 
               'leaf': False,
               'iconCls' : 'object-class',
            }  
            result.append(tmp)
    except Exception, ex:
        logger.debug(ex)

    return result 

def _put_right_value_leaf(c, leaf):
    tmp = {'text' : c["name"],#  non presente ho guardato il nome della classe FIXME chiedere ad alceste
           'id': c["id"], 
           'leaf': leaf, # sarebbe utile avere info a riguardo
           'iconCls' : 'object-class',
        }
    
    return tmp
    
def _get_child_cls_obj(request,ws_id, parent):
    """
    Get child for tree in GUI
    """
    logger.debug("_get_child_cls_obj")
    result = []
    spr = []
    
    try:
        with views_kb._kb_session() as ses:
            
            ws = ses.workspace(ws_id)
            cls_dicts = [views_kb._kbclass_to_dict(o, ses) for o in ses.classes(ws=ws, parent=parent, recurse=False)]
            cls = ses.class_(parent, ws=ws)
            logger.info("cls_dicts")
            logger.info(cls_dicts)
            logger.info("PARENTTTT")
            logger.info(parent)

            #objs = ses.objects(class_=cls.python_class, ws=ws, recurse=False)
            objs = ses.objects(class_=cls.python_class)
            
            logger.info("objs")
            logger.info(objs)
            obj_dicts = [views_kb._kbobject_to_dict(o, ses) for o in objs]
            
            #--- FIXME:some problem with objs = ses.objects(class_=cls.python_class, ws=ws, recurse=False) --
            logger.info("obj_dicts")
            logger.info(obj_dicts)
            objs_bis = []
            for o in obj_dicts:
                print str(o['class_id']) 
                print str(parent)
                if (str(o['class_id']) == str(parent)):
                    objs_bis.append(o)
            #---
        for c in cls_dicts:
            if len(c['subclasses'])>0:
                tmp = _put_right_value_leaf(c, False)
            else:
                tmp = _put_right_value_leaf(c, False)
            result.append(tmp)
            
        for o in objs_bis:
            tmp = {'text' : o['name'],  
                   'id': o['id'], 
                   'leaf': True,
                } 
            result.append(tmp)
    except Exception, ex:
        logger.debug(ex)
    
            
    return result

@login_required
def get_nodes_real_obj(request):
    '''
    Return data to tree in GUI follow the below example:
    treeloader needs :
    [{
        id: 1,
        text: 'A leaf Node',
        leaf: true
    },{
        id: 2,
        text: 'A folder Node',
        children: [{
            id: 3,
            text: 'A child Node',
            leaf: true
        }]
   }]
    '''
    parent = request.POST.get('node',  'root')
    if parent == 'root_obj_tree':
        result = _get_root_tree(request,request.session['workspace'].pk)
    else:
        result = _get_child_cls_obj(request,request.session['workspace'].pk, parent)

    return HttpResponse(simplejson.dumps(result))

def _add_attribute(name, value, groupname):
    """
    Return dictionary.
    """
    tmp = {'name'       :name,
           'value'      :value,
           'groupname'  :groupname
          }
    return tmp

def _test_duplicate(groupname, rtr):
    """
    test to avoid duplicate key
    """
    flag = False
    for item in rtr['rows']:
        if item['groupname'] == groupname:
            flag = True

    return flag

def _put_attributes(cls_obj, rtr):
    """
    Put all attributes for the Object passed.
    """
    if len(rtr['rows'])==0 or _test_duplicate(cls_obj['name'],rtr) == False:
        rtr['rows'].append(_add_attribute('notes', cls_obj['notes'],cls_obj['name']))
        for c in cls_obj['attributes']:
            tmp = _add_attribute(c,cls_obj['attributes'][c],cls_obj['name'])
            rtr['rows'].append(tmp)
    

def get_specific_info_obj(request, obj_id):
    """
    Return all information about obj passed. It's passed obj's id.
    """
    with views_kb._kb_session() as ses:
        ws = ses.workspace(request.session['workspace'].pk)
        cls = ses.object(obj_id, ws=ws)
        rtr = {"rows":[]}
        rtr['rows'].append(views_kb._kbobject_to_dict(cls, ses))
        resp = simplejson.dumps(rtr)
        return HttpResponse(resp)

def get_object_attributes_hierarchy(request):
    """
    Return all information about obj passed. It's passed obj id.
    """
    nodes = tree_view._get_item_nodes(request.POST.getlist('items'))
    with views_kb._kb_session() as ses:
        rtr = {"rows":[]}
        for node in nodes:
            n = Node.objects.get(pk = node.id)
            while n.parent_id:
                if n.kb_object_id:
                    cls = views_kb._kbobject_to_dict(ses.object(n.kb_object_id), ses)
                    _put_attributes(cls,rtr)
                n = Node.objects.get(pk = n.parent_id)
        logger.debug(rtr)
        resp = simplejson.dumps(rtr)
    
    return HttpResponse(resp)

def get_object_attributes(request):
    """
    Return all attributes for obj passed. It's passed obj id and class id.
    """
    class_id = request.POST.getlist('class_id')[0]
    obj_id = request.POST.getlist('obj_id')[0]
    if (obj_id):
        cls_obj = views_kb.object_get(request, request.session['workspace'].pk,obj_id)
        cls_obj = simplejson.loads(cls_obj.content)
    cls_dicts = views_kb.class_get(request, request.session['workspace'].pk,class_id)
    cls_dicts = simplejson.loads(cls_dicts.content) 
    rtr = {"rows":[]}
    for attribute in cls_dicts['attributes']:
        tmp = {}
        tmp['id'] = attribute
        if (obj_id):
            tmp['value'] = cls_obj['attributes'][attribute]
        else:
            tmp['value'] = None
        for specific_field in cls_dicts['attributes'][attribute]:
            tmp[specific_field] = cls_dicts['attributes'][attribute][specific_field]
        rtr['rows'].append(tmp)
    resp = simplejson.dumps(rtr)
    
    return HttpResponse(resp)

def get_class_attributes(request, class_id):
    """
    Return all attributes for class passed. It's passed the class id.
    """
    cls_dicts = views_kb.class_get(request, request.session['workspace'].pk,class_id)
    cls_dicts = simplejson.loads(cls_dicts.content) 
    rtr = {"rows":[]}
    for attribute in cls_dicts['attributes']:
        tmp = {}
        tmp['id'] = attribute
        for specific_field in cls_dicts['attributes'][attribute]:
            tmp[specific_field] = cls_dicts['attributes'][attribute][specific_field]
        rtr['rows'].append(tmp)
    resp = simplejson.dumps(rtr)
    return HttpResponse(resp)
    
    
def get_specific_info_class(request, class_id):
    """
    Return all class information.
    """
    cls_dicts = views_kb.class_get(request, request.session['workspace'].pk,class_id)
    cls_dicts = simplejson.loads(cls_dicts.content) 
    rtr = {"rows":[]}
    rtr['rows'].append(cls_dicts)
    resp = simplejson.dumps(rtr)
    return HttpResponse(resp)

def get_workspaces_with_edit_vocabulary(request):
    """
    Return all workspaces for specific user where user can edit vocabulary.
    """
    user = User.objects.get(pk=request.session['_auth_user_id'])

    wp = WorkspacePermission.objects.get(name= 'edit vocabulary')

    ws_all = Workspace.objects.all()
    rtr = {"workspaces":[]}
    for ws in ws_all:
        ws_tmp = {}
        if (ws.has_permission(user, 'edit_vocabulary')):
            ws_tmp = {
                'pk': ws.pk,
                'name': ws.name,
                'description': ws.description
            }
            rtr['workspaces'].append(ws_tmp)
        
    return HttpResponse(simplejson.dumps(rtr))    


def update_assosiation_treeview(request):
    kb_object_id = request.POST.get('id')
    ws = request.session.get('workspace', None)
    nodes= Node.objects.filter(kb_object = kb_object_id, workspace = request.session['workspace'].pk)

    for node in nodes:
        node.reassoc_node(kb_object_id,ws)

    return HttpResponse(simplejson.dumps("Ok"))    

# don't used
#def get_variant_url(request):
#
#    print "request"
#    print request.POST
#    try:
#        item_id = long(request.POST.get('item_id'))
#        variants_to_get = request.POST.get('variants_to_get')
#        user = User.objects.get(pk=request.session['_auth_user_id'])
#        workspace_id = request.session['workspace'].pk
#        logger.debug(' workspace_id %s' %workspace_id)
#        #ws = Workspace.objects.get(pk = workspace_id)        
#        #workspace = Workspace.objects.get(pk = workspace_id)
#        print(' workspace_id %s type %s; item_id %s type %s' %(workspace_id,type(workspace_id),item_id,type(item_id)))
#        component_list = Component.objects.filter(item__pk = item_id, workspace__pk = workspace_id)
#        print "component_list"
#        print component_list
#        if variants_to_get:
#            print('-----------------------------------variants_to_get %s'%variants_to_get)
#            for c in component_list:
#                if c.get_variant().name == variants_to_get:
#                    print('c.get_url %s'%c.get_url(True))
#                    url  = c.get_url(True)        
#    except Workspace.DoesNotExist,  ex:
#        logger.exception(ex)
#        url = ""
#
#    return HttpResponse(simplejson.dumps(url))    
