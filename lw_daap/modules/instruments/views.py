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
from invenio.modules.formatter import format_record

from lw_daap.ext.login import login_required
from .service_utils import createInstrument
from lw_daap.modules.profile.service_utils import getUserInfoByPortalUser
from lw_daap.modules.profile.models import UserProfile

from flask_login import current_user
import urllib2, json

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
@register_menu(blueprint, 'main.instruments', _('Instruments'), order=2)
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
        'instruments': None,
    }

    if request.method == 'POST' and form.validate():
        # Map form
        data = form.data
        # Extract access_groups from Instrument data
        access_groups = data['access_groups']
        del data['access_groups']

        i = Instrument(user_id=uid, **data)
        #db.session.add(i)
        db.session.commit()
        userInfo = getUserInfoByPortalUser(current_user['nickname'])
        userInfoJson = json.loads(userInfo)
        if userInfoJson['databaseUser']:
            instrument = createInstrument(i.name, i.embargo_date, i.access_right, i.user_id, i.license, i.conditions, userInfoJson['databaseUser'], current_user['nickname'])
            jsonInstrument = json.loads(instrument)
            if (jsonInstrument['idInstrument']) >= 0:
                i.id = int(jsonInstrument['idInstrument'])
                flash("Instrument was successfully created.", category='success')
                return redirect(url_for('.show', instrument_id=i.id))
            else:
                flash("There was an error. Please, contact with the Lifewatch site administrator.", category='error')
        else:
            flash("The database user doesn't exist. Please update your profile before registering an instrument.", category='error')

    return render_template("instruments/new.html", **ctx)
        #i.save_collection()
        #i.save_group()


@blueprint.route('/<int:instrument_id>/show/', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.show', 'Show')
@wash_arguments({'page': (int, 1)})
def show(instrument_id, page):
    instrument = Instrument.query.get_or_404(instrument_id)

    instrument.get_access_right(instrument.access_right)

    tabs = {
        'public': {
            'template': 'instruments/show.html',
            'q': {'public': True},
        }
    }

    try:
        tab_info = tabs['public']
    except KeyError:
        abort(404)
    query_opts = tab_info.get('q', {})
    records = instrument.get_instrument_records(**query_opts)
    page = max(page, 1)
    per_page = cfg.get('RECORDS_IN_INSTRUMENTS_DISPLAYED_PER_PAGE', 5)
    records = records.paginate(page, per_page=per_page)

    template = tab_info.get('template')
    current_app.logger.debug("TEMPLATE: %s" % template)

    ctx = dict(
        instrument=instrument,
        records=records,
        format_record=format_record,
        page=page,
        per_page=per_page,
    )

    return render_template(template, **ctx)