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

from .forms import InstrumentForm

from flask_login import current_user
import urllib2
from .models import Instrument
from .forms import ProjectForm, SearchForm, EditProjectForm,\
    DeleteProjectForm, IntegrateForm


blueprint = Blueprint(
    'lwdaap_instruments',
    __name__,
    url_prefix="/instruments",
    static_folder="static",
    template_folder="templates",
)
@blueprint.route('/', methods=['GET', ])
@register_menu(blueprint, 'main.instruments', _('Instruments'), order=3)
@register_breadcrumb(blueprint, '.', _('Instruments'))
@wash_arguments({'p': (unicode, ''),
                 'so': (unicode, ''),
                 'page': (int, 1),
                 })
def index(p, so, page):
    instruments = Instrument.filter_instruments(p, so)

    page = max(page, 1)
    per_page = cfg.get('INSTRUMENTS_DISPLAYED_PER_PAGE', 9)
    instruments = instruments.paginate(page, per_page=per_page)

    form = SearchForm()

    ctx = dict(
        instruments=instruments,
        form=form,
        page=page,
        per_page=per_page,
    )
    return render_template(
        "instruments/index.html",
        **ctx
    )
