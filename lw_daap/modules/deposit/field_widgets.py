# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2012, 2013, 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Implement custom field widgets."""

from wtforms.widgets import HTMLString, html_params

#from lw_daap.modules.invenio_deposit.field_widgets import PLUploadWidget

def date_widget(field, **kwargs):
    """Date picker widget that allows to specify the date format to use.
       Default is YYYY-MM-DD"""
    field_id = kwargs.pop('id', field.id)
    date_format = kwargs.pop('date_format','YYYY-MM-DD')
    html = [u'<div class="col-xs-5 col-sm-3">'
                    '<div class="form-group">'
                        '<div class="input-group datepicker">'
                            '<input class="form-control" %s data-date-format="%s" type="text">'
                            '<span class="input-group-addon">'
                                '<span class="glyphicon glyphicon-calendar"></span>'
                            '</span>'
                        '</div>'
                     '</div>'
                '</div>'
            % (html_params(id=field_id, name=field_id, value=field.data or ''),
               date_format)]
    open("/home/lwdaap/DEBUG", "a+").write(u''.join(html) + '\n')
    return HTMLString(u''.join(html))
