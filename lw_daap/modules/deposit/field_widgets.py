"""Implement custom field widgets."""

from wtforms.widgets import HTMLString
from invenio.ext.template import render_template_to_string

class SPAUploadWidget(object):

    """SPAUpload widget implementation."""

    def __init__(self, template=None):
        """Initialize widget with custom template."""
        self.template = template or "deposit/widget_spaupload.html"

    def __call__(self, field, **kwargs):
        """Render SPAUpload widget."""
        field_id = kwargs.pop('id', field.id)
        kwargs['class'] = u'spaupload'

        return HTMLString(
            render_template_to_string(
                self.template,
                field=field,
                field_id=field_id,
                **kwargs
            )
        )

spaupload_widget = SPAUploadWidget()
