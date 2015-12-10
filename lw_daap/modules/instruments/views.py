from __future__ import absolute_import

from flask import abort, Blueprint, current_app, flash, jsonify, \
    render_template, request, redirect, url_for
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu

from invenio.base.i18n import _
from invenio.base.globals import cfg
from invenio.ext.sslify import ssl_required
from invenio.base.decorators import wash_arguments
from invenio.ext.sqlalchemy import db

from lw_daap.ext.login import login_required

from flask_login import current_user
import urllib2

from lw_daap.modules.instruments.models import Instrument
from lw_daap.modules.instruments.forms import SearchForm, InstrumentForm


blueprint = Blueprint(
    'lwdaap_instruments',
    __name__,
    url_prefix="/instruments",
    static_folder="static",
    template_folder="templates",
)
@blueprint.route('/', methods=['GET', ])
@register_menu(blueprint, 'main.instrument', _('Instruments'), order=2)
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

@blueprint.route('/new/', methods=['GET', 'POST'])
@ssl_required
@login_required
@register_breadcrumb(blueprint, '.new', _('Create new'))
def new():
    uid = current_user.get_id()
    form = InstrumentForm(request.values, crsf_enabled=False)

    ctx = {
        'form': form,
        'is_new': True,
        'instrument': None,
    }

    if request.method == 'POST' and form.validate():
        # Map form
        data = form.data
        # Extract access_groups from Instrument data
        access_groups = data['access_groups']
        del data['access_groups']

        i = Instrument(user_id=uid, **data)
        db.session.add(i)
        db.session.commit()
        i.save_collection()
        #i.save_group()
        flash("Instrument was successfully created.", category='success')
        return redirect(url_for('.show', instrument_id=i.id))

    return render_template(
        "instruments/new.html",
        **ctx
    )