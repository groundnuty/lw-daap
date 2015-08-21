
from wtforms import validators, widgets

from invenio.base.i18n import _
from invenio.modules.deposit.form import WebDepositForm
from invenio.modules.deposit.fields import Date
from invenio.modules.deposit.field_widgets import date_widget


__all__ = ['PeriodField']

class PeriodFieldForm(WebDepositForm):
    start = Date(
        label=_('Start date'),
        description='Start date.', 
        #validators=[validators.DataRequired()],
        widget=date_widget,
        widget_classes='input-sm',
        )
    end = Date(
        label=_('End date'),
        description='End date.',
        #validators=[validators.DataRequired()],
        widget=date_widget,
        widget_classes='input-sm',
        )

