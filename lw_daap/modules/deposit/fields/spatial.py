
from wtforms import validators, widgets

from invenio.base.i18n import _
from lw_daap.modules.invenio_deposit.form import WebDepositForm
from lw_daap.modules.invenio_deposit import fields
from lw_daap.modules.invenio_deposit.field_widgets import ColumnInput
from lw_daap.modules.invenio_deposit.validation_utils import required_if


__all__ = ['SpatialField']

class SpatialFieldForm(WebDepositForm):
    #Coordinates--westernmost longitude
    west = fields.StringField(
        label="Western most longitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            required_if(
                'north',
                [lambda x: x is not None, ],  # non-empty
                message="All coordinates required if you specify one."
            ),
            validators.optional(),
            validators.Length(11, message="Field must be 11 characters long."),
            validators.Regexp(regex=r'([+-])(\d{3})([.])(\d{6})', message="The coordinates must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros.")
            #validators.Regexp(regex=r'([WENS])(\d{3})(\d{2})(\d{2})', message="Field must be introduced in the form hdddmmss (hemisphere-degrees-minutes-seconds). The subelements are each right justified and unused positions contain zeros.")
        ],
    )
    #Coordinates--easternmost longitude
    east = fields.StringField(
        label="Eastern most longitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            required_if(
                'south',
                [lambda x: x is not None, ],  # non-empty
                message="All coordinates required if you specify one."
            ),
            validators.optional(),
            validators.Length(11, message="Field must be 11 characters long."),
            validators.Regexp(regex=r'([+-])(\d{3})[.](\d{6})', message="The coordinates must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros.")
        ],
    )
    #Coordinates--northernmost latitude
    north = fields.StringField(
        label="Northern most latitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            required_if(
                'east',
                [lambda x: x is not None, ],  # non-empty
                message="All coordinates required if you specify one."
            ),
            validators.optional(),
            validators.Length(11, message="Field must be 11 characters long."),
            validators.Regexp(regex=r'([+-])(\d{3})[.](\d{6})', message="The coordinates must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros.")
        ],
    )
    #Coordinates--southernmost latitude
    south = fields.StringField(
        label="Southern most latitude",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-2"),
        validators=[
            required_if(
                'west',
                [lambda x: x is not None, ],  # non-empty
                message="All coordinates required if you specify one."
            ),
            validators.optional(),
            validators.Length(11, message="Field must be 11 characters long."),
            validators.Regexp(regex=r'([+-])(\d{3})[.](\d{6})', message="The coordinates must be recorded in decimal degrees (+ddd.dddddd). Unused positions must be filled with zeros.")
        ],
    )
