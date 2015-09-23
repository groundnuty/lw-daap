from __future__ import absolute_import

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu, current_menu

from invenio.base.i18n import _
from invenio.ext.sslify import ssl_required
from invenio.ext.login import reset_password

from .forms import  *
from .models import *


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
    active_when=lambda: request.endpoint.startswith("userProfile.")
)
@register_breadcrumb(blueprint, 'breadcrumbs.settings.profile', _('Profile'))
def index():
    profile = userProfile.get_or_create()
    form = ProfileForm(request.form, obj=profile)
    try:
        profile.update(**form.data)
        flash(_('Profile was update'), 'success')
    except Exception as e:
        flash(str(e), 'error')

    return render_template(
        "profile/profile.html",
        form=form,
        profile=profile
    )

