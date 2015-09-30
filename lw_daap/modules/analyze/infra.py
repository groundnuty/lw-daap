from flask_login import current_user
import humanize
from dateutil.parser import parse
from datetime import datetime
import pytz

import novaclient
import novaclient.auth_plugin
import novaclient.client

from .utils import get_requirements

def get_client():
    username = password = None
    # FIXME XXX hardcoded!
    tenant = "VO:fedcloud.egi.eu"
    url = 'https://keystone.ifca.es:5000/v2.0'
    version = 2
    auth_system = "voms"
    novaclient.auth_plugin.discover_auth_systems()
    auth_plugin = novaclient.auth_plugin.load_plugin(auth_system)
    client =  novaclient.client.Client(version, username, password,
                                        tenant, url,
                                        auth_plugin=auth_plugin,
                                        auth_system=auth_system, insecure=True)    
    return client
    

def launch_vm(name, image, flavor, app_env=''):
    client = get_client()
    s = client.servers.create(name, image=image,
                              flavor=flavor, meta={'lwdaap_vm': '',
                                                   'app_env': app_env})
    return s 


def list_vms():
    vms = []
    try:
        client = get_client()
        reqs = get_requirements()
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        for s in client.servers.list():
            addresses = []
            for t in s.addresses.values():
                for addr in t:
                    addresses.append(addr['addr'])
            v = {'name': s.name,
                 'status': s.status,
                 'size': reqs['flavors'].get(s.flavor['id'], {}).get('title'),
                 'image': reqs['images'].get(s.image['id'], {}).get('title'),
                 'created': humanize.naturaltime(now - parse(s.created)),
                 'addresses': addresses}
            vms.append(v)
    except Exception:
        pass
    return vms
