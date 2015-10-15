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

from collections import OrderedDict
import json
from invenio.modules.knowledge.api import get_kb_mappings

def get_requirements(): 
    reqs = dict(
        flavors=OrderedDict(),
        images=OrderedDict(),
        app_envs=OrderedDict(),
    )
    for mapping in get_kb_mappings('requirements'):
        v = json.loads(mapping['value'])
        if v.get('domain_flavor', False):
            if v['flavor-id']:
                reqs['flavors'][v['flavor-id']] = v
        elif v.get('domain_os', False):
            if v['image-id']:
                reqs['images'][v['image-id']] = v
        elif v.get('domain_app_env', False):
            if v['app-id']:
                reqs['app_envs'][v['id']] = v
    return reqs

