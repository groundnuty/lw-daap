
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
