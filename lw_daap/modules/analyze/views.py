import json

from flask import Blueprint, current_app, render_template, request, redirect, url_for
from flask_menu import register_menu

from forms import LaunchForm
from infra import launch_vm, list_vms

from lw_daap.modules.profile.decorators import delegation_required


blueprint = Blueprint(
    'lwdaap_analyze',
    __name__,
    url_prefix='/analyze',
    template_folder='templates',
    static_folder='static',
)


@blueprint.route('/')
@register_menu(blueprint, 'main.analyze', 'Analyze', order=3)
@delegation_required
def index():
    ctx = dict(
        vms=list_vms()
    )
    return render_template('analyze/index.html', **ctx)


@blueprint.route('/launch', methods=['GET', 'POST'])
@delegation_required
def launch():
    form = LaunchForm(request.form)
    form.fill_fields_choices()
    if form.validate_on_submit():
        launch_vm(name=form.name.data,
                  image=form.image.data,
                  flavor=form.flavor.data,
                  app_env=form.app_env.data)
        return redirect(url_for('.index'))
    ctx = dict(
        form = form,
    )
    return render_template('analyze/launch.html', **ctx)
