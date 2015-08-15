
from flask import Blueprint
from flask_menu import register_menu
from flask_breadcrumbs import register_breadcrumb

from invenio.base.i18n import _


blueprint = Blueprint('lw_daap', __name__, url_prefix='',
                      template_folder='templates', static_folder='static')


#@blueprint.route('/communtities', methods=['GET', 'POST'])
#@register_menu(blueprint, 'main.communities', _('Communities'), order=1)
#@register_breadcrumb(blueprint, '.', _('Home'))
#def communities():
#  return "Hola"
 
