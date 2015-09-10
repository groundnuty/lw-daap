
from wtforms import validators, widgets

from invenio.base.i18n import _
from lw_daap.modules.invenio_deposit.form import WebDepositForm
from lw_daap.modules.invenio_deposit.fields import Date
from lw_daap.modules.deposit.field_widgets import date_widget


__all__ = ['PeriodField']

class PeriodFieldForm(WebDepositForm):
    start = Date(
        label=_('Start date'),
        description='Start date.',
        widget=date_widget,
        widget_classes='',
        )
    end = Date(
        label=_('End date'),
        description='End date.',
        widget=date_widget,
        widget_classes='',
        )

