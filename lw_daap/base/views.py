
from flask import Blueprint, render_template
from flask_menu import register_menu
from flask_breadcrumbs import register_breadcrumb

from invenio.base.i18n import _


blueprint = Blueprint('lw_daap', __name__, url_prefix='',
                      template_folder='templates', static_folder='static')


@blueprint.route('/about', methods=['GET', ])
@register_menu(blueprint, 'main.about', _('About'), order=4)
@register_breadcrumb(blueprint, 'breadcrumbs.about', _("About"))
def about():
    return render_template('lw_daap/about.html')
