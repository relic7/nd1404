#########################################################################
#
# NotreDAM, Copyright (C) 2012, Sardegna Ricerche.
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
#
# WSGI script for NotreDAM
#
# Author: Alceste Scalas <alceste@crs4.it>
#
#########################################################################

import os
import sys

# Redirect standard output to standard error
# FIXME: mostly necessary for dealing with 'print's scattered in the code base
sys.stdout = sys.stderr
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__)), 'dam')
sys.path.append(os.path.join(os.path.dirname(__file__)), 'application')

(parent_dir, _tail) = os.path.split(os.path.dirname(__file__))
sys.path.append(parent_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'dam.settings'
print 'WSGI OS ENVIRON'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
