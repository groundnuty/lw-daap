## aeonium ######
## Copied from zenodo/legacy/utils/zenodoutils.py

def create_doi(recid=None):
    if recid == None:
        recid = 12345
    return {'doi': '%s/lw_daap.%s' % ('10.5072', recid),
       'recid': recid }

def filter_empty_helper(keys=None):
    """ Remove empty elements from a list"""
    def _inner(elem):
        if isinstance(elem, dict):
            for k, v in elem.items():
                if (keys is None or k in keys) and v:
                    return True
            return False
        else:
            return bool(elem)
    return _inner
