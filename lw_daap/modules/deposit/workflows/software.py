
from __future__ import absolute_import


from .upload import upload

from lw_daap.modules.deposit.forms import SoftwareForm, \
    SoftwareEditForm, FilesForm

class software(upload):
    draft_definitions = {
        'metadata': SoftwareForm,
        'edit': SoftwareEditForm,
        'files': FilesForm,
    }
