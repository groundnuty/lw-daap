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

## This file is part of Zenodo.
## Copyright (C) 2012, 2013, 2014 CERN.
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

import re

from flask import current_app
from flask_login import current_user

from lw_daap.modules.invenio_deposit.validation_utils import DOISyntaxValidator 


def community_autocomplete(dummy_form, dummy_field, term, limit=50):
    from invenio.modules.communities.models import Community

    if not term:
        objs = Community.query.limit(limit).all()
    else:
        term = '%' + term + '%'
        objs = Community.query.filter(
            Community.title.like(term) | Community.id.like(term),
            Community.id != 'daap'
        ).filter_by().limit(limit).all()

    return map(
        lambda o: {
            'value': o.title,
            'fields': {
                'identifier': o.id,
                'title': o.title,
                'curatedby': o.owner.nickname,
                'description': o.description,
                'provisional': True,
            }
        },
        objs
    )


def accessgroups_autocomplete(dummy_form, dummy_field, term, limit=50):
    from lw_daap.modules.invenio_groups.models import Group

    if not term:
        objs = Group.query.limit(limit).all()
    else:
        term = '%' + term + '%'
        objs = Group.query.filter(
            Group.name.like(term)
        ).filter_by().limit(limit).all()

    return map(
        lambda o: {
            'value': o.name,
            'fields': {
                'identifier': o.id,
                'title': o.name,
            }
        },
        objs
    )


def inputrecords_autocomplete_dataset(dummy_form, dummy_field, term, limit=50):
    from invenio.legacy.search_engine import search_pattern_parenthesised
    from invenio.modules.records.models import Record
    from invenio.modules.records.api import get_record

    if not term:
        objs = Record.query.limit(limit).all()
    else:
        # datasets from projects w/ curate = True
        recids = search_pattern_parenthesised(
            #p='title:%%%s%% AND 980__:dataset AND (980__:community-* OR (8560_w:%s AND (NOT 980__:project-* OR 983__a:True)))' % (term.encode('utf-8'), current_user.get_id()))
            p='title:%%%s%% AND 980__:dataset AND (980__:community-* OR 8560_w:%s)' % (term.encode('utf-8'), current_user.get_id()))
        objs = Record.query.filter(
            Record.id.in_(recids)
        ).filter_by().limit(limit).all()
        if not objs:
            if re.match(DOISyntaxValidator.pattern, term, re.I):
                return [{
                    'value': "%s (doi)" % term,
                    'fields': {
                        'identifier': term,
                        'title': "%s (doi)" %  term,
                    }
                }] 

    return map(
        lambda o: {
            'value': "%s (record id: %s)" % (o[1], o[0]),
            'fields': {
                'identifier': o[0],
                'title': "%s (record id: %s)" % (o[1], o[0]),
            }
        },
        map(lambda o: (o.id, get_record(o.id)['title']), 
            filter(lambda o: get_record(o.id)['project_collection'] != None 
                   and get_record(o.id)['record_curated_in_project'] == True , objs))
    )


def inputrecords_autocomplete_software(dummy_form, dummy_field, term, limit=50):
    from invenio.legacy.search_engine import search_pattern_parenthesised
    from invenio.modules.records.models import Record
    from invenio.modules.records.api import get_record

    if not term:
        objs = Record.query.limit(limit).all()
    else:
        recids = search_pattern_parenthesised(
            p='title:%%%s%% AND 980__:software AND (980__:community-* OR 8560_w:%s)' % (term.encode('utf-8'), current_user.get_id()))
        objs = Record.query.filter(
            Record.id.in_(recids)
        ).filter_by().limit(limit).all()
        if not objs:
            if re.match(DOISyntaxValidator.pattern, term, re.I):
                return [{
                    'value': "%s (doi)" % term,
                    'fields': {
                        'identifier': term,
                        'title': "%s (doi)" %  term,
                    }
                }] 

    return map(
        lambda o: {
            'value': "%s (record id: %s)" % (o[1], o[0]),
            'fields': {
                'identifier': o[0],
                'title': "%s (record id: %s)" % (o[1], o[0]),
            }
        },
        map(lambda o: (o.id, get_record(o.id)['title']), objs)
    )
