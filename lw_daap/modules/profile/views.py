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

from flask import abort, Blueprint, current_app, flash, jsonify, \
    render_template, request
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu

from invenio.base.i18n import _
from invenio.base.globals import cfg
from invenio.ext.sslify import ssl_required

from lw_daap.ext.login import login_required

from .forms import ProfileForm
from .models import UserProfile
from .proxy_utils import add_voms_info, get_client_proxy_info, \
    generate_proxy_request, build_proxy

from .service_utils import existDBUser, createDBUser, changeDBPassword, findByDatabaseUser, findByPortalUser, addUserDB
from flask_login import current_user
import urllib2


blueprint = Blueprint(
    'userprofile',
    __name__,
    url_prefix="/account/settings",
    static_folder="static",
    template_folder="templates",
)


@blueprint.route("/profile", methods=['GET', 'POST'])
@ssl_required
@login_required
@register_menu(
    blueprint, 'settings.profile',
    _('%(icon)s Profile', icon='<i class="fa fa-user fa-fw"></i>'),
    order=0,
    active_when=lambda: request.endpoint.startswith("userprofile."),
)
@register_breadcrumb(blueprint, 'breadcrumbs.settings.profile', _('Profile'))
def index():
    profile = UserProfile.get_or_create()
    form = ProfileForm(request.form, obj=profile)
    if form.validate_on_submit():
        try:
            dbUser = form.user_db.data
            dbPass = form.pass_db.data
            portalUser = current_user['nickname']

            if not existDBUser(dbUser):
                createDBUser(dbUser, dbPass)
            else:
                changeDBPassword(dbUser, dbPass)

            if not findByDatabaseUser(dbUser) and not findByPortalUser(portalUser):
                addUserDB(dbUser, portalUser)
            profile.update(**form.data)
            flash(_('Profile was updated'), 'success')
        except Exception as e:
            current_app.logger.debug("ERROR")
            flash(str(e), 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.debug("Error in the %s field - %s" % (
                                         getattr(form, field).label.text,
                                         error))

    ctx = dict(
        form=form,
        profile=profile,
    )
    ctx.update(get_client_proxy_info(profile))
    return render_template(
        "profile/profile.html",
        **ctx
    )


@blueprint.route("/profile/delegation")
@ssl_required
@login_required
@register_breadcrumb(blueprint, 'breadcrumbs.settings.profile', _('Profile'))
def delegate():
    profile = UserProfile.get_or_create()
    ctx = dict(profile=profile)
    ctx.update(get_client_proxy_info(profile))
    return render_template(
        "profile/delegation.html",
        **ctx
    )


@blueprint.route("/proxy-request")
@ssl_required
@login_required
def csr_request():
    profile = UserProfile.get_or_create()
    priv_key, csr = generate_proxy_request()
    profile.update(csr_priv_key=priv_key)
    return csr


@blueprint.route('/delegate-proxy', methods=['POST'])
@ssl_required
@login_required
def delegate_proxy():
    profile = UserProfile.get_or_create()
    if not profile.csr_priv_key:
        current_app.logger.debug("NO KEY!")
        abort(400)
    try:
        proxy = request.data
    except KeyError:
        current_app.logger.debug("NO proxy!")
        abort(400)

    new_proxy, time_left = build_proxy(proxy, profile.csr_priv_key)
    if cfg.get('CFG_DELEGATION_VO'):
        new_proxy = add_voms_info(new_proxy, cfg['CFG_DELEGATION_VO'])
    profile.update(user_proxy=new_proxy)

    return jsonify(dict(
        user_proxy=True,
        time_left=time_left
    ))


@blueprint.route('/delete-proxy', methods=['POST'])
@ssl_required
@login_required
def delete_proxy():
    profile.update(user_proxy=None)
    return ''
