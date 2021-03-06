#########################################################################
#
# NotreDAM, Copyright (C) 2009, Sardegna Ricerche.
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

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from dam.preferences.models import UserSetting, SettingValue, DAMComponent, DAMComponentSetting, SystemSetting, WSSetting 
from dam.workspace.models import DAMWorkspace as Workspace
from dam.metadata.models import MetadataLanguage
from dam.settings import LANGUAGE_CODE

import logging
logger = logging.getLogger('dam')


def get_metadata_default_language(user, workspace=None):
    """
    Returns default metadata language for the given user (or the application default)
    """
    component=DAMComponent.objects.get(name__iexact='Language')
    setting=DAMComponentSetting.objects.get(component=component, name__iexact='default_metadata_language')
    comma_separated_languages = setting.get_user_setting(user, workspace)
    list_of_languages = comma_separated_languages.split(',')
    return list_of_languages[0]



@login_required
def get_lang_pref(request):
    """
    Returns the list of available metadata languages chosen by the given user
    """
    workspace = request.session['workspace']
    user = User.objects.get(pk=request.session['_auth_user_id'])
    component=DAMComponent.objects.get(name__iexact='User Interface')
    setting=DAMComponentSetting.objects.get(component=component, name__iexact='supported_languages')
    comma_separated_languages = setting.get_user_setting(user, workspace)
    list_of_languages = comma_separated_languages.split(',')
    resp = {'languages':[]}
    default_language = get_metadata_default_language(user,workspace)
    languages = MetadataLanguage.objects.filter(code__in=list_of_languages).values('code', 'language', 'country')
    for l in languages:
        if l['code'] == default_language:
            l['default_value'] = True
        resp['languages'].append(l)
    return HttpResponse(simplejson.dumps(resp))

@login_required
def get_user_settings(request):
    """
    Returns the list of Settings and the values for the given user
    """
    user = User.objects.get(pk=request.session['_auth_user_id'])
    workspace = request.session.get('workspace')
    settings = DAMComponentSetting.objects.filter(setting_level__in=['U', 'W']).order_by('caption')
    
    data = {'prefs':[]}
    for s in settings:
        choices = [[c.name, c.description] for c in s.choices.all()]
        my_value = s.get_user_setting_by_level(workspace, user, ['U', 'W', 'S'])
        data['prefs'].append({'id':'pref__%d' % s.id, 'name':s.name,'caption': s.caption,'name_component': s.component.name,  'type': s.type,  'value': my_value,  'choices':choices})
    return HttpResponse(simplejson.dumps(data))

@login_required
def save_pref(request):
    """
    Save user preference
    """
    try:
        user = User.objects.get(pk=request.session['_auth_user_id'])
        
        DAMComponentSetting.objects.save_preference(request, user)

        settings = DAMComponentSetting.objects.filter(setting_level__in=['U', 'W']).order_by('caption')
        for p in request.POST:
            for s in settings:
                if str(p[6:]) == str(s.id) and s.name == "application_supported_languages":
	                request.session['django_language'] = request.POST[p][:2]
	                request.session.save()

        return HttpResponse(simplejson.dumps({'success': True}))
    except Exception,  ex:
        logger.exception(ex)
        raise ex
    
@login_required
def save_system_pref(request):
    """
    Save system preference (dam admin)
    """
    try:
        try:
            supported_languages = DAMComponentSetting.objects.get(name = 'supported_languages')
            default_language = DAMComponentSetting.objects.get(name = 'default_metadata_language')
            new_supported_languages = SettingValue.objects.filter(name__in = request.POST.getlist('pref__' + str(supported_languages.pk)))
            default_language.choices.remove(*default_language.choices.all())
            default_language.choices.add(*new_supported_languages)
            
        except DAMComponentSetting.DoesNotExist:
            pass
            
        DAMComponentSetting.objects.save_preference(request, None)
                            
        return HttpResponse(simplejson.dumps({'success': True}))
    except Exception,  ex:
        logger.exception(ex)
        raise ex    

def get_ws_homepage_prefs(ws):
    """
    Returns ws settings about homepage (name for homepage search, ordering_criteria, order_mode)
    """
    ws_homepage = ''
    ws_ordering_criteria = ''
    ws_order_mode = ''
    try:
        component = DAMComponent.objects.get(name__iexact='Homepage')
    except DAMComponent.DoesNotExist:
        return ws_homepage, ws_ordering_criteria, ws_order_mode
    try:
        setting = DAMComponentSetting.objects.filter(component=component)
        homepage_setting = DAMComponentSetting.objects.get(component=component, name__iexact='homepage')
        ws_homepage = homepage_setting.get_ws_preference(ws).value
        ordering_criteria_setting = DAMComponentSetting.objects.get(component=component, name__iexact='ordering_criteria')
        ws_ordering_criteria = ordering_criteria_setting.get_ws_preference(ws).value[1:-1].replace(':', '_')
        order_mode_setting = DAMComponentSetting.objects.get(component=component, name__iexact='order_mode')
        ws_order_mode = order_mode_setting.get_ws_preference(ws).value
    except DAMComponentSetting.DoesNotExist:
        pass
    except AttributeError:
        pass
    return ws_homepage, ws_ordering_criteria, ws_order_mode

@login_required
def get_homepage_prefs(request):
    """
    Returns json resp with ws settings about homepage (name for homepage search, ordering_criteria, order_mode)
    """
    workspace = request.session['workspace']
    homepage, ordering_criteria, order_mode = get_ws_homepage_prefs(workspace)
    resp = {}
    resp['homepage'] = {'homepage':homepage,'ordering_criteria':ordering_criteria, 'order_mode':order_mode}
    return HttpResponse(simplejson.dumps(resp))



@login_required
def save_ws_pref(request):
    """
    Save workspace preference
    """
    try:

        workspace = request.session.get('workspace')

        DAMComponentSetting.objects.save_preference(request, workspace)
                            
        return HttpResponse(simplejson.dumps({'success': True}))
    except Exception,  ex:
        logger.exception(ex)
        raise ex 

def _get_ws_settings(workspace):
    ws_settings = {'prefs':[]}
    try:
        settings = DAMComponentSetting.objects.filter(setting_level='W')
    except DAMComponentSetting.DoesNotExist:
        return ws_settings
        
    for s in settings:
        choices = [[c.name, c.description] for c in s.choices.all()]
        value = s.get_user_setting_by_level(workspace)
        ws_settings['prefs'].append({'id': 'pref__%d'%s.id, 'name':s.name,'caption': s.caption,'name_component': s.component.name,  'type': s.type,  'value': value,  'choices':choices})
    return ws_settings
    
@login_required
def get_ws_settings(request):
    """
    Get workspace settings
    """
    workspace = request.session.get('workspace')
    ws_settings = _get_ws_settings(workspace)
    return HttpResponse(simplejson.dumps(ws_settings))    

@login_required
def account_prefs(request):
    from django.db import IntegrityError

#    username = request.POST['username']
    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    email = request.POST['email']
    #session_language = request.POST['session_language']
    
    current_password = request.POST.get('current_password')
    new_password = request.POST.get('new_password')
    
    if current_password:
        if request.user.check_password(current_password):
            if new_password:
                logger.debug('valid new password')
                request.user.set_password(new_password)
            else:
                logger.error('Invalid new password')
                return HttpResponse(simplejson.dumps({'success': False, 'errors': [{'name':'new_password', 'msg':'new password is invalid'}]}))
            
        else:
            logger.error('wrong current password')
            return HttpResponse(simplejson.dumps({'success': False, 'errors': [{'name':'current_password', 'msg':'password does not match'}]})) 
            
    try:
#        request.user.username = username
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
	#request.session['django_language'] = session_language
	#request.session.save()
    except IntegrityError:
        return HttpResponse(simplejson.dumps({'success': False, 'errors': [{'name':'username', 'msg':'username already used'}]}))
        
    return HttpResponse(simplejson.dumps({'success': True}))
    
@login_required
def get_account_info(request):
    try:
        account_info = {
#        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        #'session_language': request.session['django_language']
        }
    except Exception,  ex:
        logger.exception('ERROR IN ACCOUNT INFO: %s' % ex)
        account_info = {
#        'username': request.user.username,
        'first_name': '',
        'last_name': '',
        'email': '',
        #'session_language': LANGUAGE_CODE,
        }
        #request.session['django_language'] = LANGUAGE_CODE
    logger.debug('account_info %s'%account_info)
    return HttpResponse(simplejson.dumps({'success': True, 'data': account_info}))
    
