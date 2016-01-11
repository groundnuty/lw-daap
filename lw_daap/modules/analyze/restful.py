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

"""Helper REST API for getting files for analysis."""

from flask import send_file, current_app, url_for
from flask_restful import Resource, abort
from flask_login import current_user

from invenio.modules.records.api import get_record

from invenio.ext.restful import require_api_auth


class RecordFilesListResource(Resource):
    method_decorators = [
        require_api_auth()
    ]

    def get(self, recid):
        from invenio.legacy.bibdocfile.api import BibRecDocs
        from invenio.legacy.search_engine import check_user_can_view_record

        record = get_record(recid)
        if not record:
            abort(404)
        auth_code, _ = check_user_can_view_record(current_user, recid)
        if auth_code:
            abort(401) 
        ids = [recid]
        for k in ['rel_dataset', 'rel_software']:
            ids.extend([int(r) for r in record.get(k, [])])
        files = []
        for recid in ids:
            record_files = BibRecDocs(recid).list_latest_files(
                list_hidden=False)
            files.extend(
                map(
                    lambda f: {
                        'id': f.docid,
                        'name': '%s%s' % (f.name, f.format),
                        'url': url_for('recordfileresource',
                                        recid=recid, fileid=f.docid),
                    }, 
                    filter(lambda f: not f.is_icon(), record_files))
            )
        return files


class RecordFileResource(Resource):
    method_decorators = [
        require_api_auth()
    ]

    def get(self, recid, fileid):
        record = get_record(recid)
        if not record:
            abort(404)
        uid = current_user.get_id()
        from invenio.legacy.bibdocfile.api import BibRecDocs
        record_files = BibRecDocs(recid).list_latest_files(list_hidden=False)
        for f in record_files:
            if f.docid == fileid:
                docfile = f 
                break
        else:
            abort(404)
        if docfile.is_restricted(current_user)[0]:
            abort(401)
        filename='%s%s' % (docfile.name, docfile.format)
        return send_file(docfile.fullpath, mimetype=docfile.mime,
                         attachment_filename=filename)
 

def setup_app(app, api):
    api.add_resource(
        RecordFilesListResource,
        '/api/analysis_files/<int:recid>/',
    )
    api.add_resource(
        RecordFileResource,
        '/api/analysis_files/<int:recid>/<int:fileid>',
    )
