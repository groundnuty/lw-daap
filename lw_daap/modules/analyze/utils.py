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

