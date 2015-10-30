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

#
# This file is part of Zenodo.
# Copyright (C) 2014, 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or modify
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


from __future__ import absolute_import

from flask import Blueprint, render_template, \
    request, current_app, abort, jsonify

from invenio.ext.sslify import ssl_required

from lw_daap.ext.login import login_required

from .utils import sync, utcnow, parse_timestamp, remove_hook, create_hook, \
    init_account
from .helpers import get_api, get_token, get_account, check_token


blueprint = Blueprint(
    'lwdaap_github',
    __name__,
    static_folder="static",
    template_folder="templates",
    url_prefix="/github",
)


@blueprint.route('/')
@ssl_required
@login_required
def index():
    token = get_token()
    ctx = dict(connected=False)

    if token is not None and check_token(token):
        extra_data = token.remote_account.extra_data
        if extra_data.get("login") is None:
            init_account(token)
            extra_data = token.remote_account.extra_data
        sync(get_api(), extra_data)

        ctx.update({
            "connected": True,
            "repos": extra_data['repos'],
            "name": extra_data['login'],
            "user_id": token.remote_account.user_id,
            # "last_sync": humanize.naturaltime(now - last_sync),
        })
    return render_template("github/index.html", **ctx)


@blueprint.route('/releases/<owner>/<name>')
@ssl_required
@login_required
def releases(owner, name):

    token = get_token()
    ctx = dict(connected=False)

    if token is not None and check_token(token):
        extra_data = token.remote_account.extra_data
        if extra_data.get("login") is None:
            init_account(token)
            extra_data = token.remote_account.extra_data
        gh = get_api()
        repo = gh.repository(owner, name)
        releases = []
        for r in repo.iter_releases():
            releases.append(r)
        ctx.update({
            "connected": True,
            "repo": {"owner": repo.owner, "name": repo.name},
            "name": extra_data['login'],
            "user_id": token.remote_account.user_id,
            "releases": releases,
        })
    return render_template("github/releases.html", **ctx)


@blueprint.route('/releases/<owner>/<name>/<release_id>')
def select_release(owner, name, release_id):
    token = get_token()
    ctx = dict(connected=False)

    if token is not None and check_token(token):
        extra_data = token.remote_account.extra_data
        if extra_data.get("login") is None:
            init_account(token)
            extra_data = token.remote_account.extra_data
        gh = get_api()
        repo = gh.repository(owner, name)
        release = repo.release(release_id)

        print release.tag_name
        for tag in repo.iter_tags():
            if tag.name == release.tag_name:
                return jsonify({"url": tag.tarball_url,
                                "name": tag.name,
                                "owner": owner,
                                "repo": name})
        abort(404)
    abort(400)
