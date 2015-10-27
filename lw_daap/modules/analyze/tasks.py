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

""" Analysis tasks """

from __future__ import absolute_import

import os
import stat
import subprocess
from tempfile import NamedTemporaryFile

from celery.task.base import PeriodicTask
from celery.utils.log import get_task_logger

from invenio.base.globals import cfg

from .infra import get_client, kill_old_vms


logger = get_task_logger(__name__)


class ProxyRenewalTask(PeriodicTask):
    """
    Renews the portal proxy every 11 hours
    """
    run_every = cfg['CFG_LWDAAP_ROBOT_RENEWAL_PERIOD']

    def run(self, *args, **kwargs):
        logger.info("Renewing proxy")
        with NamedTemporaryFile(mode='rw') as new_proxy:
            cmd = ['voms-proxy-init',
                   '--out', new_proxy.name,
                   '-rfc'
                  ]
            vo = cfg.get('CFG_DELEGATION_VO')
            if vo:
                cmd.extend(['--voms', vo]) 
            proc = subprocess.Popen(cmd, shell=False,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            logger.debug("CMD %s", ' '.join(cmd))
            out = ''.join([l for l in proc.stdout])
            logger.debug("OUTPUT: %s", out)
            proc.wait()
            if proc.returncode != 0:
                # and not _check_proxy_validity(new_proxy):
                msg = "Proxy generation failed (%d): %s" % (proc.returncode, out)
                logger.error(msg)
                raise self.retry(Exception(msg))
            # dump new proxy to proper location
            # XXX should this file be locked somehow?
            with open(cfg.get('CFG_LWDAAP_ROBOT_PROXY'), 'w+') as f:
                f.write(new_proxy.read())
                f.flush()
            os.chmod(cfg.get('CFG_LWDAAP_ROBOT_PROXY'),
                     stat.S_IRUSR | stat.S_IWUSR)


class VMKiller(PeriodicTask):
    """
    Kills old VMs regardless of their activity
    """
    run_every = cfg['CFG_LWDAAP_VMKILLER_PERIOD']

    def run(self, *args, **kwargs):
        cli = get_client()
        kill_old_vms(cli, cfg['CFG_LWDAAP_VMKILLER_MAXLIFE'])
