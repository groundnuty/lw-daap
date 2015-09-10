
from wtforms import validators, widgets

from invenio.base.i18n import _
from lw_daap.modules.invenio_deposit.form import WebDepositForm


__all__ = ['SpatialField']

class SpatialFieldForm(WebDepositForm):
    west = Date(
        label=_('Start date'),
        description='Start date.', 
        widget=date_widget,
        widget_classes='input-sm',
        )
    end = Date(
        label=_('End date'),
        description='End date.',
        widget=date_widget,
        widget_classes='input-sm',
        )

