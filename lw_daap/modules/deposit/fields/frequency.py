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


from wtforms import IntegerField
from wtforms import validators, widgets

from invenio.base.i18n import _
from lw_daap.modules.invenio_deposit.form import WebDepositForm
from lw_daap.modules.invenio_deposit import fields
from lw_daap.modules.invenio_deposit.field_widgets import ColumnInput
from lw_daap.modules.invenio_deposit.validation_utils import required_if


__all__ = ['FrequencyField']

class FrequencyFieldForm(WebDepositForm):
    size = fields.IntegerField(
        label="",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            validators.optional(),
        ],
    )

    unit = fields.SelectField(
        label="",
        choices=[
            ('year', 'year'),
            ('month', 'month'),
            ('day', 'day'),
            ('hour', 'hour'),
            ('minute', 'minute'),
        ],
        default='year',
        widget_classes='form-control',
        widget=ColumnInput(
            class_="col-xs-2 col-pad-0", widget=widgets.Select()
        ),
        validators=[
            required_if(
                'size',
                [lambda x: bool(x), ],  # non-empty
                message="Field required if you specify a value."
            ),
        ],
    )
