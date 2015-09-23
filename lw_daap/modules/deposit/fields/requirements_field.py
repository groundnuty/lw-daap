# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2012, 2013 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public Requirements as published by
# the Free Software Foundation, either version 3 of the Requirements, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public Requirements for more details.
#
# You should have received a copy of the GNU General Public Requirements
# along with Zenodo. If not, see <http://www.gnu.org/license/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Requirements field."""

import json
from operator import itemgetter

from wtforms import SelectField

from lw_daap.modules.invenio_deposit.field_base import WebDepositField
from lw_daap.modules.invenio_deposit.processor_utils import set_flag
from invenio.modules.knowledge.api import get_kb_mappings

__all__ = ['RequirementsField']


def _kb_requirements_choices(domain_flavor=True, domain_os=True):
    def _mapper(x):
        requirements = json.loads(x['value'])
        if (requirements.get('domain_flavor', False) and domain_flavor) or \
                (requirements.get('domain_os', False) and domain_os):
            return (x['key'], requirements['title'])
        else:
            return None
    return sorted(
        filter(lambda x: x is not None,
               map(_mapper, get_kb_mappings('requirements', '', ''))),
        key=itemgetter(1),
    )


class RequirementsField(WebDepositField, SelectField):

    """Requirements field."""

    def __init__(self, **kwargs):
        """Initialize requirements field."""
        kwargs.setdefault("icon", "icon-laptop")

        if 'choices' not in kwargs:
            requirements_filter = {}
            for opt in ['domain_flavor', 'domain_os']:
                if opt in kwargs:
                    requirements_filter[opt] = kwargs[opt]
                    del kwargs[opt]
            kwargs['choices'] = _kb_requirements_choices(**requirements_filter)
        kwargs['processors'] = [set_flag('touched'), ]
        super(RequirementsField, self).__init__(**kwargs)
