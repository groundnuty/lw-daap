
from flask import Blueprint

blueprint = Blueprint('ebd_base', __name__, url_prefix='',
                      template_folder='templates', static_folder='static')
