#############################################################################
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
###############################################################################
#==============================================================================
#

import os.path, os
import sys
import logging

#
#==============================================================================
#
#############################
## -- Init Env Configs --  ##
#############################
#
DEMO_STRING="Development Demo"
PYTHONPATH= ""

REMOVE_OLD_PROCESSES= True
CONFIRM_REGISTRATION = True

## Base Dirs Defined
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_URLCONF = 'dam.urls'

from config import *
INSTALLATIONPATH = os.path.join(os.getenv('HOME'), ".dam")
BACKUP_PATH = os.path.join(INSTALLATIONPATH, 'file_backup')
THUMBS_DIR = os.path.join(INSTALLATIONPATH, 'thumbs')
dir_log = os.path.join(INSTALLATIONPATH, 'log')

try:
    os.makedirs(BACKUP_PATH, 16877)
except:
    pass

try:
    os.makedirs(THUMBS_DIR, 16877)
except:
    pass

#########
## Append Defined Dirs to sys.path
#########
sys.path.append(PYTHONPATH)
sys.path.append(ROOT_PATH)
sys.path.append(os.path.dirname(__file__))
sys.path.append(INSTALLATIONPATH)

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
# All hosts allowed
# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['*']

SERVER_PUBLIC_ADDRESS = '127.0.0.1:10000'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('johnb', 'john.bragato@gmail.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True


#
#==============================================================================
#
###########################
## -- Installed Apps  -- ##
###########################
#

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.admin',
	'dam.core.dam_repository',
    'dam.scripts',
	'dam.repository',
	'dam.treeview',
	'dam.core.dam_metadata',
	'dam.metadata',
	'dam.variants',
	'dam.preferences',
	'dam.core.dam_workspace',
	'dam.workspace',
	'dam.application',
	'dam.api',
	'dam.workflow',
	'dam.eventmanager',
	'dam.geo_features',
	'dam.basket',
	'dam.upload',
	'dam.appearance',
    'dam.mprocessor',
    'dam.kb',
    'south',
	'debug_toolbar',
)

#
#==============================================================================
#
############################
## -- Database Configs -- ##
############################
#
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dam_db',
        'USER': 'root',
        'PASSWORD': 'mysql',
        # 'HOST': '127.0.0.1',
        # 'PORT': '3301',
        #'OPTIONS': {
        #    'init_command': 'SET storage_engine=InnoDB',
        #    'charset' : 'utf8',
        #    'use_unicode' : True,
        #},
        #'TEST_CHARSET': 'utf8',
        #'TEST_COLLATION': 'utf8_general_ci',
    },
    # 'slave': {
    #     ...
    # },
}

#if DATABASES['default']['ENGINE'] == 'sqlite3':
#    DATABASES['default']['NAME'] = os.path.join(ROOT_PATH,  DATABASE_NAME)

#DATABASE_HOST = ''	         # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''	         # Set to empty string for default. Not used with sqlite3.

#
#==============================================================================
#
#==============================================================================
##                -- Static And Media file/dir Configs/Def --                ##
#==============================================================================
#
##########################
## -- Static Configs -- ##
##########################
#
##########################
# STATIC_ROOT= os.path.join(ROOT_PATH, 'var','static')
# if os.path.isdir(STATIC_ROOT):
#     pass
# else:
#     os.makedirs(STATIC_ROOT, mode=0777)

STATIC_ROOT = os.path.abspath(os.path.join(ROOT_PATH, 'files'))
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    STATIC_ROOT,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

#==============================================================================
#
#########################
## -- Media Configs -- ##
#########################
#
##########################
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

MEDIA_ROOT = os.path.join(ROOT_PATH, 'var','media')
if os.path.isdir(MEDIA_ROOT):
    pass
else:
    os.makedirs(MEDIA_ROOT, mode=0777)

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

#==============================================================================
#
#########################
# -- Storage Configs -- #
#########################
from dam.mprocessor.config import Configurator
c = Configurator()
MPROCESSOR_STORAGE = c.get('STORAGE', 'cache_dir')
STORAGE_SERVER_URL= '/storage/'

#
#############################
# -- File Upload Configs -- #
#############################
FILE_UPLOAD_TEMP_DIR = '/var/notredam'
#FILE_UPLOAD_TEMP_DIR = '/tmp'
FILE_UPLOAD_MAX_MEMORY_SIZE = 157286400
FILE_UPLOAD_PERMISSIONS = 0664

###############################
#### Storage/Cache Services ###
###############################

# Enable these options for memcached
CACHE_BACKEND= "memcached://127.0.0.1:11211/"
CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True

# Set this to true if you use a proxy that sets X-Forwarded-Host
USE_X_FORWARDED_HOST = True

#AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
#AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
#AWS_STORAGE_BUCKET_NAME = '<YOUR BUCKET NAME>'

#STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

#
##################################################
##################################################
##################################################
#
#==============================================================================
# Secrets and Login Keys #
#==============================================================================
#
#  Make this unique, and don't share it with anybody.
SECRET_KEY = '8w+8&332v83)459&4X124cvb(3w=2mz*%af&ele832zf=g@_7+'
CAPTCHA_PRIVATE_KEY = '6LeIrcMSAAAAAF_F3yhg0AyO65M5bpj4Kb4OW9tC'

##############################################
#
#==============================================================================
##  --  Templates  --  ##
#==============================================================================
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)


TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.join(ROOT_PATH, 'templates'),
)

##################################################
#
# List of callables that know how to import templates from various sources.
#TEMPLATE_LOADERS = (
#	'django.template.loaders.filesystem.load_template_source',
#	'django.template.loaders.app_directories.load_template_source',
#	 'django.template.loaders.eggs.load_template_source',
#)

if DEBUG:
    TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',      
    ]
else:
    TEMPLATE_LOADERS = [
        ('django.template.loaders.cached.Loader',(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
            )),
    ]


#==============================================================================
## --  Middleware & Hashers--  ##
#==============================================================================
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    
)

# Place bcrypt first in the list, so it will be the default password hashing
# mechanism
# PASSWORD_HASHERS = (
#     'django.contrib.auth.hashers.BCryptPasswordHasher',
#     'django.contrib.auth.hashers.PBKDF2PasswordHasher',
#     'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
#     'django.contrib.auth.hashers.SHA1PasswordHasher',
#     'django.contrib.auth.hashers.MD5PasswordHasher',
#     'django.contrib.auth.hashers.CryptPasswordHasher',
# )

#==============================================================================
#
######################
## --  Sessions  -- ##
######################
#
#
# By default, be at least somewhat secure with our session cookies.
SESSION_COOKIE_HTTPONLY = True

# Set this to true if you are using https
SESSION_COOKIE_SECURE = False

# SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

#==============================================================================
#
#########################
##  -- LDAP Configs -- ##
#########################
#
#### UNCOMMENT TO USE LDAP AUTHENTICATION. NOTE THAT IT NEEDS ldap PACKAGE INSTALLED
#AUTHENTICATION_BACKENDS = (
#    'django_auth_ldap.backend.LDAPBackend',
#    'django.contrib.auth.backends.ModelBackend',    
#  
#)

#import ldap
#from django_auth_ldap.config import LDAPSearch
#
#AUTH_LDAP_SERVER_URI = "ldap://ldapcluster.relic7.org"
#AUTH_LDAP_BIND_PASSWORD = ""
#AUTH_LDAP_USER_SEARCH = LDAPSearch("dc=crs4",ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
#AUTH_LDAP_USER_ATTR_MAP = {
#    "first_name": "givenName",
#    "last_name": "sn",
#    "email": "mail"
#}

#==============================================================================
#
#########################
## -- Email Configs -- ##
#########################
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'john.bragato@gmail.com'
# EMAIL_FILE_PATH =
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '993'
EMAIL_HOST_USER = 'john.bragato@gmail.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_SENDER = "john.bragato@bluefly.com"

#==============================================================================
#
###################
## -- Logging -- ##
###################
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)-8s %(pathname)s %(lineno)s %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file':{
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(dir_log,  'dam.log')

        
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            #'filters': ['special']
        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'dam': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'INFO',
            #'filters': ['special']
        }
    }
}

#==============================================================================
#                      Third party app settings
#==============================================================================
# List of callables that know how to import templates from various sources.
#==============================================================================
#
#################################
## -- DEBUG TOOLBAR CONFIGS -- ##
#################################
#
def custom_show_toolbar(request):
    """ Only show the debug toolbar to users with the superuser flag. """
    return request.user.is_superuser

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'HIDE_DJANGO_SQL': False,
    'TAG': 'body',
    'SHOW_TEMPLATE_CONTEXT': True,
    'ENABLE_STACKTRACES': True,
}
#
# DEBUG_TOOLBAR_PANELS = (
#     #'debug_toolbar_user_panel.panels.UserPanel',
#     'debug_toolbar.panels.version.VersionDebugPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     #'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
#     'debug_toolbar.panels.headers.HeaderDebugPanel',
#     'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
#     'debug_toolbar.panels.template.TemplateDebugPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.signals.SignalDebugPanel',
#     #'debug_toolbar.panels.logger.LoggingPanel',
#
# )

#
#==============================================================================
#
#################################
## -- ADMIN_TOOLS CONFIGS -- ##
#################################
## Customize Admin interface with Admin Tools
#ADMIN_TOOLS_MENU = 'menu.CustomMenu'
#ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
## ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'
ADMIN_TOOLS_THEMING_CSS = 'css/theming.css'

#==============================================================================
#  Celery settings
#==============================================================================
# import djcelery
# celery.setup loader()
# BROKER_URL = "django://"
# Uncomment these to activate and customize Celery:
# CELERY_ALWAYS_EAGER = False  # required to activate celeryd
# BROKER_HOST = 'localhost'
# BROKER_PORT = 5672
# BROKER_USER = 'django'
# BROKER_PASSWORD = 'django'
# BROKER_VHOST = 'django'
# CELERY_RESULT_BACKEND = 'amqp'
#
#==============================================================================
# REST FRAMEWORK SETTINGS tastypie and django_restframework
#==============================================================================
TASTYPIE_DEFAULT_FORMATS = ['json']

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': 20
}

#==============================================================================
## Others Misc
#==============================================================================
CRISPY_TEMPLATE_PACK = 'bootstrap3'

#==============================================================================
### AUTOCOMPLETE django-ajax-selects
#==============================================================================
# define the lookup channels in use on the site
# AJAX_LOOKUP_CHANNELS = {
#     #  simple: search Person.objects.filter(name__icontains=q)
#     'person'  : {'model': 'example.person', 'search_field': 'name'},
#     # define a custom lookup channel
#     'song'   : ('example.lookups', 'SongLookup')
# }


#==============================================================================
#############################################
#######           Extraneous          #######
#############################################
#==============================================================================
# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
# from django.core.exceptions import ImproperlyConfigured
#
#
# def get_env_setting(setting):
#     """ Get the environment setting or return exception """
#     try:
#         return os.environ[setting]
#     except KeyError:
#         error_msg = "Set the %s env variable" % setting
#         raise ImproperlyConfigured(error_msg)


# Specify a custom user model to use
#AUTH_USER_MODEL = 'accounts.djdamUser'
# SECURITY WARNING: keep the secret key used in production secret!
# Hardcoded values can leak through source control.
# This is an example method of getting the value from an environment setting.
# Uncomment to use, and then make sure you set the SECRET_KEY environment variable.
# This is good to use in production, and on services that support it such as Heroku.
#SECRET_KEY = get_env_setting('SECRET_KEY')

#==============================================================================
##################################################
#######                End                 #######
##################################################
#==============================================================================