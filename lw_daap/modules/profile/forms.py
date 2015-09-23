from __future__ import absolute_import, print_function, unicode_literals

from invenio.base.i18n import _
from invenio.utils.forms import InvenioBaseForm

from wtforms_alchemy import ClassMap, model_form_factory
from .models import userProfile

ModelForm = model_form_factory(InvenioBaseForm)

class ProfileForm(ModelForm):
  class Meta:
    model = userProfile
