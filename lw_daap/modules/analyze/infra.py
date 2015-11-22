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

from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
from urlparse import urlsplit

from dateutil.parser import parse
import etcd
from flask import current_app
from flask_login import current_user
import novaclient.auth_plugin
import novaclient.client
import humanize
import pytz
import requests.exceptions

from invenio.base.globals import cfg

from .utils import get_requirements
from .context import build_user_data


class InfraException(Exception):
    pass

#
# global client
# probably needs some thinking
robot_client = None


def _make_client(proxy_file):
    username = password = None
    tenant = cfg.get('CFG_OPENSTACK_TENANT', '')
    url = cfg.get('CFG_OPENSTACK_AUTH_URL', '')
    version = 2
    auth_system = "voms"
    novaclient.auth_plugin.discover_auth_systems()
    auth_plugin = novaclient.auth_plugin.load_plugin(auth_system)
    auth_plugin.opts["x509_user_proxy"] = proxy_file
    client = novaclient.client.Client(version, username, password,
                                      tenant, url,
                                      auth_plugin=auth_plugin,
                                      auth_system=auth_system)
    try:
        client.authenticate()
    except requests.exceptions.RequestException as e:
        raise InfraException(e.message)
    return client


def _needs_new_client(client):
    if not client:
        return True
    catalog = client.client.service_catalog.catalog
    try:
        expires = parse(catalog['access']['token']['expires'])
    except KeyError:
        return True
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    if now - expires > timedelta(minutes=5):
        return True
    return False


def get_client(user_proxy=None):
    current_app.logger.debug("GET CLIENT")
    if not user_proxy:
        global robot_client
        if _needs_new_client(robot_client):
            robot_client = _make_client(cfg.get('CFG_LWDAAP_ROBOT_PROXY'))
        client = robot_client
    else:
        with NamedTemporaryFile() as proxy_file:
            proxy_file.write(user_proxy)
            proxy_file.flush()
            client = _make_client(proxy_file.name)
    return client


def _vm_mapper():
    """
    Maps VM information into a dictionary with the portal required fields
    """
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    reqs = get_requirements()
    flavors = {v['flavor-id']: v['title'] for v in reqs['flavors'].values()}
    images = {v['image-id']: v['title'] for v in reqs['images'].values()}

    def _mapper(vm):
        created = now - parse(vm.created)
        return {
            'id': vm.id,
            'name': vm.name,
            'status': vm.status,
            'size': flavors.get(vm.flavor['id']),
            'image': images.get(vm.image['id']),
            'created': humanize.naturaltime(created),
            'seconds': created.seconds,
            'user': vm.metadata.get('lwdaap_user'),
            'app_env': vm.metadata.get('app_env'),
        }
    return _mapper


def _lwdaap_vm_filter(user_id):
    """
    Filters out VMs not started by this module
    """
    def _filter(vm):
        return (vm.user_id == user_id and
                vm.metadata.get('lwdaap_vm', None) is not None)
    return _filter


def is_user_vm(vm, user_id):
    daap_user = '%s' % current_user.get_id()
    return (vm.user_id == user_id and
            vm.metadata.get('lwdaap_vm', None) is not None and
            vm.metadata.get('lwdaap_user') == daap_user)


def _get_user_id(client):
    catalog = client.client.service_catalog.catalog
    return catalog['access']['user']['id']


def build_vm_list(client):
    user_id = _get_user_id(client)
    vms = map(_vm_mapper(), filter(_lwdaap_vm_filter(user_id),
                                   client.servers.list()))
    return vms


def list_vms(client):
    daap_user = '%s' % current_user.get_id()
    return filter(lambda vm: vm['user'] == daap_user, build_vm_list(client))


def launch_vm(client, name, image, flavor,
              app_env=None, recid=None, ssh_key=None):
    current_vms = list_vms(client)
    if len(current_vms) >= cfg.get('CFG_LWDAAP_MAX_VMS'):
        msg = 'Maximum number of VMs per user reached!'
        raise InfraException(msg)
    userdata = build_user_data(app_env, ssh_key, recid)
    metadata = {'lwdaap_vm': '',
                'lwdaap_user': "%s" % current_user.get_id(),
                'app_env': app_env}
    try:
        # Robot Cert ('lw_wp' User Cert?)
        s = client.servers.create(name, image=image, flavor=flavor,
                                  meta=metadata,
                                  userdata=userdata,
                                  key_name='lwkey')
    except Exception as e:
        raise InfraException(e.message)
    return s


def terminate_vm(client, vm_id):
    try:
        client.servers.delete(vm_id)
    except Exception as e:
        raise InfraException(e.message)


def kill_old_vms(client, max_time):
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    for vm in build_vm_list(client):
        if now - parse(vm.created) > max_time:
            current_app.logger.info("KILLING VM with ID: %s", vm.id)
            # client.servers.delete(vm.id)


def get_vm(client, vm_id):
    try:
        user_id = _get_user_id(client)
        vm = client.servers.get(vm_id)
        if is_user_vm(vm, user_id):
            return _vm_mapper()(vm)
        return None
    except Exception as e:
        current_app.logger.debug("PUM!, %s" % e)
        return None


# XXX this needs some refactoring
def get_vm_connection(client, vm_id):
    vm = get_vm(client, vm_id)
    if not vm:
        return dict(
            error=True,
            msg='Instance is not known to the system'
        )
    if vm['status'] != 'ACTIVE':
        return dict(
            error=True,
            msg='Instance must be ACTIVE to get connected to it.'
        )

    u = urlsplit(cfg.get('CFG_ANALYZE_ETCD_URL'))
    netloc = u[1].split(':')
    if len(netloc) > 1:
        etcd_client = etcd.Client(host=netloc[0], port=int(netloc[1]))
    else:
        etcd_client = etcd.Client(host=netloc[0])

    vm_dir = '/'.join([cfg.get('CFG_ANALYZE_MAPPINGS_KEY', '/'), vm_id])
    try:
        r = etcd_client.read(vm_dir, recursive=True)
        d = {c.key.split('/')[-1]: c.value for c in r.children}
        app_env = vm.get('app_env')
        if app_env == 'ssh':
            d['user'] = 'lw'
            return dict(
                error=False,
                msg=('<p>You can connect via SSH to %(ip)s, '
                     'port %(port)s with '
                     'user "%(user)s":</p>'
                     '<p>ssh -i &lt;your ssh key&gt; -p %(port)s '
                     '%(user)s@%(ip)s</p>') % d
            )
        elif app_env in ['jupyter-python', 'jupyter-r']:
            return dict(
                error=False,
                msg=('<p>You can connect to <a href="%(http)s" '
                     'class="btn btn-info">jupyter</a>.') % d
            )
        else:
            return dict(
                error=True,
                msg='Unknown application environment "%s".' % app_env
            )
    except etcd.EtcdKeyNotFound:
        return dict(
            error=True,
            msg='Connection details are still not available.'
        )
    except etcd.EtcdException as e:
        return dict(
            error=True,
            msg='Unable to get connection details (%s).' % e
        )
