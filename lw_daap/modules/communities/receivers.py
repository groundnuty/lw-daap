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

from flask import current_app
from flask.ext.cache import make_template_fragment_key


def make_public_restricted(sender, collection=None, provisional=False, **extra):
    """
    set permissions on the public part of the collection so it can be 
    viewed by anyone. This is to allow records being in more than one community
    but only curated in some to be globally available
    """
    from invenio.modules.access.models import (AccACTION, AccARGUMENT,
        AccAuthorization, AccROLE)
    from invenio.ext.sqlalchemy import db

    if provisional:
        return  # provisional has proper rights already set
    # Role: anyuser
    role = AccROLE.query.filter_by(name='anyuser').first()

    # Argument
    fields = dict(keyword='collection', value=collection.name)
    arg = AccARGUMENT.query.filter_by(**fields).first()
    if not arg:
        arg = AccARGUMENT(**fields)
        db.session.add(arg)

    # Action
    action = AccACTION.query.filter_by(name='viewrestrcoll').first()

    # Authorization
    auth = AccAuthorization.query.filter_by(role=role, action=action,
                                            argument=arg).first()
    if not auth:
        auth = AccAuthorization(role=role, action=action, argument=arg,
                                argumentlistid=1)
    db.session.commit()


def invalidate_jinja2_cache(sender, collection=None, lang=None, **extra):
    """
    Invalidate collection cache
    """
    from invenio.ext.cache import cache
    if lang is None:
        lang = current_app.config['CFG_SITE_LANG']
    cache.delete(make_template_fragment_key(collection.name, vary_on=[lang]))


def pre_curation_reject_listener(sender, action=None, recid=None,
                                 pretend=None):
    """
    Pre-curation reject listener that will add 'spam' collection identifier
    if a record is rejected.
    """
    if sender.id == "zenodo" and action == "reject":
        # Overrides all other collections identifiers
        return {'correct': [], 'replace': ['SPAM']}
    else:
        return None


def post_curation_reject_listener(sender, action=None, recid=None, record=None,
                                  pretend=None):
    """
    Post-curation reject listener that will inactive an already minted
    DOI for a rejected record.
    """
    if sender.id == "zenodo" and action == "reject" and not pretend:
        from invenio.modules.pidstore.tasks import datacite_delete
        datacite_delete.delay(recid)
