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

from flask import Blueprint, render_template, request, flash, url_for, redirect, current_app
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu
from flask_login import current_user

from invenio.base.i18n import _
from invenio.base.globals import cfg
from invenio.ext.sslify import ssl_required
from invenio.ext.principal import permission_required
from invenio.ext.sqlalchemy import db
from invenio.utils.pagination import Pagination

from lw_daap.ext.login import login_required

from .forms import ProjectForm, SearchForm, EditProjectForm
from .models import Project

blueprint = Blueprint(
    'lwdaap_projects',
    __name__,
    url_prefix='/projects',
    static_folder="static",
    template_folder="templates",
)


def myprojects_ctx():
    """Helper method for return ctx used by many views."""
    uid = current_user.get_id()
    return { 'myprojects': Project.query.filter_by(id_user=uid).order_by(db.asc(Project.title)).all() }


@blueprint.route('/', methods=['GET', ])
@register_menu(blueprint, 'main.projects', _('Projects'), order=2)
@register_breadcrumb(blueprint, '.', _('Projects'))
def index():
    ctx = myprojects_ctx()

    # these should come as query params
    p = so = None
    page = 1
    ###############
    projects = Project.filter_projects(p, so)
    per_page = cfg.get('PROJECTS_DISPLAYED_PER_PAGE', 10)
    page = max(page, 1)
    pagination = Pagination(page, per_page, projects.count())

    form = SearchForm()

    ctx.update({
        'projects': projects,
        'form': form,
        'pagination': pagination,
    })
    return render_template(
        "projects/index.html",
        **ctx
    )


@blueprint.route('/myprojects')
@register_menu(blueprint,
        'settings.myprojects',
        _('%(icon)s My Projects', icon='<i class="fa fa-list-alt fa-fw"></i>'),
        order=0,
        active_when=lambda: request.endpoint.startswith("lwdaap_projects"),
)
@register_breadcrumb(blueprint, 'breadcrumbs.settings.myprojects', _('My Projects'))
@login_required
def myprojects():
    ctx = myprojects_ctx()
    return render_template(
        'projects/myview.html',
        **ctx
    )


@blueprint.route('/new/', methods=['GET', 'POST'])
@ssl_required
@login_required
@permission_required('submit')
@register_breadcrumb(blueprint, '.new', _('Create new'))
def new():
    uid = current_user.get_id()
    form = ProjectForm(request.values, crsf_enabled=False)

    ctx = myprojects_ctx()
    ctx.update({
        'form': form,
        'is_new': True,
        'project': None,
    })

    if request.method == 'POST' and form.validate():
        # Map form
        data = form.data
        p = Project(id_user=uid, **data)
        db.session.add(p)
        db.session.commit()
        p.save_collection()
        flash("Project was successfully created.", category='success')
        return redirect(url_for('.show', project_id=p.id))

    return render_template(
        "projects/new.html",
        **ctx
    )

@blueprint.route('/edit/<int:project_id>/', methods=['GET', 'POST'])
@ssl_required
@login_required
@register_breadcrumb(blueprint, '.edit', _('Edit'))
def edit(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.get_id() != project.id_user:
        abort(404)

    form = EditProjectForm(request.values, project)
    ctx = dict(
        form=form,
        is_new=False,
        project=project,
    )

    if request.method == 'POST' and form.validate():
        for field, val in form.data.items():
            setattr(project, field, val)
        db.session.commit()
        project.save_collection()
        flash("Project successfully edited.", category='success')
        return redirect(url_for('.show', project_id=project.id))

    return render_template(
        "projects/new.html",
        **ctx
    ) 
    


def project_breadcrumb(*args, **kwargs):
    project_id = request.view_args['project_id']
    project = Project.query.get(project_id)
    # XXX  FIXME
    return [{'text': project.title,
             'url': url_for('.show', project_id=project_id)}]


@blueprint.route('/show/<int:project_id>', methods=['GET'])
@register_breadcrumb(blueprint, '.show', 'Show')
def show(project_id):
    project = Project.query.get_or_404(project_id)
    ctx = dict(
        project=project,
    )
    return render_template("projects/show.html", **ctx)
