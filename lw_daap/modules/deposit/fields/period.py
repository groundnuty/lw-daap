
from wtforms import validators, widgets

from invenio.base.i18n import _
from lw_daap.modules.invenio_deposit.form import WebDepositForm
from lw_daap.modules.invenio_deposit.fields import Date
from lw_daap.modules.invenio_deposit.field_widgets import ColumnInput
from lw_daap.modules.deposit.field_widgets import date_widget
from lw_daap.modules.invenio_deposit.validation_utils import required_if

from flask import current_app

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
        ],
        widget=ColumnInput(date_widget, class_="col-xs-3"),
        widget_classes='',
        )



