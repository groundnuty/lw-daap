
from datetime import datetime
from itertools import chain
from tempfile import NamedTemporaryFile

from dateutil.parser import parse
from flask import current_app
from flask_login import current_user
import novaclient
import novaclient.auth_plugin
import novaclient.client
import humanize
import pytz


from invenio.base.globals import cfg

from .utils import get_requirements

def get_client(user_proxy):
    username = password = None
    tenant = cfg.get('CFG_OPENSTACK_TENANT', '')
    url = cfg.get('CFG_OPENSTACK_AUTH_URL', '')
    version = 2
    auth_system = "voms"
    novaclient.auth_plugin.discover_auth_systems()
    auth_plugin = novaclient.auth_plugin.load_plugin(auth_system)
    with NamedTemporaryFile() as proxy_file:
        proxy_file.write(user_proxy)
        proxy_file.flush()
        auth_plugin.opts["x509_user_proxy"] = proxy_file.name
        client =  novaclient.client.Client(version, username, password,
                                           tenant, url,
                                           auth_plugin=auth_plugin,
                                           auth_system=auth_system,
                                           # XXX REMOVE THIS ASAP!
                                           insecure=True)
        client.authenticate()
    return client


def launch_vm(client, name, image, flavor, app_env=''):
    try:
        s = client.servers.create(name, image=image,
                                  flavor=flavor, meta={'lwdaap_vm': '',
                                                       'app_env': app_env})
    except Exception, e:
        current_app.logger.debug("PUM!, %s" % e)
    return s

def terminate_vm(client, vm_id):
    try:
        client.servers.delete(vm_id)
    except Exception, e:
        current_app.logger.debug("PUM!, %s" % e)


def list_vms(client):
    reqs = get_requirements()
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    catalog = client.client.service_catalog.catalog
    user_id = catalog['access']['user']['id']

    def _filter(vm):
        return (vm.user_id == user_id and
                vm.metadata.get('lwdaap_vm', None) is not None)

    def _mapper(vm):
        addrs = [addr['addr']
                 for addr in chain.from_iterable(vm.addresses.values())]
        created = now - parse(vm.created)
        return {
            'id': vm.id,
            'name': vm.name,
            'status': vm.status,
            'size': reqs['flavors'].get(vm.flavor['id'], {}).get('title'),
            'image': reqs['images'].get(vm.image['id'], {}).get('title'),
            'created': humanize.naturaltime(created),
            'seconds': created.seconds,
            'addresses': addrs,
        }
    return  map(_mapper, filter(_filter, client.servers.list()))
