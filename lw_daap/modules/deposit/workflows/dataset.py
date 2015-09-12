
from __future__ import absolute_import


from .upload import upload

from lw_daap.modules.deposit.forms import DatasetForm, \
    DatasetEditForm, FilesForm

class dataset(upload):
    draft_definitions = {
        '_metadata': DatasetForm,
        '_edit': DatasetEditForm,
        '_files': FilesForm,
    }
