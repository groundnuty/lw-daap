
from __future__ import absolute_import


from .upload import upload

from lw_daap.modules.deposit.forms import AnalysisForm, \
    AnalysisEditForm, AnalysisFilesForm

class analysis(upload):
    draft_definitions = {
        '_metadata': AnalysisForm,
        '_edit': AnalysisEditForm,
        '_files': AnalysisFilesForm,
    }
