
from __future__ import absolute_import


from .upload import upload

from lw_daap.modules.deposit.forms import SoftwareForm, \
    BasicEditForm

class software(upload):
    draft_definitions = {
        '_default': SoftwareForm,
        '_edit': BasicEditForm,
    }
