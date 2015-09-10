
from __future__ import absolute_import

from flask import Blueprint, abort, current_app
from flask_login import current_user, login_required

from invenio.ext.cache import cache
from invenio.legacy.bibrecord import record_add_field
from invenio.modules.pidstore.models import PersistentIdentifier
from invenio.modules.records.api import get_record

from .utils import build_doi

blueprint = Blueprint(
    'lwdaap_pids',
    __name__,
    url_prefix='/pids',
    static_folder="static",
    template_folder="templates",
)

DOI_PID_TYPE = 'doi'


def add_doi(recid, doi):
    rec = {}
    record_add_field(rec, '001', controlfield_value=str(recid))
    pid_fields = [('a', doi), ('2', 'DOI')]
    record_add_field(rec, tag='024', ind1='7', subfields=pid_fields)

    from invenio.legacy.bibupload.utils import bibupload_record
    bibupload_record(record=rec, file_prefix='doi', mode='-c',
                     opts=[], alias="doi")
    return rec

@blueprint.route('mint/<int:recid>', methods=['GET', 'POST'])
@login_required
def mint_doi(recid):
    """ mint a PID for the record """
    uid = current_user.get_id()
    record = get_record(recid)

    # do only allow to mint to the owner
    if uid != int(record.get('owner', {}).get('id', -1)):
        abort(401)

    # don't try to mint a doi if the record already has one
    if record.get('doi', None) is not None:
        abort(400) 

    # crazy invenio stuff, cache actions so they dont get duplicated
    key = "pid_mint:%s" % recid
    cache_action = cache.get(key)
    if cache_action:
        pass
        #return "ONGOING!"

    doi = build_doi(recid)
    # Set 5 min cache to allow bibupload/bibreformat to finish
    cache.set(key, doi, timeout=5*60)
    record[DOI_PID_TYPE] = doi 

    current_app.logger.info("Registering pid %s" % doi)
    pid = PersistentIdentifier.create(DOI_PID_TYPE, doi)
    if pid is None:
        pid = PersistentIdentifier.get(DOI_PID_TYPE, doi)

    try:
        pid.assign('rec', recid) 
    except Exception:
        register_exception(alert_admin=True)

    r = add_doi(recid, doi)

    return "%s" % record['doi']
