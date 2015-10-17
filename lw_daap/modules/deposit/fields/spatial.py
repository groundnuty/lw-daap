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
from wtforms.validators import StopValidation, ValidationError

from invenio.base.i18n import _
from lw_daap.modules.invenio_deposit.form import WebDepositForm
from lw_daap.modules.invenio_deposit import fields
from lw_daap.modules.invenio_deposit.field_widgets import ColumnInput
from lw_daap.modules.invenio_deposit.validation_utils import required_if


__all__ = ['SpatialField']


def coord_validator(coord):
    return validators.Regexp(
        regex=r'([+-])(\d{3})([.])(\d{6})',
        message=('%s must be recorded in decimal degrees (+/-ddd.dddddd). '
                 'Unused positions must be filled with zeros.' %coord)
    )


class SpatialFieldForm(WebDepositForm):
    #Coordinates--westernmost longitude
    west = fields.FloatField(
        label="Western most longitude",
        placeholder="West",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            validators.optional(),
            #coord_validator('Western most longitude'),
            validators.NumberRange(min=-180, max=180, message="The western most longitude values are bounded by +/-180 degrees.")
        ],
    )
    #Coordinates--easternmost longitude
    east = fields.FloatField(
        label="Eastern most longitude",
        placeholder="East",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            validators.optional(),
            #coord_validator('Eastern most longitude'),
            validators.NumberRange(min=-180, max=180, message="The eastern most longitude values are bounded by +/-180 degrees.")
        ],
    )
    #Coordinates--northernmost latitude
    north = fields.FloatField(
        label="Northern most latitude",
        placeholder="North",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            validators.optional(),
            #coord_validator('Northern most latitude'),
            validators.NumberRange(min=-90, max=90, message="The northern most latitude values are bounded by +/-90 degrees.")
        ],
    )
    #Coordinates--southernmost latitude
    south = fields.FloatField(
        label="Southern most latitude",
        placeholder="South",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            validators.optional(),
            #coord_validator('Southern most latitude'),
            validators.NumberRange(min=-90, max=90, message="The southern most latitude values are bounded by +/-90 degrees.")
        ],
    )

    def validate(self, **kwargs):
        r = super(SpatialFieldForm, self).validate(**kwargs)
        fields = [f for f in self] 
        if any(bool(f.data is not None) for f in fields):
            if not all(bool(f.data is not None) for f in fields):
                err = self.errors.get('south', [])
                err.append('All coordinates must be filled.')
                self.errors['south'] = err
                return False
        return r

