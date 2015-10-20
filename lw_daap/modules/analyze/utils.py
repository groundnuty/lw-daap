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
    domains_to_reqs = {
        # kb_mappings has 'domain-xxx' = True for each type of requirement
        # the value of the key is a tuple: first the name of the OrderedDict
        # to use, seconde
        'domain_flavor': {'reqs': 'flavors', 'id': 'flavor-id'},
        'domain_os': {'reqs': 'images', 'id': 'image-id'},
        'domain_app_env': {'reqs': 'app_envs', 'id': 'app-id'},
    }
    for mapping in get_kb_mappings('requirements'):
        v = json.loads(mapping['value'])
        for d, r in domains_to_reqs.items():
            if v.get(d, False):
                if v.get(r['id']):
                    reqs[r['reqs']][v['id']] = v
    return reqs

