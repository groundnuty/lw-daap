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

from flask import current_app, url_for, abort, jsonify
from flask_login import current_user

from invenio.ext.cache import cache
from invenio.ext.logging import register_exception
from invenio.legacy.bibrecord import record_add_field
from invenio.modules.pidstore.models import PersistentIdentifier
from invenio.modules.pidstore.tasks import datacite_register
from invenio.modules.records.api import get_record

from lw_daap.modules.projects.models import Project

DOI_PID_TYPE = 'doi'


def build_doi(recid):
    return '10.5281/lwdaap.%s' % recid


def action_key(recid, action_name):
    return 'record_%s_%s' % (recid, action_name)


def add_doi_to_record(recid, doi):
    rec = {}
    record_add_field(rec, '001', controlfield_value=str(recid))
    pid_fields = [('a', doi), ('2', 'DOI')]
    record_add_field(rec, tag='024', ind1='7', subfields=pid_fields)

    from invenio.legacy.bibupload.utils import bibupload_record
    bibupload_record(record=rec, file_prefix='doi', mode='-c',
                     opts=[], alias="doi")
    return rec


def control_actions(record, curate=None, archive=None, publish=None):
    rec = {}
    record_add_field(rec, '001', controlfield_value=str(record['recid']))
    if curate is None:
        curate = record.get('record_curated_in_project', False)
    if archive is None:
        archive = record.get('record_selected_for_archive', False)
    if publish is None:
        publish = record.get('record_public_from_project', False)

    project_info_fields = [('a', '%s' % curate)]
    record_add_field(rec, tag='983', ind1='_',
                     ind2='_', subfields=project_info_fields)
    project_info_fields = [('b', '%s' % publish)]
    record_add_field(rec, tag='983', ind1='_',
                     ind2='_', subfields=project_info_fields)
    project_info_fields = [('c', '%s' % archive)]
    record_add_field(rec, tag='983', ind1='_',
                     ind2='_', subfields=project_info_fields)
    from invenio.legacy.bibupload.utils import bibupload_record
    bibupload_record(record=rec, file_prefix='project_info', mode='-c',
                     opts=[], alias="project_info")


def json_error(code, msg):
    response = jsonify({'code': code, 'msg': msg})
    response.status_code = code
    return response


def record_actions(recid=None, project_id=None, action_name='',
                   action=None, msg='', redirect_url=None):
    uid = current_user.get_id()
    record = get_record(recid)
    if not record:
        abort(404)

    # either the use is allowed in the project
    # or is the owner
    if project_id:
        project = Project.query.get_or_404(project_id)
        if not project.is_user_allowed():
            abort(401)
    else:
        if uid != int(record.get('owner', {}).get('id', -1)):
            abort(401)

    # crazy invenio stuff, cache actions so they dont get duplicated
    key = action_key(recid, action_name)
    cache_action = cache.get(key)
    if cache_action == action_name:
        return json_error(400, ' '.join([msg, 'Please wait some minutes.']))
    # Set 5 min cache to allow bibupload/bibreformat to finish
    cache.set(key, action_name, timeout=5 * 60)

    r = action(record)
    if r is not None:
        return r

    if redirect_url is None:
        redirect_url = url_for('record.metadata', recid=recid)
    return jsonify({'status': 'ok', 'redirect': redirect_url})


def doi_action(record):
    if record.get('doi', None) is not None:
        return json_error(400, 'Record already has a DOI.')

    recid = record['recid']
    doi = build_doi(recid)
    current_app.logger.info("Registering pid %s" % doi)
    pid = PersistentIdentifier.create(DOI_PID_TYPE, doi)
    if pid is None:
        pid = PersistentIdentifier.get(DOI_PID_TYPE, doi)
    try:
        pid.assign('rec', recid)
        datacite_register.delay(recid)
    except Exception, e:
        register_exception(alert_admin=True)
        return json_error(400, '%s' % e)

    add_doi_to_record(recid, doi)
    return None
