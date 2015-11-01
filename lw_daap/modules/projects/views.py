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

from flask import Blueprint, render_template, request, flash, \
    url_for, redirect, current_app, jsonify
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu
from flask_login import current_user
from flask_restful import abort

from invenio.ext.cache import cache
from invenio.legacy.bibrecord import record_add_field

from invenio.base.decorators import wash_arguments
from invenio.base.i18n import _
from invenio.base.globals import cfg
from invenio.ext.sslify import ssl_required
from invenio.ext.sqlalchemy import db
from invenio.modules.formatter import format_record
from invenio.modules.records.api import get_record

from lw_daap.ext.login import login_required
from lw_daap.modules.invenio_groups.models import Group

from .forms import ProjectForm, SearchForm, EditProjectForm,\
    DeleteProjectForm, IntegrateForm
from .models import Project

from .utils import get_cache_key

blueprint = Blueprint(
    'lwdaap_projects',
    __name__,
    url_prefix='/projects',
    static_folder="static",
    template_folder="templates",
)


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
@register_menu(
    blueprint,
    'settings.myprojects',
    _('%(icon)s My Projects',
      icon='<i class="fa fa-list-alt fa-fw"></i>'),
    order=0,
    active_when=lambda: request.endpoint.startswith("lwdaap_projects"),)
@register_breadcrumb(blueprint, 'breadcrumbs.settings.myprojects',
                     _('My Projects'))
@login_required
def myprojects():
    myprojects = Project.get_user_projects(current_user).order_by(
        db.asc(Project.title)).all()
    ctx = {
        'myprojects': myprojects,
        'deleteform': DeleteProjectForm(),
    }
    return render_template(
        'projects/myview.html',
        **ctx
    )


@blueprint.route('/new/', methods=['GET', 'POST'])
@ssl_required
@login_required
@register_breadcrumb(blueprint, '.new', _('Create new'))
def new():
    uid = current_user.get_id()
    form = ProjectForm(request.values, crsf_enabled=False)

    ctx = {
        'form': form,
        'is_new': True,
        'project': None,
    }

    if request.method == 'POST' and form.validate():
        # Map form
        data = form.data
        p = Project(id_user=uid, **data)
        db.session.add(p)
        db.session.commit()
        p.save_collection()
        p.save_group()
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
    if not project.is_user_allowed():
        abort(401)

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
        project.save_group()
        flash("Project successfully edited.", category='success')
        return redirect(url_for('.show', project_id=project.id))

    return render_template(
        "projects/new.html",
        **ctx
    )


def _build_integrate_draft(project, selected_records):
    from lw_daap.modules.invenio_deposit.models \
        import DepositionDraftCacheManager

    rel_dataset = []
    rel_software = []
    for recid in selected_records:
        r = get_record(recid)
        rec_info = {
            'title': '%s (record id: %s)' % (r.get('title'), recid),
            'identifier': recid,
        }
        if r.get('upload_type') == 'dataset':
            rel_dataset.append(rec_info)
        elif r.get('upload_type') == 'software':
            rel_software.append(rec_info)
    current_app.logger.debug(rel_dataset)
    current_app.logger.debug(rel_software)
    draft_cache = DepositionDraftCacheManager.get()
    draft_cache.data['project_collection'] = project.id
    draft_cache.data['record_curated_in_project'] = True
    draft_cache.data['record_public_from_project'] = False
    draft_cache.data['rel_dataset'] = rel_dataset
    draft_cache.data['rel_software'] = rel_software
    draft_cache.save()


def integrate(project, page=1):
    if not project.is_user_allowed():
        abort(401)

    records = project.get_project_records(
        record_types=['dataset', 'software'],
        curated=True)

    form = IntegrateForm(request.values)
    form.records.choices = [(r.id, r.id) for r in records]
    selected_records = [int(recid) for recid in form.records.data or []]

    if request.method == 'POST':
        if form.validate():
            if form.integrate.data == "yes":
                _build_integrate_draft(project, selected_records)
                return redirect(url_for('webdeposit.create',
                                        deposition_type='analysis'))
                flash("INTEGRATE! %s" % selected_records, category="success")
        else:
            flash("Something weird happened %s" % form.errors,
                  category='error')

    page = max(page, 1)
    per_page = cfg.get('RECORDS_IN_PROJECTS_DISPLAYED_PER_PAGE', 5)
    records = records.paginate(page, per_page=per_page)

    ctx = dict(
        selected_records=selected_records,
        form=form,
        path='integrate',
        project=project,
        records=records,
        format_record=format_record,
        page=page,
        per_page=per_page,
    )
    return render_template('projects/integrate.html', **ctx)


@blueprint.route('/<int:project_id>/show/', defaults={'path': 'plan'},
                 methods=['GET', 'POST'])
@blueprint.route('/<int:project_id>/show/<path:path>', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.show', 'Show')
@wash_arguments({'page': (int, 1)})
def show(project_id, path, page):
    project = Project.query.get_or_404(project_id)
    if not project.is_user_allowed():
        path = 'public'
    if path == 'integrate':
        return integrate(project, page)

    tabs = {
        'plan': {
            'template': 'projects/plan.html',
            'q': {'record_types': ['dmp']},
        },
        'collect': {
            'template': 'projects/collect.html',
            'q': {'record_types': ['dataset', 'software']},
        },
        'curate': {
            'template': 'projects/curate.html',
            'q': {'record_types': ['dataset']},
        },
        'analyze': {
            'template': 'projects/analyze.html',
            'q': {'record_types': ['analysis']},
        },
        'preserve': {
            'template': 'projects/preserve.html',
            'q': {'curated': True},
        },
        'publish': {
            'template': 'projects/publish.html',
            'q': {'curated': True},
        },
        'public': {
            'template': 'projects/show.html',
            'q': {'public': True},
        }
    }

    try:
        tab_info = tabs[path]
    except KeyError:
        abort(404)
    query_opts = tab_info.get('q', {})
    records = project.get_project_records(**query_opts)
    page = max(page, 1)
    per_page = cfg.get('RECORDS_IN_PROJECTS_DISPLAYED_PER_PAGE', 5)
    records = records.paginate(page, per_page=per_page)

    template = tab_info.get('template')
    current_app.logger.debug("TEMPLATE: %s" % template)

    ctx = dict(
        path=path,
        project=project,
        records=records,
        format_record=format_record,
        page=page,
        per_page=per_page,
    )

    return render_template(template, **ctx)


@blueprint.route('/<int:project_id>/delete', methods=['POST'])
@ssl_required
@login_required
def delete(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.get_id() != project.id_user:
        flash('Only the owner of the project can delete it', category='error')
        abort(404)
    if project.is_public:
        flash('Project has public records, cannot be deleted',
              category='error')
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


@blueprint.route('/<int:project_id>/deposit/<depositions:deposition_type>',
                 methods=['GET'])
@ssl_required
@login_required
def deposit(project_id, deposition_type):
    project = Project.query.get_or_404(project_id)
    if not project.is_user_allowed():
        flash('Only the owner of the project can deposit records on it',
              category='error')
        abort(404)

    from lw_daap.modules.invenio_deposit.models \
        import DepositionDraftCacheManager
    draft_cache = DepositionDraftCacheManager.get()
    draft_cache.data['project_collection'] = project_id
    curated = deposition_type.lower() != 'dataset'
    draft_cache.data['record_curated_in_project'] = curated
    draft_cache.data['record_public_from_project'] = False
    draft_cache.save()

    return redirect(url_for('webdeposit.create',
                    deposition_type=deposition_type, next=next))


def error_400(msg):
    response = jsonify({'code': 400, 'msg': msg})
    response.status_code = 400
    return response


@blueprint.route('/<int:project_id>/curate/<int:record_id>/',
                 methods=['POST'])
@ssl_required
@login_required
def curation(project_id, record_id):
    project = Project.query.get_or_404(project_id)
    record = get_record(record_id)
    if not record:
        abort(404)

    # do only allow to curate to the owner
    if not project.is_user_allowed():
        abort(401)

    # crazy invenio stuff, cache actions so they dont get duplicated
    key = get_cache_key(record_id)
    cache_action = cache.get(key)
    if cache_action == 'curate':
        return error_400('Record is being curated, '
                         'you should wait some minutes.')
    # Set 5 min cache to allow bibupload/bibreformat to finish
    cache.set(key, 'curate', timeout=5*60)

    rec = {}
    record_add_field(rec, '001', controlfield_value=str(record_id))
    project_info_fields = [('a', 'True')]
    record_add_field(rec, tag='983', ind1='_',
                     ind2='_', subfields=project_info_fields)
    project_info_fields = [('b', 'False')]
    record_add_field(rec, tag='983', ind1='_',
                     ind2='_', subfields=project_info_fields)
    from invenio.legacy.bibupload.utils import bibupload_record
    bibupload_record(record=rec, file_prefix='project_info', mode='-c',
                     opts=[], alias="project_info")

    return jsonify({'status': 'ok',
                    'redirect': url_for('.show',
                                        project_id=project_id, path='curate')})


@blueprint.route('/<int:project_id>/preserve/<int:record_id>/',
                 methods=['POST'])
@ssl_required
@login_required
def preserve(project_id, record_id):
    from lw_daap.modules.pids.views import mint_doi
    return mint_doi(record_id, project_id)


@blueprint.route('/<int:project_id>/join/',
                 methods=['POST', 'GET'])
@ssl_required
@login_required
def join(project_id):
    project = Project.query.get_or_404(project_id)
    group = project.group
    if group.can_join(current_user):
        group.subscribe(current_user)
    return redirect(url_for('.show', project_id=project_id, path='plan'))


@blueprint.route('/<int:project_id>/publish/<int:record_id>/',
                 methods=['POST'])
@ssl_required
@login_required
def publication(project_id, record_id):
    project = Project.query.get_or_404(project_id)
    record = get_record(record_id)
    if not record:
        abort(404)

    # do only allow to curate to the owner
    if not project.is_user_allowed():
        abort(401)

    # crazy invenio stuff, cache actions so they dont get duplicated
    key = get_cache_key(record_id)
    cache_action = cache.get(key)
    if cache_action == 'publish':
        return error_400('Record is being published, '
                         'you should wait some minutes.')
    # Set 5 min cache to allow bibupload/bibreformat to finish
    cache.set(key, 'publish', timeout=5*60)

    rec = {}
    record_add_field(rec, '001', controlfield_value=str(record_id))
    project_info_fields = [('a', 'True')]
    record_add_field(rec, tag='983', ind1='_',
                     ind2='_', subfields=project_info_fields)
    project_info_fields = [('b', 'True')]
    record_add_field(rec, tag='983', ind1='_',
                     ind2='_', subfields=project_info_fields)
    from invenio.legacy.bibupload.utils import bibupload_record
    bibupload_record(record=rec, file_prefix='project_info', mode='-c',
                     opts=[], alias="project_info")

    return jsonify({'status': 'ok',
                    'redirect': url_for('.show',
                                        project_id=project_id,
                                        path='publish')})
