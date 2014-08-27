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

from django.conf.urls import *

urlpatterns = patterns('',

    (r'^demo_registration/$','dam.demo_registration.views.registration'),
    (r'^confirm_user/$','dam.demo_registration.views.confirm_user'),
    (r'^demo_admin/get_user_list/$', 'dam.demo_registration.views.get_user_list'),
    (r'^demo_admin/confirm_user/$', 'dam.demo_registration.views.confirm_user'),
    (r'^demo_admin/disable_user/$', 'dam.demo_registration.views.disable_user'),
    (r'^demo_admin/$', 'dam.demo_registration.views.demo_admin'),

)
