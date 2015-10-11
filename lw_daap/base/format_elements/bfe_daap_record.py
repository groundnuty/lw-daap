# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2012, 2013 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from flask import url_for
from invenio.modules.records.api import get_record


def format_element(bfo, rec_id={}):
    try:
        rec_id = int(rec_id.get('record_id'))
        r = get_record(rec_id)
        d = dict(
            title=r['title'],
            link=url_for('record.metadata', recid=rec_id)
        )
    except ValueError:
        # doi ?
        d = dict(
            title=rec_id.get('record_id'),
            link='http://doi.org/' + rec_id.get('record_id')
        )
    except TypeError:
        return ''
    
    return '<a href="%(link)s">%(title)s</a>' % d


def escape_values(bfo):
    return 0

