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

from datetime import timedelta
import os

import invenio.config as cfg

#
# Configuration for OpenStack
#

CFG_OPENSTACK_AUTH_URL = 'https://keystone.ifca.es:5000/v2.0'
CFG_OPENSTACK_TENANT = "VO:vo.lifewatch.eu"

#
# Configuration for Robot Certificate
#
CFG_LWDAAP_ROBOT_PROXY = os.path.join(cfg.CFG_PREFIX, 'var', 'robot_proxy')
CFG_LWDAAP_ROBOT_RENEWAL_PERIOD = timedelta(hours=10)

#
# VM Killer
#
CFG_LWDAAP_VMKILLER_PERIOD = timedelta(minutes=30)
CFG_LWDAAP_VMKILLER_MAXLIFE = timedelta(hours=5)

#
# Configuration of the etcd host
#
CFG_ANALYZE_ETCD_URL = 'http://193.146.75.165:4001'
CFG_ANALYZE_ETCD_PORT = 4001

CFG_ANALYZE_MAPPINGS_KEY = 'mappings'
CFG_ANALYZE_NODES_KEY = 'nodes'
