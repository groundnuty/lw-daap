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

"""
Contextualization
"""

from base64 import b64encode
import yaml

from invenio.base.globals import cfg
from invenio.ext.template import render_template_to_string


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
                "shell": "/bin/bash",
            },
        ]


def jupyter_context(app_env, ssh_key, context):
    jupyter_script = b64encode(
        # nothing to pass to the template?
        render_template_to_string('analyze/jupyter.sh', app_env=app_env)
    )
    jupyter_script_path = '/usr/local/bin/start-jupyter.sh'
    context['write_files'].append({
        'encoding': 'b64',
        'content': jupyter_script,
        'permissions': '755',
        'path': jupyter_script_path,
    })
    context['runcmd'].append([jupyter_script_path])


def record_context(recid, context):
    context['runcmd'].append(['/usr/bin/touch', '/tmp/comefrom%s' % recid])


CONTEXT_MAP = {
    'ssh': ssh_context,
    'jupyter-python': jupyter_context,
    'jupyter-r': jupyter_context,
}


def build_user_data(app_env, ssh_key=None, recid=None):
    context = nato_context()
    app_env_context = CONTEXT_MAP.get(app_env, None)
    if app_env_context:
        app_env_context(app_env, ssh_key, context)
    if recid:
        record_context(recid, context)

    return '\n'.join(['#cloud-config',
                      yaml.safe_dump(context,
                                     default_flow_style=False)])
