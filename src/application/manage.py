#!/usr/bin/python
# from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)


#if __name__ == "__main__":
#    execute_manager(settings)

if __name__ == "__main__":
    import os, sys, settings
    sys.path.append(os.path.dirname(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dam.settings")
    os.environ['DJANGO_SETTINGS_MODULE'] = 'dam.settings'

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
