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

## This file is part of Zenodo.
## Copyright (C) 2012, 2013, 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from flask import Blueprint

from invenio.base.signals import webcoll_after_webpage_cache_update
from invenio.modules.communities.signals import after_save_collection, \
    pre_curation, post_curation

from .receivers import invalidate_jinja2_cache, pre_curation_reject_listener, \
    post_curation_reject_listener, make_public_restricted, update_provisional_query


blueprint = Blueprint(
    'lwdaap_communities',
    __name__,
    static_folder="static",
    template_folder="templates",
)


@blueprint.before_app_first_request
def register_receivers():
    """
    Setup signal receivers for communities module.
    """
    webcoll_after_webpage_cache_update.connect(invalidate_jinja2_cache)
    after_save_collection.connect(invalidate_jinja2_cache)
    after_save_collection.connect(make_public_restricted)
    after_save_collection.connect(update_provisional_query)
    pre_curation.connect(pre_curation_reject_listener)
    post_curation.connect(post_curation_reject_listener)
