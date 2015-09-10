
def build_doi(recid):
   return '10.5281/lwdaap.%s' % recid 

def get_cache_key(recid):
    return 'pid_mint:%s' % recid
