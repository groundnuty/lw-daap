from __future__ import absolute_import

from flask import url_for 
from flask_login import current_user

from invenio.ext.cache import cache

from ..utils import build_doi, get_cache_key


def format_element(bfo, recid=None):
    key = get_cache_key(recid)
    cache_action = cache.get(key)
    return cache_action

def escape_values(bfo):
    return 0
