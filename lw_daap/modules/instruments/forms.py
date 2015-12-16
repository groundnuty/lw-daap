from __future__ import absolute_import

from invenio.base.i18n import _
from invenio.utils.forms import InvenioBaseForm, InvenioForm as Form

from wtforms import HiddenField, StringField, TextAreaField,\
    SelectMultipleField, validators

from lw_daap.modules.invenio_deposit import fields
from lw_daap.modules.deposit import fields as zfields
from lw_daap.modules.invenio_deposit.filter_utils import sanitize_html, \
    strip_string
from datetime import date
from invenio.config import CFG_DATACITE_DOI_PREFIX, CFG_SITE_NAME, \
    CFG_SITE_SUPPORT_EMAIL

from lw_daap.modules.invenio_deposit.validation_utils \
    import DOISyntaxValidator, invalid_doi_prefix_validator, list_length, \
    pid_validator, required_if, \
    unchangeable

from lw_daap.modules.invenio_deposit.field_widgets import CKEditorWidget, \
    ExtendedListWidget, ItemWidget, TagListWidget
from lw_daap.modules.deposit.forms import AccessGroupsForm
from invenio.utils.html import CFG_HTML_BUFFER_ALLOWED_TAG_WHITELIST

from lw_daap.modules.deposit.field_widgets import date_widget, DynamicHiddenListWidget

class SearchForm(Form):
    """Search Form."""
    p = StringField(
        validators=[validators.DataRequired()]
    )

class DeleteInstrumentForm(Form):
    delete = HiddenField(default='yes', validators=[validators.DataRequired()])

class InstrumentForm(Form):

    """Instrument Form."""

    field_sets = [
        ('Information', [
            'name', 'access_right', 'embargo_date'
            , 'license', 'conditions', 'access_groups'
        ], {'classes': 'in'}),
    ]

    field_placeholders = {
    }

    field_state_mapping = {
    }

    #
    # Methods
    #
    def get_field_icon(self, name):
        """Return field icon."""
        return self.field_icons.get(name, '')

    def get_field_by_name(self, name):
        """Return field by name."""
        try:
            return self._fields[name]
        except KeyError:
            return None

    def get_field_placeholder(self, name):
        """Return field placeholder."""
        return self.field_placeholders.get(name, "")

    def get_field_state_mapping(self, field):
        """Return field state mapping."""
        try:
            return self.field_state_mapping[field.short_name]
        except KeyError:
            return None

    def has_field_state_mapping(self, field):
        """Check if field has state mapping."""
        return field.short_name in self.field_state_mapping

    def has_autocomplete(self, field):
        """Check if filed has autocomplete."""
        return hasattr(field, 'autocomplete')

    def get_groups(self):
        """Get a list of the (group metadata, list of fields)-tuples.

        The last element of the list has no group metadata (i.e. None),
        and contains the list of fields not assigned to any group.
        """
        fields_included = set()
        field_groups = []

        if hasattr(self, 'groups'):
            for group in self.groups:
                group_obj = {
                    'name': group[0],
                    'meta': CFG_GROUPS_META.copy(),
                }

                fields = []
                for field_name in group[1]:
                    if field_name in ['-', ]:
                        fields.append(field_name)
                    else:
                        try:
                            fields.append(self[field_name])
                            fields_included.add(field_name)
                        except KeyError:
                            pass

                if len(group) == 3:
                    group_obj['meta'].update(group[2])

                field_groups.append((group_obj, fields))

        # Append missing fields not defined in groups
        rest_fields = []
        for field in self:
            if field.name not in fields_included:
                rest_fields.append(field)
        if rest_fields:
            field_groups.append((None, rest_fields))

        return field_groups

    field_icons = {
        'name': 'fa fa-md fa-fw',
        'embargo_date': 'fa fa-calendar fa-fw',
        'license': 'fa fa-certificate fa-fw',
        'access_conditions': 'fa fa-pencil fa-fw',
        'access_groups': 'fa fa-group fa-fw'
    }

    name = fields.TitleField(
        validators=[
            validators.DataRequired(),
            validators.Length(min=5),
        ],
        description='Required.',
        filters=[
            strip_string,
        ],
        export_key='instruments',
        icon='fa fa-md fa-fw',
    )
    access_right = zfields.AccessRightField(
        label="Access right",
        description="Required. Open access uploads have considerably higher "
        "visibility on %s." % CFG_SITE_NAME,
        default="open",
        validators=[validators.DataRequired()]
    )
    embargo_date = fields.Date(
        label=_('Embargo date'),
        icon='fa fa-calendar fa-fw',
        description='Required only for Embargoed Access uploads.'
        'The date your upload will be made publicly available '
        'in case it is under an embargo period from your publisher.',
        default=date.today(),
        validators=[
            required_if('access_right', ['embargoed']),
            validators.optional()
        ],
        widget=date_widget,
        widget_classes='input-small',
        hidden=True,
        disabled=True,
    )
    license = zfields.LicenseField(
        validators=[
            required_if('access_right', ['embargoed', 'open', ]),
            validators.DataRequired()
        ],
        default='cc-zero',
        domain_data=True,
        domain_content=True,
        domain_software=True,
        description='Required. The selected license applies to all of your '
        'files displayed in the bottom of the form. If you want to upload '
        'some files under a different license, please do so in two separate'
        ' uploads. If you think a license missing is in the list, please '
        'inform us at %s.' % CFG_SITE_SUPPORT_EMAIL,
        filters=[
            strip_string,
        ],
        placeholder="Start typing a license name or abbreviation...",
        icon='fa fa-certificate fa-fw',
    )
    conditions = fields.TextAreaField(
        label=_('Conditions'),
        icon='fa fa-pencil fa-fw',
        description='Specify the conditions under which you grant users '
        'access to the files in your upload. User requesting '
        'access will be asked to justify how they fulfil the '
        'conditions. Based on the justification, you decide '
        'who to grant/deny access. You are not allowed to '
        'charge users for granting access to data hosted on '
        'Dataset.',
        default="",
        validators=[
            required_if('access_right', ['restricted']),
            validators.optional()
        ],
        widget=CKEditorWidget(
            toolbar=[
                ['PasteText', 'PasteFromWord'],
                ['Bold', 'Italic', 'Strike', '-',
                 'Subscript', 'Superscript', ],
                ['NumberedList', 'BulletedList', 'Blockquote'],
                ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'RemoveFormat'],
                ['Mathjax', 'SpecialChar', 'ScientificChar'], ['Source'],
                ['Maximize'],
            ],
            disableNativeSpellChecker=False,
            extraPlugins='scientificchar,mathjax,blockquote',
            removePlugins='elementspath',
            removeButtons='',
            # Must be set, otherwise MathJax tries to include MathJax via the
            # http on CDN instead of https.
            mathJaxLib='https://cdn.mathjax.org/mathjax/latest/MathJax.js?'
            'config=TeX-AMS-MML_HTMLorMML'
        ),
        filters=[
            sanitize_html(allowed_tag_whitelist=(
                CFG_HTML_BUFFER_ALLOWED_TAG_WHITELIST + ('span',)
            )),
            strip_string,
        ],
        hidden=True,
        disabled=True,
    )

    access_groups = fields.DynamicFieldList(
        fields.FormField(
            AccessGroupsForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget()),
            description=("Optional. Specify the groups you "
                         "will grant the access"),
        ),
        validators=[
            # required_if('access_right', ['restricted']),
            validators.optional()
        ],
        label=_('Access groups'),
        description='Optional. Specify the groups you will grant the access.',
        default="",
        widget=TagListWidget(template="{{title}}"),
        widget_classes=' dynamic-field-list',
        icon='fa fa-group fa-fw',
        hidden=True,
        disabled=True,
    )

    """Instrument Upload Form."""
    #
    # Form configuration
    #
    _title = _('New instruments')
    _drafting = False   # enable and disable drafting

    #
    # Grouping of fields
    #
    groups = [
        ('<i class="fa fa-info"></i> Instrument information', [
            'instruments', 'access_right', 'embargo_date'
            , 'license', 'access_conditions', 'access_groups'
        ], {
            # 'classes': '',
            'indication': 'optional',
        }),
    ]

class EditInstrumentForm(InstrumentForm):
    pass

class IntegrateForm(Form):
    records = SelectMultipleField('records', coerce=int)
    integrate = HiddenField(default='no',
                            validators=[validators.DataRequired()])