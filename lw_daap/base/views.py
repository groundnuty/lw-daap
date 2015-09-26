
from flask import Blueprint, render_template
from flask_menu import register_menu
from flask_breadcrumbs import register_breadcrumb

from invenio.base.i18n import _
from invenio.base.signals import pre_template_render
from invenio.ext.template. \
    context_processor import register_template_context_processor


blueprint = Blueprint('lw_daap', __name__, url_prefix='',
                      template_folder='templates', static_folder='static')


@blueprint.route('/about', methods=['GET', ])
@register_breadcrumb(blueprint, 'breadcrumbs.about', _("About"))
def about():
    return render_template('lw_daap/about.html')


def add_record_variables(sender, **kwargs):
    """Add a variable 'daap_files' and 'daap_record' into record templates."""
    if 'recid' not in kwargs:
        return

    @register_template_context_processor
    def _add_record_variables():
        from invenio.legacy.bibdocfile.api import BibRecDocs
        from invenio.modules.records.api import get_record

        ctx = dict(
            daap_files=[f for f in BibRecDocs(
                kwargs['recid'], human_readable=True
            ).list_latest_files(
                list_hidden=False
            ) if not f.is_icon()],
            # this updates the DB, but avoids ugly caching
            daap_record=get_record(kwargs['recid'], True)
        )

        return ctx


@blueprint.before_app_first_request
def register_receivers():
    # Add template context processor to record request, that will add a files
    # variable into the template context
    pre_template_render.connect(add_record_variables, 'record.metadata')
    pre_template_render.connect(add_record_variables, 'record.files')
    pre_template_render.connect(add_record_variables, 'record.usage')
