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


from wtforms import validators
from datetime import date

from invenio.base.i18n import _
from lw_daap.modules.invenio_deposit.form import WebDepositForm
from lw_daap.modules.invenio_deposit.fields import Date
from lw_daap.modules.invenio_deposit.field_widgets import ColumnInput
from lw_daap.modules.deposit.field_widgets import date_widget
from lw_daap.modules.invenio_deposit.validation_utils import required_if
from lw_daap.modules.deposit.validation_utils import StartEndDate


__all__ = ['PeriodField']


class PeriodFieldForm(WebDepositForm):
    start = Date(
        label=_('Start date'),
        description='Start date.',
        validators=[
            required_if(
                'end',
                [lambda x: x is not None, ],  # non-empty
                message="Start date required if you specify an end date."
            ),
            validators.optional(),
            StartEndDate(
                max_from='end',
                message='%(field_label)s must be previous to end date.'),
        ],
        widget=ColumnInput(date_widget, class_="col-xs-3"),
        widget_classes='',
    )
    end = Date(
        label=_('End date'),
        description='End date.',
        validators=[
            required_if(
                'start',
                [lambda x: x is not None, ],  # non-empty
                message="End date required if you specify a start date."
            ),
            validators.optional(),
            StartEndDate(max=date.today(), min_from='start',
                         message=('%(field_label)s must be between start'
                                  ' date and today.')),
        ],
        widget=ColumnInput(date_widget, class_="col-xs-3"),
        widget_classes='',
    )
