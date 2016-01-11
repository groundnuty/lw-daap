from __future__ import absolute_import

from flask import abort, Blueprint, current_app, flash, jsonify, \
    render_template, request, redirect, url_for, make_response
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu

from invenio.base.i18n import _
from invenio.base.globals import cfg
from invenio.ext.sslify import ssl_required
from invenio.base.decorators import wash_arguments
from invenio.ext.sqlalchemy import db
from invenio.modules.formatter import format_record

from lw_daap.ext.login import login_required
from .service_utils import createInstrument, getFilteredInstrumentsByIdUser, addPermissionGroup, findInstrumentByName, \
    getPaginatedInstrumentsByIdUser, getCountInstrumentsByIdUser, getDBPublicUser, getDBPublicPass

from lw_daap.modules.profile.service_utils import getUserInfoByPortalUser
from lw_daap.modules.profile.models import UserProfile

from flask_login import current_user
import urllib2, json

from lw_daap.modules.instruments.models import Instrument
from lw_daap.modules.instruments.forms import SearchForm, InstrumentForm
from lw_daap.modules.instruments.pagination import Pagination

from werkzeug import MultiDict
from array import *

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
    page = max(page, 1)
    per_page = cfg.get('INSTRUMENTS_DISPLAYED_PER_PAGE', 9)

    instruments = getPaginatedInstrumentsByIdUser(current_user['id'],p, page, per_page)
    count = getCountInstrumentsByIdUser(current_user['id'],p)
    instruments_json = json.loads(instruments)

    form = SearchForm()

    my_array = [None] * 0
    for instrument in instruments_json:
       i = Instrument.from_json(instrument)
       my_array.append(i)

    pagination = Pagination(page, per_page, count)

    ctx = dict(
        instruments=my_array,
        form=form,
        page=page,
        per_page=per_page,
        pagination = pagination,
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
        data = form.data

        # Extract access_groups from Instrument data
        access_groups = data['access_groups']
        del data['access_groups']

        # Depends on the access right selected, clean some instrument fields
        i = Instrument(user_id=uid, **data)
        if i.access_right == "open":
            i.access_conditions = ""
            i.embargo_date = ""
        elif i.access_right == "embargoed":
            i.access_conditions = ""
        elif i.access_right == "restricted":
            i.embargo_date = ""
            i.license = ""
        else:
            i.access_conditions = ""
            i.embargo_date = ""
            i.license = ""

        db.session.commit()

        # Check if logged user has configured the profile BD fields
        userInfo = getUserInfoByPortalUser(current_user['nickname'])
        userInfoJson = json.loads(userInfo)
        if userInfoJson['databaseUser']:
            # If already exists an instrument with the chosen name: show an error message
            # Else: Save instrument data
            try:
                instrumentWithSameName = findInstrumentByName(i.name)
                flash("Already exists an instrument with the same name. Please choose another name.", category='error')
            except Exception as e:
                instrument = createInstrument(i.name, i.embargo_date, i.access_right, i.user_id, i.license, i.access_conditions, userInfoJson['databaseUser'], current_user['nickname'])
                jsonInstrument = json.loads(instrument)
                if (jsonInstrument['idInstrument']) >= 0:
                    i.id = int(jsonInstrument['idInstrument'])
                    if i.access_right == 'restricted':
                        for group in access_groups:
                            try:
                                addPermissionGroup(i.name, group['identifier'])
                            except Exception as e:
                                flash("There was an error. Please, contact with the Lifewatch site administrator.", category='error')
                    flash("Instrument was successfully created.", category='success')
                    return redirect(url_for('.show', instrument_id=i.id))
                else:
                    flash("There was an error. Please, contact with the Lifewatch site administrator.", category='error')
        else:
            flash("The database user doesn't exist. Please update your profile before registering an instrument.", category='error')


    return render_template("instruments/new.html", **ctx)


@blueprint.route('/<int:instrument_id>/show/', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.show', 'Show')
@wash_arguments({'page': (int, 1)})
def show(instrument_id, page):
    instrument = Instrument.query.get_or_404(instrument_id)

    dbuser = getDBPublicUser(instrument_id)
    dbpass = getDBPublicUser(instrument_id)
    tablename = "INST_CONTENT_" + instrument.name

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

    ctx = dict(
        instrument=instrument,
        records=records,
        tablename=tablename.upper(),
        dbuser=dbuser,
        dbpass=dbpass,
        format_record=format_record,
        page=page,
        per_page=per_page,
    )

    return render_template(template, **ctx)

@blueprint.route('/save/', methods=['POST', 'GET'])
@login_required
def save():
    is_submit = request.args.get('submit') == '1'
    is_complete_form = request.args.get('all') == '1'


    if request.method != 'POST':
        abort(400)

    data = request.json or MultiDict({})

    if 'access_groups' in data:
        del data['access_groups']
    uid = current_user.get_id()

    instrument = Instrument(user_id=uid, **data)
    dummy_form, validated, result = instrument.process(
        data, complete_form=is_complete_form or is_submit
    )

    # if validated and is_submit:
    #     instrument.complete()

    try:
        return jsonify(result)
    except TypeError:
        return jsonify(None)



@blueprint.route(
    '/save/<field_name>/',
    methods=['GET', 'POST'])
@login_required
def autocomplete(field_name=None):
    """Auto-complete a form field."""
    term = request.args.get('term')  # value
    limit = request.args.get('limit', 50, type=int)

    form = InstrumentForm(request.values, crsf_enabled=False)
    result = form.autocomplete(field_name, term, limit=limit)
    result = result if result is not None else []

    # jsonify doesn't return lists as top-level items.
    resp = make_response(
        json.dumps(result, indent=None if request.is_xhr else 2)
    )
    resp.mimetype = "application/json"
    return resp
