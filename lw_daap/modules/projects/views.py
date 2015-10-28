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
from flask_restful import abort

from invenio.legacy.bibrecord import record_add_field

from invenio.base.decorators import wash_arguments
from invenio.base.i18n import _
from invenio.base.globals import cfg
from invenio.ext.sslify import ssl_required
from invenio.ext.principal import permission_required
from invenio.ext.sqlalchemy import db
from invenio.modules.formatter import format_record
from lw_daap.ext.login import login_required

from .forms import ProjectForm, SearchForm, EditProjectForm, DeleteProjectForm
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
@wash_arguments({'p': (unicode, ''),
                 'so': (unicode, ''),
                 'page': (int, 1),
                 })
def index(p, so, page):
    projects = Project.filter_projects(p, so)

    page = max(page, 1)
    per_page = cfg.get('PROJECTS_DISPLAYED_PER_PAGE', 9)
    projects = projects.paginate(page, per_page=per_page)

    form = SearchForm()

    ctx = dict(
        projects=projects,
        form=form,
        page=page,
        per_page=per_page,
    )
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
    ctx.update({
        "deleteform": DeleteProjectForm()
    })
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


@blueprint.route('/<int:project_id>/edit/', methods=['GET', 'POST'])
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
    current_app.logger.debug("REDIRECT TO %s" % url_for('.show', project_id=project.id))

    if request.method == 'POST' and form.validate():
        for field, val in form.data.items():
            setattr(project, field, val)
        db.session.commit()
        project.save_collection()
        flash("Project successfully edited.", category='success')
        current_app.logger.debug("REDIRECT TO %s" % url_for('.show', project_id=project.id))
        return redirect(url_for('.show', project_id=project.id))

    return render_template(
        "projects/new.html",
        **ctx
    )

@blueprint.route('/<int:project_id>/show/', defaults={'path': 'plan'}, methods=['GET'])
@blueprint.route('/<int:project_id>/show/<path:path>', methods=['GET'])
@register_breadcrumb(blueprint, '.show', 'Show')
@wash_arguments({'p': (unicode, ''),
                 'so': (unicode, ''),
                 'page': (int, 1),
                 'dmpage': (int, 1),
                 'dtpage': (int, 1),
                 'sfpage': (int, 1),
                 'nlpage': (int, 1),
                 'pbpage': (int, 1),
                 })
def show(project_id, path,
         p, so, page, dmpage, dtpage, sfpage, nlpage, pbpage):
    project = Project.query.get_or_404(project_id)
    records = project.get_project_records()
    records_dmp = project.get_project_records_by_type('dmp')
    records_dataset = project.get_project_records_by_type('dataset')
    records_software = project.get_project_records_by_type('software')
    records_analysis = project.get_project_records_by_type('analysis')
    records_public = project.get_project_records_public()

    page = max(page, 1)
    per_page = cfg.get('RECORDS_IN_PROJECTS_DISPLAYED_PER_PAGE', 1)
    records = records.paginate(page, per_page=per_page)
    records_dmp = records_dmp.paginate(dmpage, per_page=per_page)
    records_dataset = records_dataset.paginate(dtpage, per_page=per_page)
    records_software = records_software.paginate(sfpage, per_page=per_page)
    records_analysis = records_analysis.paginate(nlpage, per_page=per_page)
    records_public = records_public.paginate(pbpage, per_page=per_page)

    tab_templates = {
        'plan': 'projects/plan.html',
        'collect': 'projects/collect.html',
        'curate': 'projects/curate.html',
        'integrate': 'projects/integrate.html',
        'analyze': 'projects/analyze.html',
        'preserve': 'projects/preserve.html',
        'publish': 'projects/publish.html',
    }
    template = tab_templates.get(path, None)

    ctx = dict(
        tab='projects/' + path + '.html',
        project=project,
        records=records,
        records_dmp=records_dmp,
        records_dataset=records_dataset,
        records_software=records_software,
        records_analysis=records_analysis,
        records_public=records_public,
        format_record=format_record,
        page=page,
        dmpage=dmpage,
        dtpage=dtpage,
        sfpage=sfpage,
        nlpage=nlpage,
        pbpage=pbpage,
        per_page=per_page,
    )

    if template is not None:
        return render_template(template, **ctx)
    abort(404)


@blueprint.route('/<int:project_id>/delete', methods=['POST'])
@ssl_required
@login_required
@permission_required('submit')
def delete(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.get_id() != project.id_user:
        flash('Only the owner of the project can delete it', category='error')
        abort(404)
    if project.is_public:
        flash('Project has public records, cannot be deleted', category='error')
        abort(404)

    form = DeleteProjectForm(request.values)
    if request.method == 'POST' and form.validate():
        project.delete_collection()
        db.session.delete(project)
        db.session.commit()
        flash("Project was successfully deleted.", category='success')
    else:
        flash("Project cannot be deleted.", category='warning')
    return redirect(url_for('.myprojects'))


@blueprint.route('/<int:project_id>/deposit/<depositions:deposition_type>', methods=['GET'])
@ssl_required
@login_required
@permission_required('submit')
def deposit(project_id, deposition_type):
    project = Project.query.get_or_404(project_id)
    if current_user.get_id() != project.id_user:
        flash('Only the owner of the project can deposit records on it', category='error')
        abort(404)

    from lw_daap.modules.invenio_deposit.models import DepositionDraftCacheManager
    draft_cache = DepositionDraftCacheManager.get()
    draft_cache.data['project_collection'] = project_id
    draft_cache.data['record_curated_in_project'] = False
    draft_cache.data['record_public_from_project'] = False
    draft_cache.save()

    return redirect(url_for('webdeposit.create', deposition_type=deposition_type, next=next))

@blueprint.route('/<int:project_id>/show/curate/<int:record_id>/', methods=['POST'])
@ssl_required
@login_required
@permission_required('submit')
def curation(project_id, record_id):
    rec = {}
    record_add_field(rec, '001', controlfield_value=str(record_id))
    project_info_fields = [('a', 'True')]
    record_add_field(rec, tag='983', ind1='_', ind2='_', subfields=project_info_fields)    
    from invenio.legacy.bibupload.utils import bibupload_record
    bibupload_record(record=rec, file_prefix='project_info', mode='-c',
                     opts=[], alias="project_info")
    return rec
    

