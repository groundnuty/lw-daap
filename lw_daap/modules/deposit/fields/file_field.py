from wtforms import FileField as wFileField 
from invenio.modules.deposit.field_base import WebDepositField

__all__ = ['FileField']


class FileField(WebDepositField, wFileField):
    def __init__(self, **kwargs):
        defaults = dict(icon='upload', export_key=False)
        defaults.update(kwargs)
        super(FileField, self).__init__(**kwargs)
