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

from flask import url_for
from invenio.modules.records.api import get_record


def format_element(bfo, rec_id=''):
    try:
        rec_id = int(rec_id)
        r = get_record(rec_id)
        d = dict(
            title=r['title'],
            link=url_for('record.metadata', recid=rec_id)
        )
    except ValueError:
        # doi ?
        d = dict(title=rec_id, link='http://doi.org/' + rec_id)
    except TypeError:
        return ''

    return '<a href="%(link)s"><span class="label label-primary">%(title)s</span></a>' % d


def escape_values(bfo):
    return 0

