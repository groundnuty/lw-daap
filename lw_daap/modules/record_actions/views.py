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

from __future__ import absolute_import

from flask import Blueprint
from invenio.ext.sslify import ssl_required
from invenio.ext.cache import cache
from lw_daap.ext.login import login_required

from .actions import record_actions, doi_action, control_actions, action_key


blueprint = Blueprint(
    'lwdaap_actions',
    __name__,
    url_prefix='/record_actions',
    static_folder="static",
    template_folder="templates",
)


@blueprint.app_template_global()
def get_pid(recid):
    return 'lifewatch.openscience/%s' % recid


@blueprint.app_template_filter()
def cached_record_action(record, action_name):
    """Determine if a given action is underway."""
    cache_action = cache.get(action_key(record['recid'], action_name))
    if cache_action == action_name:
        return True
    attrs_for_actions = {
        'curate': 'record_curated_in_project',
        'publish': 'record_publish_from_project',
        'archive': 'record_selected_for_archive',
        'doi': 'doi',
    }
    return record.get(attrs_for_actions[action_name], False)


@blueprint.route('/mint/<int:recid>', methods=['POST'])
@login_required
def mint_doi(recid):
    doi_msg = 'DOI is being processed.'
    return record_actions(recid=recid, action_name='doi', action=doi_action,
                          msg=doi_msg)


@blueprint.route('/archive/<int:recid>', methods=['POST'])
@login_required
def archive_record(recid):
    archive_msg = 'Archiving request is being processed.'
    return record_actions(recid=recid, action_name='archive',
                          action=lambda x: control_actions(x, archive=True),
                          msg=archive_msg)
