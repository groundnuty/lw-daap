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
from lw_daap.modules.instruments.service_utils import getAllInstruments
from lw_daap.modules.instruments.service_utils import getInstrument
from lw_daap.modules.instruments.service_utils import getUsergroupByIdInstrument
from datetime import datetime
from werkzeug import MultiDict
from flask import current_app

__all__ = ['InstrumentField']

def instrument_processor(form, field, submit=False, fields=None):
    form.embargo_date.flags.hidden = True
    form.embargo_date.flags.disabled = True
    form.license.flags.hidden = True
    form.license.flags.disabled = True
    form.access_conditions.flags.hidden = True
    form.access_conditions.flags.disabled = True
    form.access_groups.flags.hidden = True
    form.access_groups.flags.disabled = True
    form.access_right.flags.hidden = True
    form.access_right.flags.disabled = True

    if field.data != '-1':
        selected = getInstrument(field.data)
        instrument = json.loads(selected)
        accessRight = str(instrument['accessRight'])
        license = str(instrument['license'])
        embargoDate = str(instrument['embargoDate'])
        conditions = str(instrument['conditions'])
        groups = getUsergroupByIdInstrument(field.data)
        groups_json = json.loads(groups)
        d = MultiDict()
        for group in groups_json:
            info = {
               u'identifier': unicode(str(group['idGroup'])),
               u'title': group['name'],
            }
            d.add(unicode('access_groups'),info)
        #current_app.logger.debug(d)
        form.access_groups.process(d)
        #MultiDict([(unicode('access_groups'),info)])
        form.license.data = license
        form.access_conditions.data = conditions
        if embargoDate is not None and str(embargoDate) != 'None':
            form.embargo_date.data = datetime.fromtimestamp(float(embargoDate)/1000.0).strftime('%Y-%m-%d')
        if accessRight == 'embargoed':
            form.embargo_date.flags.hidden = False
            form.embargo_date.flags.disabled = False

        if accessRight == 'restricted':
            form.access_conditions.flags.hidden = False
            form.access_conditions.flags.disabled = False
            form.access_groups.flags.hidden = False
            form.access_groups.flags.disabled = False

        if accessRight in ['open', 'embargoed']:
            form.license.flags.hidden = False
            form.license.flags.disabled = False
        form.access_right.data = unicode(accessRight)
    else:
        form.access_right.data = 'open'
        form.access_conditions.data = ''
        form.license.flags.hidden = False
        form.license.flags.disabled = False
    form.access_right.flags.hidden = False
    form.access_right.flags.disabled = False


class InstrumentField(WebDepositField, SelectField):

    """Instrument field."""

    def __init__(self, **kwargs):
        """Initialize instruments field."""
        kwargs.setdefault("icon", "icon-certificate")

        if 'choices' not in kwargs:
            #current_app.logger.debug('Obtengo los instrumentos')
            instruments = getAllInstruments()
            #current_app.logger.debug('Hecho')
            instruments_json = json.loads(instruments)
            #current_app.logger.debug('Cargo json')
            #current_app.logger.debug(instruments_json)
            choices = [("-1", 'Select an instruments')]
            for instrument in instruments_json:
                choices.append((str(instrument['idInstrument']), str(instrument['name'])))

            kwargs['choices'] = choices
        kwargs['processors'] = [set_flag('touched'),instrument_processor, ]
        super(InstrumentField, self).__init__(**kwargs)
