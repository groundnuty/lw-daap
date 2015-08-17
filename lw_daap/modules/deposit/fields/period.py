
from invenio.modules.deposit.fields.wtformsext import FormField
from wtforms import Form, validators

from invenio.base.i18n import _
from invenio.modules.deposit.fields import Date 
from invenio.modules.deposit.field_widgets import date_widget

__all__ = ['PeriodField']

class PeriodFieldForm(Form):
    start = Date(
        label=_('Start date'),
        icon='fa fa-calendar fa-fw',
        validators=[validators.DataRequired()],
        widget=date_widget,
        widget_classes='input-sm',
        )
    end = Date(
        label=_('End date'),
        icon='fa fa-calendar fa-fw',
        validators=[validators.DataRequired()],
        widget=date_widget,
        widget_classes='input-sm',
        )

class PeriodField(FormField):
    form_class = PeriodFieldForm
