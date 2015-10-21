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

from flask import Blueprint, render_template
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu

from invenio.base.i18n import _

blueprint = Blueprint(
    'lwdaap_projects',
    __name__,
    url_prefix='/projects',
    static_folder="static",
    template_folder="templates",
)


@blueprint.route('/', methods=['GET', ])
@register_breadcrumb(blueprint, '.', _('Projects'))
@register_menu(blueprint, 'main.projects', _('Projects'), order=2)
def index():
    ctx = {}
    return render_template(
        "projects/index.html",
        **ctx
    )
