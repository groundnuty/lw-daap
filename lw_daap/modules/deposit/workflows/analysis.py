
from __future__ import absolute_import


from .upload import upload

from lw_daap.modules.deposit.forms import AnalysisForm, \
    AnalysisEditForm

class analysis(upload):
    draft_definitions = {
        '_default': AnalysisForm,
        '_edit': AnalysisEditForm,
    }
