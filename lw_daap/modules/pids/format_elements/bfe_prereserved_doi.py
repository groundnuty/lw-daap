from __future__ import absolute_import

from ..utils import build_doi

def format_element(bfo):
    return build_doi(bfo.recID)

def escape_values(bfo):
    return 0
