import json

from flask import Blueprint, current_app, render_template
from flask_menu import register_menu

from invenio.modules.knowledge.api import get_kb_mappings


blueprint = Blueprint(
    'lwdaap_analyze',
    __name__,
    url_prefix='/analyze',
    template_folder='templates',
    static_folder='static',
)

def get_requirements(): 
    m = get_kb_mappings('requirements')
    return [json.loads(k['value']) for k in m] 

def find_requirement(reqs, key, req_id):
    r = next((x for x in reqs if x.get(key, None) == req_id), {})
    return r.get('title', 'unknown')


@blueprint.route('/')
@register_menu(blueprint, 'main.analyze', 'Analyze', order=3)
def index():
    ctx = dict(
        vms=[]
    )
    return render_template('analyze/index.html', **ctx)

