
from wtforms import validators, widgets

from invenio.base.i18n import _
from lw_daap.modules.invenio_deposit.form import WebDepositForm
from lw_daap.modules.invenio_deposit import fields
from lw_daap.modules.invenio_deposit.field_widgets import ColumnInput


__all__ = ['SpatialField']

class SpatialFieldForm(WebDepositForm):
    #Coordinates--westernmost longitude
    west = fields.StringField(
        label="Western most longitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            validators.optional(),
        ],
    )
    #Coordinates--easternmost longitude
    east = fields.StringField(
        label="Eastern most longitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            validators.optional(),
        ],
    )
    #Coordinates--northernmost latitude
    north = fields.StringField(
        label="Northern most latitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            validators.optional(),
        ],
    )
    #Coordinates--southernmost latitude
    south = fields.StringField(
        label="Southern most latitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            validators.optional(),
        ],
    )
