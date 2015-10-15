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

import json

from flask import Blueprint, current_app, render_template, request, redirect, url_for
from flask_menu import register_menu

from flask import Response, jsonify


from lw_daap.modules.profile.decorators import delegation_required
from lw_daap.modules.profile.models import userProfile 

from . import infra
from .forms import LaunchForm, LaunchFormData
from .utils import get_requirements

blueprint = Blueprint(
    'lwdaap_analyze',
    __name__,
    url_prefix='/analyze',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/')
@register_menu(blueprint, 'main.analyze', 'Analyze', order=3)
@delegation_required()
def index():
    profile = userProfile.get_or_create()
    client = infra.get_client(profile.user_proxy)
    ctx = dict(
        vms = infra.list_vms(client),
    )
    return render_template('analyze/index.html', **ctx)


@blueprint.route('/launch', methods=['GET', 'POST'])
@delegation_required()
def launch():
    profile = userProfile.get_or_create()
    reqs = get_requirements()
    obj = LaunchFormData(reqs, **request.args)
    form = LaunchForm(obj=obj, user_profile=profile)
    form.fill_fields_choices(reqs)
    if form.validate_on_submit():
        client = infra.get_client(profile.user_proxy)
        infra.launch_vm(client, name=form.name.data, image=form.image.data,
                        flavor=form.flavor.data, app_env=form.app_env.data,
                        ssh_key=profile.ssh_public_key)
        # XXX TODO error checking
        return redirect(url_for('.index'))
    ctx = dict(
        form=form,
        flavors=reqs['flavors'],
    )
    return render_template('analyze/launch.html', **ctx)


@blueprint.route('/terminate/<vm_id>', methods=['POST'])
@delegation_required()
def terminate(vm_id):
    profile = userProfile.get_or_create()
    client = infra.get_client(profile.user_proxy)
    infra.terminate_vm(client, vm_id)
    return redirect(url_for('.index'))


@blueprint.route('/connect/<vm_id>', methods=['GET'])
def connect(vm_id):
    profile = userProfile.get_or_create()
    client = infra.get_client(profile.user_proxy)
    return jsonify(infra.get_vm_connection(client, vm_id))
