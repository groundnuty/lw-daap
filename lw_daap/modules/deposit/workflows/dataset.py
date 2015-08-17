
from __future__ import absolute_import


from .upload import upload

from lw_daap.modules.deposit.forms import ZenodoForm, \
    ZenodoEditForm

class dataset(upload):
    draft_definitions = {
        '_default': ZenodoForm,
        '_edit': ZenodoEditForm,
    }
