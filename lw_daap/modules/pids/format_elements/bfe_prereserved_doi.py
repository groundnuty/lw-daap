from __future__ import absolute_import

from ..utils import build_doi

def format_element(bfo, record=None):
    return build_doi(int(record['recid'])) 

def escape_values(bfo):
    return 0
