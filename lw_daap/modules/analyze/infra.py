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

from base64 import b64encode
from datetime import datetime
from itertools import chain
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
import yaml


from invenio.base.globals import cfg
from invenio.ext.template import render_template_to_string

from .utils import get_requirements


def _vm_mapper():
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    reqs = get_requirements()

    def _mapper(vm):
        created = now - parse(vm.created)
        return {
            'id': vm.id,
            'name': vm.name,
            'status': vm.status,
            'size': reqs['flavors'].get(vm.flavor['id'], {}).get('title'),
            'image': reqs['images'].get(vm.image['id'], {}).get('title'),
            'created': humanize.naturaltime(created),
            'seconds': created.seconds,
            'metadata': vm.metadata,
        }
    return _mapper

def _vm_filter(user_id, daap_user=None):
    def _filter(vm):
        return (vm.user_id == user_id and
                vm.metadata.get('lwdaap_vm', None) is not None and
                # XXX
                # ONLY THIS USER VMS!!!
                vm.metadata.get('user', None) == daap_user)
    return _filter


def _get_user_id(client):
    catalog = client.client.service_catalog.catalog
    return catalog['access']['user']['id']


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


def nato_context():
    context_script = b64encode(
        render_template_to_string('analyze/etcd-updater.sh',
                                  etcd_url=cfg.get('CFG_ANALYZE_ETCD_URL'),
                                  ttl=600,
                                  root=cfg.get('CFG_ANALYZE_NODES_KEY'))
    )
    context_script_path = '/usr/local/bin/etcd-updater.sh'
    crontab = b64encode(
        render_template_to_string('analyze/etcd_updater_cron',
                                  context_script_path=context_script_path)
    )
    return {
        'write_files': [
            {
                'encoding': 'b64',
                'content': context_script,
                'permissions': '755',
                'path': context_script_path,
            },
            {
                'encoding': 'b64',
                'content': crontab,
                'permissions': '755',
                'path': '/etc/cron.d/etcd_updater'
            },
        ],
        # run it as soon as the VM is booted
        'runcmd': [
            [context_script_path],
        ],
    }


def ssh_context(app_env, ssh_key, context):
    if ssh_key:
        context['users'] = [
            "default",
            {
                "name": "lw",
                "sudo": "ALL=(ALL) NOPASSWD:ALL",
                "ssh-import-id": None,
                "lock-passwd": True,
                "ssh-authorized-keys": [ssh_key],
            },
        ]


def jupyter_context(app_env, ssh_key, context):
    jupyter_script = b64encode(
        # nothing to pass to the template?
        render_template_to_string('analyze/jupyter.sh')
    )
    jupyter_script_path = '/usr/local/bin/start-jupyter.sh'
    context['write_files'].append({
        'encoding': 'b64',
        'content': jupyter_script,
        'permissions': '755',
        'path': jupyter_script_path,
    })
    context['runcmd'].append([jupyter_script_path])


CONTEXT_MAP = {
    'ssh': ssh_context,
    'jupyter-python': jupyter_context,
    'jupyter-r': jupyter_context,
}


def launch_vm(client, name, image, flavor, app_env='', ssh_key=None):
    context = nato_context()
    app_env_context = CONTEXT_MAP.get(app_env, None)
    if app_env_context:
        app_env_context(app_env, ssh_key, context)

    userdata='\n'.join(['#cloud-config',
                        yaml.safe_dump(context,
                                       default_flow_style=False)])
    current_app.logger.debug(userdata)
    try:
        s = client.servers.create(name, image=image,
                                  flavor=flavor, meta={'lwdaap_vm': '',
                                                       'app_env': app_env},
                                  userdata=userdata,
                                  key_name='lw_wp')
    except Exception, e:
        current_app.logger.debug("PUM!, %s" % e)
    return s

def terminate_vm(client, vm_id):
    try:
        client.servers.delete(vm_id)
    except Exception, e:
        current_app.logger.debug("PUM!, %s" % e)


def list_vms(client):
    user_id = _get_user_id(client)
    return  map(_vm_mapper(), filter(_vm_filter(user_id), client.servers.list()))


def get_vm(client, vm_id):
    try:
        user_id = _get_user_id(client)
        vm = client.servers.get(vm_id)
        if _vm_filter(user_id)(vm):
            return _vm_mapper()(vm)
        return None
    except Exception, e:
        current_app.logger.debug("PUM!, %s" % e)
        return None


# XXX this needs some refactoring
def get_vm_connection(client, vm_id):
    vm = get_vm(client, vm_id)
    if not vm:
        return dict(
            error=True,
            msg='Instante is not known to the system'
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
        app_env = vm.get('metadata', {}).get('app_env')
        if app_env == 'ssh':
            d['user'] = 'lw'
            return dict(
                error=False,
                msg=('<p>You can connect via SSH to %(ip)s, port %(port)s with '
                     'user "%(user)s":</p>'
                     '<p>ssh -i &lt;your ssh key&gt; -p %(port)s '
                     '%(user)s@%(ip)s</p>') % d
            )
        elif app_env == 'jupyter-python':
            return dict(
                error=False,
                msg='<p>You can connect to <a href="%(http)s">jupyter</a>.' % d
            )

        else:
            return dict(
                error=True,
                msg='Uknown application environment "%s".' % app_env
            )
    except etcd.EtcdKeyNotFound:
        return dict(
            error=True,
            msg='Connection details are still not available.'
        )
    except etcd.EtcdException, e:
        return dict(
            error=True,
            msg='Unable to get connection details (%s).' % e
        )
