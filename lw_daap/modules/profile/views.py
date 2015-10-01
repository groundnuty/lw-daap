from __future__ import absolute_import

from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
import humanize
import pytz

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import current_user
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu, current_menu

from invenio.base.i18n import _
from invenio.ext.sslify import ssl_required
from invenio.ext.login import reset_password

from lw_daap.ext.login import login_required

from .forms import  *
from .models import *

from .proxy_utils import get_client_proxy_info, generate_proxy_request, build_proxy


blueprint = Blueprint(
    'userProfile',
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
    active_when=lambda: request.endpoint.startswith("userProfile."),
)
@register_breadcrumb(blueprint, 'breadcrumbs.settings.profile', _('Profile'))
def index():
    profile = userProfile.get_or_create()
    form = ProfileForm(request.form, obj=profile)
    if form.validate_on_submit():
        try:
            profile.update(**form.data)
            flash(_('Profile was updated'), 'success')
        except Exception as e:
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
    profile = userProfile.get_or_create()
    ctx = dict(profile=profile)
    ctx.update(get_client_proxy_info(profile))
    return render_template(
        "profile/delegation.html",
        **ctx
    )


@blueprint.route("/proxy_request")
@ssl_required
@login_required
def csr_request():
    profile = userProfile.get_or_create()
    priv_key, csr = generate_proxy_request()
    profile.update(csr_priv_key=priv_key)
    return jsonify(dict(
        csr=csr
    ))


@blueprint.route('/delegate-proxy', methods=['POST'])
@ssl_required
@login_required
def delegate_proxy():
    profile = userProfile.get_or_create()
    if not profile.csr_priv_key:
        abort(400)
    try:
        proxy = request.form['x509Proxy']
    except KeyError:
        abort(400)

    new_proxy, time_left = build_proxy(proxy, profile.csr_priv_key)
    profile.update(user_proxy=new_proxy)

    return jsonify(dict(
        user_proxy=True,
        time_left=humanize.naturaldelta(time_left),
    ))


@blueprint.route('/delete-proxy', methods=['POST'])
@ssl_required
@login_required
def delete_proxy():
    profile = userProfile.get_or_create()
    profile.update(user_proxy=None)
    return ''
