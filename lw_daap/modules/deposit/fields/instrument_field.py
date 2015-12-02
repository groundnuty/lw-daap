# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.

# This file is part of Zenodo.
# Copyright (C) 2012, 2013 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Instrument field."""

import json
from operator import itemgetter

from wtforms import SelectField

from lw_daap.modules.invenio_deposit.field_base import WebDepositField
from lw_daap.modules.invenio_deposit.processor_utils import set_flag
from invenio.modules.knowledge.api import get_kb_mappings
from lw_daap.modules.instrument.service_utils import getAllInstruments
from flask import current_app

__all__ = ['InstrumentField']

class InstrumentField(WebDepositField, SelectField):

    """Instrument field."""

    def __init__(self, **kwargs):
        """Initialize instrument field."""
        kwargs.setdefault("icon", "icon-certificate")

        if 'choices' not in kwargs:
            instruments = getAllInstruments()
            instruments_json = json.loads(instruments)
            for instrument in instruments_json:
                inst_choice = [(instrument['idInstrument'], instrument['name'])]
                kwargs['choices'].append(inst_choice)
        kwargs['processors'] = [set_flag('touched'), ]
        super(InstrumentField, self).__init__(**kwargs)
