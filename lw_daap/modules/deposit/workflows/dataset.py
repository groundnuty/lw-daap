
from __future__ import absolute_import


from .upload import upload

from lw_daap.modules.deposit.forms import DatasetForm, \
    DatasetEditForm, FilesForm

class dataset(upload):
    draft_definitions = {
        'metadata': DatasetForm,
        'edit': DatasetEditForm,
        'files': FilesForm,
    }
