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

import os.path, os
import sys
import logging



DEMO_STRING="Development Demo" 
PYTHONPATH= ""
CAPTCHA_PRIVATE_KEY = '6LeIrcMSAAAAAF_F3yhg0AyO65M5bpj4Kb4OW9tC'

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

sys.path.append(PYTHONPATH)
sys.path.append(ROOT_PATH)
sys.path.append(os.path.dirname(__file__))

REMOVE_OLD_PROCESSES= True
CONFIRM_REGISTRATION = True
from mprocessor.config import Configurator
c = Configurator()
MPROCESSOR_STORAGE = c.get('STORAGE', 'cache_dir')
STORAGE_SERVER_URL= '/storage/'


INSTALLATIONPATH = os.path.join(os.getenv('HOME'), ".dam"  )
BACKUP_PATH = os.path.join(INSTALLATIONPATH, 'file_backup')
sys.path.append(INSTALLATIONPATH)

THUMBS_DIR = os.path.join(INSTALLATIONPATH,  'thumbs')

from config import *
dir_log = os.path.join(INSTALLATIONPATH, 'log')



# Database
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



CAPTCHA_PRIVATE_KEY = '6LeIrcMSAAAAAF_F3yhg0AyO65M5bpj4Kb4OW9tC'
EMAIL_HOST = "mail.google.com"
EMAIL_SENDER = "john.bragato@bluefly.com"
SERVER_PUBLIC_ADDRESS = '127.0.0.1:10000'

DEMO_STRING="Development Demo" 

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('johnb', 'john.bragato@gmail.com'),
)

MANAGERS = ADMINS


#DATABASE_HOST = ''	         # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''	         # Set to empty string for default. Not used with sqlite3.

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

STATIC_ROOT = os.path.join(ROOT_PATH, 'files')
STATIC_URL = '/static/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8w+8&332v83)459&4X124cvb(3w=2mz*%af&ele832zf=g@_7+'

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


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
     'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    
)

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

#### DECOMMENT TO USE LDAP AUTHENTICATION. NOTE THAT IT NEEDS ldap PACKAGE INSTALLED
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



ROOT_URLCONF = 'dam.urls'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.join(ROOT_PATH, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request"
)

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
