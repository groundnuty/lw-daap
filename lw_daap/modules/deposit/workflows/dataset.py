
from __future__ import absolute_import


from .upload import upload

from lw_daap.modules.deposit.forms import DatasetForm, \
    BasicEditForm

class dataset(upload):
    draft_definitions = {
        '_default': DatasetForm,
        '_edit': BasicEditForm,
    }
