# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.


from wtforms import validators, widgets

from invenio.base.i18n import _
from lw_daap.modules.invenio_deposit.form import WebDepositForm
from lw_daap.modules.invenio_deposit import fields
from lw_daap.modules.invenio_deposit.field_widgets import ColumnInput
from lw_daap.modules.invenio_deposit.validation_utils import required_if


__all__ = ['SpatialField']

class SpatialFieldForm(WebDepositForm):
    #Coordinates--westernmost longitude
    west = fields.StringField(
        label="Western most longitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            required_if(
                'east',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="All coordinates required if you specify one."
            ),
            validators.optional(),
            #validators.Length(11, message="The coordinates must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros."),
            validators.Regexp(regex=r'([+-])(\d{3})([.])(\d{6})', message="The coordinates (Western most longitude) must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros.")
        ],
    )
    #Coordinates--easternmost longitude
    east = fields.StringField(
        label="Eastern most longitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            required_if(
                'south',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="All coordinates required if you specify one."
            ),
            validators.optional(),
            #validators.Length(11, message="The coordinates must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros."),
            validators.Regexp(regex=r'([+-])(\d{3})[.](\d{6})', message="The coordinates (Eastern most longitude) must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros.")
        ],
    )
    #Coordinates--northernmost latitude
    north = fields.StringField(
        label="Northern most latitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            required_if(
                'east',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="All coordinates required if you specify one."
            ),
            validators.optional(),
            #validators.Length(11, message="The coordinates must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros."),
            validators.Regexp(regex=r'([+-])(\d{3})[.](\d{6})', message="The coordinates (Northern most latitude) must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros.")
        ],
    )
    #Coordinates--southernmost latitude
    south = fields.StringField(
        label="Southern most latitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            required_if(
                'west',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="All coordinates required if you specify one."
            ),
            validators.optional(),
            #validators.Length(11, message="The coordinates must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros."),
            validators.Regexp(regex=r'([+-])(\d{3})[.](\d{6})', message="The coordinates (Southern most latitude) must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros.")
        ],
    )
