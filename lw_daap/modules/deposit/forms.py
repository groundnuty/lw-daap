# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 CSIC.
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

import json
from datetime import date

import idutils
from flask import request
from jinja2 import Markup
from wtforms import FormField, validators, widgets
from wtforms.validators import ValidationError
from wtforms_components import DateRange

from invenio.base.globals import cfg
from invenio.base.i18n import _
from invenio.config import CFG_DATACITE_DOI_PREFIX, CFG_SITE_NAME, \
    CFG_SITE_SUPPORT_EMAIL
from lw_daap.modules.invenio_deposit import fields
from lw_daap.modules.invenio_deposit.autocomplete_utils import kb_autocomplete
from lw_daap.modules.invenio_deposit.field_widgets \
    import ButtonWidget, CKEditorWidget, ColumnInput, ExtendedListWidget, \
    ItemWidget, TagInput, TagListWidget, plupload_widget
from lw_daap.modules.invenio_deposit.filter_utils import sanitize_html, \
    strip_string
from lw_daap.modules.invenio_deposit.form import WebDepositForm
from lw_daap.modules.invenio_deposit.processor_utils import PidNormalize, \
    PidSchemeDetection, datacite_lookup, replace_field_data
from lw_daap.modules.invenio_deposit.validation_utils \
    import DOISyntaxValidator, invalid_doi_prefix_validator, list_length, \
    minted_doi_validator, not_required_if, pid_validator, required_if, \
    unchangeable
from invenio.modules.knowledge.api import get_kb_mapping
from invenio.utils.html import CFG_HTML_BUFFER_ALLOWED_TAG_WHITELIST

from lw_daap.modules.invenio_groups.models import Group

from . import fields as zfields
from .field_widgets import date_widget, DynamicHiddenListWidget
from .autocomplete import community_autocomplete, accessgroups_autocomplete, \
    inputrecords_autocomplete_dataset, inputrecords_autocomplete_software
from .validators import community_validator, project_acl_validator, \
    rel_record_validator
from .utils import create_doi, filter_empty_helper


__all__ = (
    'BasicForm',
    'DMPForm',
    'DatasetForm',
    'SoftwareForm',
    'AnalysisForm',
)

#
# Local processors
#
local_datacite_lookup = datacite_lookup(mapping=dict(
    get_titles='title',
    get_dates='publication_date',
    get_description='description',
))


#
# Local autocomplete mappers
#
def map_result(func, mapper):
    def inner(form, field, term, limit=50):
        prefix = form._prefix
        return map(
            lambda x: mapper(x, prefix),
            func(form, field, term, limit=limit)
        )
    return inner


def community_obj_value(key_name):
    from invenio.modules.communities.models import Community

    def _getter(field):
        if field.data:
            obj = Community.query.filter_by(id=field.data).first()
            if obj:
                return getattr(obj, key_name)
        return None
    return _getter


def accessgroups_obj_value(key_name):
    def _getter(field):
        if field.data:
            obj = Group.query.filter_by(id=field.data).first()
            if obj:
                return getattr(obj, key_name)
        return None
    return _getter


def inputrecords_obj_value():
    from invenio.modules.records.api import get_record

    def _getter(field):
        if field.data:
            try:
                obj = get_record(int(field.data))
            except ValueError:
                return field.data
            if obj:
                return "%s (record id: %s)" % (obj.get('title', None),
                                               field.data)
        return None
    return _getter


def authorform_mapper(obj, prefix):
    obj.update({
        'value': "%s: %s" % (obj['name'], obj['affiliation']),
        'fields': {
            '%sname' % prefix: obj['name'],
            '%saffiliation' % prefix: obj['affiliation'],
        }
    })
    return obj


#
# Subforms
#
class RelatedIdentifierForm(WebDepositForm):
    scheme = fields.StringField(
        label="",
        default='',
        widget_classes='',
        widget=widgets.HiddenInput(),
    )
    identifier = fields.StringField(
        label="",
        placeholder="e.g. 10.1234/foo.bar...",
        validators=[
            validators.optional(),
            pid_validator(),
        ],
        processors=[
            PidSchemeDetection(set_field='scheme'),
            PidNormalize(scheme_field='scheme'),
        ],
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-4"),
    )
    relation = fields.SelectField(
        label="",
        choices=[
            ('isCitedBy', 'cites this upload'),
            ('cites', 'is cited by this upload'),
            ('isSupplementTo', 'is supplemented by this upload'),
            ('isSupplementedBy', 'is a supplement to this upload'),
            ('isNewVersionOf', 'is previous version of this upload'),
            ('isPreviousVersionOf', 'is new version of this upload'),
            ('isPartOf', 'has this upload as part'),
            ('hasPart', 'is part of this upload'),
            ('isAnalyzedBy', 'is analyzed by this upload'),
            ('analyzes', 'analyzes this upload'),
            ('isCompiledBy', 'compiled/created this upload'),
            ('compiles', 'is compiled/created by this upload'),
            ('isIdenticalTo', 'is identical to upload'),
            ('isAlternativeIdentifier', 'is alternate identifier'),
        ],
        default='isSupplementTo',
        widget_classes='form-control',
        widget=ColumnInput(
            class_="col-xs-6 col-pad-0", widget=widgets.Select()
        ),
    )

    def validate_scheme(form, field):
        """Set scheme based on value in identifier."""
        schemes = idutils.detect_identifier_schemes(
            form.data.get('identifier') or ''
        )
        if schemes:
            field.data = schemes[0]
        else:
            field.data = ''


class CreatorForm(WebDepositForm):
    name = fields.StringField(
        placeholder="Family name, First name",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-6"),
        validators=[
            required_if(
                'affiliation',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="Creator name is required if you specify affiliation."
            ),
        ],
    )
    affiliation = fields.StringField(
        placeholder="Affiliation",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-4 col-pad-0"),
    )
    orcid = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            PidNormalize(scheme='orcid'),
        ],
    )
    gnd = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            PidNormalize(scheme='gnd'),
        ],
    )

    def validate_orcid(form, field):
        if field.data:
            schemes = idutils.detect_identifier_schemes(
                field.data or ''
            )
            if 'orcid' not in schemes:
                raise ValidationError("Not a valid ORCID-identifier.")

    def validate_gnd(form, field):
        if field.data:
            schemes = idutils.detect_identifier_schemes(
                field.data or ''
            )
            if 'gnd' not in schemes:
                raise ValidationError("Not a valid GND-identifier.")


class ContributorsForm(WebDepositForm):
    name = fields.StringField(
        placeholder="Family name, First name",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-4 col-pad-0"),
        validators=[
            required_if(
                'affiliation',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="Contributor name is required if you specify"
                " affiliation."
            ),
        ],
    )
    affiliation = fields.StringField(
        placeholder="Affiliation",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-3 col-pad-0"),
    )
    type = fields.SelectField(
        label="",
        choices=cfg['DEPOSIT_CONTRIBUTOR_TYPE_CHOICES'],
        default=cfg['DEPOSIT_CONTRIBUTOR_TYPE_CHOICES'][0][0],
        widget_classes='form-control',
        widget=ColumnInput(
            class_="col-xs-3 col-pad-0", widget=widgets.Select()
        ),
    )
    orcid = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            PidNormalize(scheme='orcid'),
        ],
    )
    gnd = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            PidNormalize(scheme='gnd'),
        ],
    )

    def validate_orcid(form, field):
        if field.data:
            schemes = idutils.detect_identifier_schemes(
                field.data or ''
            )
            if 'orcid' not in schemes:
                raise ValidationError("Not a valid ORCID-identifier.")

    def validate_gnd(form, field):
        if field.data:
            schemes = idutils.detect_identifier_schemes(
                field.data or ''
            )
            if 'gnd' not in schemes:
                raise ValidationError("Not a valid GND-identifier.")


class SubjectsForm(WebDepositForm):
    term = fields.StringField(
        placeholder="Term",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-5"),
        validators=[
            required_if(
                'identifier',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="Term is required if you specify identifier."
            ),
        ],
    )
    scheme = fields.StringField(
        label="",
        default='',
        widget_classes='',
        widget=widgets.HiddenInput(),
    )
    identifier = fields.StringField(
        label="",
        placeholder="Identifier",
        validators=[
            required_if(
                'term',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="Identifier is required if you specify term."
            ),
            validators.optional(),
            pid_validator(),
        ],
        processors=[
            PidSchemeDetection(set_field='scheme'),
            PidNormalize(scheme_field='scheme'),
        ],
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-5 col-pad-0"),
    )

    def validate_scheme(form, field):
        """Set scheme based on value in identifier."""
        schemes = idutils.detect_identifier_schemes(
            form.data.get('identifier') or ''
        )
        if schemes:
            field.data = schemes[0]
        else:
            field.data = ''


class CommunityForm(WebDepositForm):
    identifier = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('title', community_obj_value('title')),
        ],
    )
    title = fields.StringField(
        placeholder="Start typing a community name...",
        autocomplete_fn=community_autocomplete,
        widget=TagInput(),
        widget_classes='form-control',
    )
    provisional = fields.BooleanField(
        default=True,
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('provisional', lambda x: x.object_data),
        ]
    )


class AccessGroupsForm(WebDepositForm):
    identifier = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('title', accessgroups_obj_value('name')),
        ],
    )
    title = fields.StringField(
        placeholder="Start typing a group name...",
        autocomplete_fn=accessgroups_autocomplete,
        widget=TagInput(),
        widget_classes='form-control',
    )


class InputRecordDatasetFieldForm(WebDepositForm):
    identifier = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('title', inputrecords_obj_value()),
        ],
    )
    title = fields.StringField(
        placeholder="Start typing a record title...",
        autocomplete_fn=inputrecords_autocomplete_dataset,
        widget=TagInput(),
        widget_classes='form-control',
    )
    is_pid = fields.BooleanField(
        widget=widgets.HiddenInput(),
        default=False
    )


class InputRecordSoftwareFieldForm(WebDepositForm):
    identifier = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('title', inputrecords_obj_value()),
        ],
    )
    title = fields.StringField(
        placeholder="Start typing a record title...",
        autocomplete_fn=inputrecords_autocomplete_software,
        widget=TagInput(),
        widget_classes='form-control',
    )
    is_pid = fields.BooleanField(
        widget=widgets.HiddenInput(),
        default=False
    )


class FileDescriptionForm(WebDepositForm):
    description = fields.StringField(
        label="",
        widget=widgets.HiddenInput(),
    )
    file_id = fields.StringField(
        label="",
        widget=widgets.HiddenInput(),
    )


class FilesForm(WebDepositForm):
    template = 'deposit/files.html'
    files_require = True

    files_errors = fields.StringField(
        widget=widgets.HiddenInput(),
        label=''
    )

    plupload_file = fields.FileUploadField(
        label="",
        widget=plupload_widget,
        export_key=False
    )

    file_description = fields.DynamicFieldList(
        fields.FormField(
            FileDescriptionForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div'
            ),
        ),
        label='',
        widget_classes='',
        icon='fa fa-user fa-fw',
        widget=DynamicHiddenListWidget(),
        min_entries=0,
    )

    def validate_files_errors(form, field):
        """Ensure minimum one file is attached."""
        if form.files_require:
            if not getattr(request, 'is_api_request', False):
                try:
                    # Tested in API by a separate workflow task.
                    if len(form.files) == 0:
                        raise ValidationError(
                            "You must provide at least one file.")
                except AttributeError:
                    # this should never happen
                    pass


class AnalysisFilesForm(FilesForm):
    files_require = False


#
# BasicForm
#
class BasicForm(WebDepositForm):
    template = 'deposit/metadata.html'

    """Basic Upload Form."""

    #
    # Basic information
    #
    doi = fields.DOIField(
        label="Digital Object Identifier",
        description="Optional. Did your publisher already assign a DOI to "
        "your upload? If not, leave the field empty and a new "
        "DOI will be prereserved for your record. If you wish, "
        "you can mint the prereserved DOI in the "
        "next steps. A DOI allows "
        "others to easily and unambiguously cite your data.",
        placeholder="e.g. 10.1234/lw_daap...",
        validators=[
            DOISyntaxValidator(),
            invalid_doi_prefix_validator(prefix=CFG_DATACITE_DOI_PREFIX),
        ],
        processors=[
            local_datacite_lookup
        ],
        export_key='doi',
        icon='fa fa-barcode fa-fw',
    )
    publication_date = fields.Date(
        label=_('Publication date'),
        icon='fa fa-calendar fa-fw',
        description='Required. In case your upload '
        'was already published elsewhere, please use the date of first'
        ' publication.',
        default=date.today(),
        validators=[
            validators.DataRequired(),
            DateRange(max=date.today(), message="Date must be at most today."),
        ],
        widget=date_widget,
        widget_classes='input-sm',
    )
    title = fields.TitleField(
        validators=[
            validators.DataRequired(),
            validators.Length(min=5),
        ],
        description='Required.',
        filters=[
            strip_string,
        ],
        export_key='title',
        icon='fa fa-book fa-fw',
    )
    creators = fields.DynamicFieldList(
        fields.FormField(
            CreatorForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div'
            ),
        ),
        label='Authors',
        add_label='Add another author',
        description='Required.',
        icon='fa fa-user fa-fw',
        widget_classes='',
        min_entries=1,
        export_key='authors',
        validators=[validators.DataRequired(), list_length(
            min_num=1, element_filter=filter_empty_helper(),
        )],
    )
    description = fields.TextAreaField(
        label="Description",
        description='Required. You can upload documentation in the next step.',
        default='',
        icon='fa fa-pencil fa-fw',
        validators=[validators.DataRequired(), ],
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
    )
    keywords = zfields.KeywordsField(
        validators=[validators.optional()],
        label='Keywords',
        description='Optional. Introduce keywords separated by commas.',
        default='',
        icon='fa fa-tags fa-fw',
        widget_classes='form-control',
    )
    notes = fields.TextAreaField(
        label="Additional notes",
        description='Optional.',
        default='',
        validators=[validators.optional()],
        filters=[
            strip_string,
        ],
        widget_classes='form-control',
        icon='fa fa-pencil fa-fw',
    )

    #
    # Access rights
    #
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
    access_conditions = fields.TextAreaField(
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

    #
    # Collection
    #
    communities = fields.DynamicFieldList(
        fields.FormField(
            CommunityForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget())
        ),
        validators=[community_validator],
        widget=TagListWidget(template="{{title}}"),
        widget_classes=' dynamic-field-list',
        icon='fa fa-group fa-fw',
        export_key='provisional_communities',
    )

    #
    # Project
    #
    project = fields.StringField(
        widget=widgets.HiddenInput(),
        validators=[project_acl_validator],
        default=None,
        label='',
    )

    record_curated_in_project = fields.StringField(
        widget=widgets.HiddenInput(),
        default="False",
        label='',
    )

    record_public_from_project = fields.StringField(
        widget=widgets.HiddenInput(),
        default="False",
        label='',
    )

    #
    # Related work
    #
    related_identifiers = fields.DynamicFieldList(
        fields.FormField(
            RelatedIdentifierForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div'
            ),
        ),
        label="Related identifiers",
        add_label='Add another related identifier',
        description="Optional. Format: e.g. 10.1234/foo.bar",
        icon='fa fa-barcode fa-fw',
        widget_classes='',
        min_entries=1,
    )

    #
    # Subjects
    #
    subjects = fields.DynamicFieldList(
        fields.FormField(
            SubjectsForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div'
            ),
        ),
        label="Subjects",
        add_label='Add another subject',
        icon='fa fa-tags fa-fw',
        widget_classes='',
        min_entries=1,
    )

#
# Form
#


class DMPForm(BasicForm):

    """DMP Upload Form."""
    upload_type = fields.StringField(
        widget=widgets.HiddenInput(),
        default="dmp",
    )

    #
    # Form configuration
    #
    _title = _('New DMP')
    _drafting = True   # enable and disable drafting

    #
    # Grouping of fields
    #
    groups = [
        ('<i class="fa fa-info"></i> Basic information', [
            'doi', 'publication_date', 'title', 'creators',
            'description', 'keywords', 'notes',
        ], {
            # 'classes': '',
            'indication': 'required',
        }),
        ('<i class="fa fa-certificate"></i> License', [
            'access_right', 'embargo_date', 'license',
            'access_conditions', 'access_groups',
        ], {
            # 'classes': '',
            'indication': 'required',
            'description': (
                'Unless you explicitly specify the license conditions below'
                ' for Open Access and Embargoed Access uploads, you agree to'
                ' release your data files under the terms of the Creative'
                ' Commons Zero (CC0) waiver. All authors of the data and'
                ' publications have agreed to the terms of this waiver and'
                ' license.')
        }),
        ('<i class="fa fa-users"></i> Communities', [
            'communities',
        ], {
            # 'classes': '',
            'indication': 'recommended',
            'description': Markup(
                'Any user can create a community on'
                ' %(CFG_SITE_NAME)s (<a href="/communities/">browse'
                ' communities</a>). Specify communities which you wish your'
                ' upload to appear in. The owner of the community (and also'
                ' the default community) will be notified, and can either'
                ' accept or reject your request.' %
                {'CFG_SITE_NAME': CFG_SITE_NAME}),
        }),
        ('<i class="fa fa-bars"></i> Related Identifiers', [
            'related_identifiers'
        ], {
            'classes': '',
            'indication': 'optional',
        }),
        ('<i class="fa fa-tags"></i> Subjects', [
            'subjects'
        ], {
            'classes': '',
            'indication': 'optional',
            'description': 'Specify subjects from a taxonomy or controlled '
            'vocabulary. Each term must be uniquely identified '
            '(e.g. a URL). For free form text, use the keywords'
            ' field in basic information section.',
        }),
    ]


class DatasetForm(BasicForm):

    """Dataset Upload Form."""
    upload_type = fields.StringField(
        widget=widgets.HiddenInput(),
        default="dataset",
    )

    period = fields.DynamicFieldList(
        fields.FormField(
            zfields.PeriodFieldForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget()),
        ),
        label="Temporal coverage",
        add_label='Add another period',
        description='Optional. Start and end dates.',
        icon='fa fa-calendar fa-fw',
        widget_classes='',
        min_entries=1,
    )

    frequency = fields.DynamicFieldList(
        fields.FormField(
            zfields.FrequencyFieldForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget()),
            # widget=ExtendedListWidget(html_tag='div',
            # item_widget=ItemWidget(), class_="row"), # when not in dynamic
            # field
        ),
        label="Frecuency",
        add_label='Add another frequency',
        description='Optional. Frecuency collection of your data.',
        icon='fa fa-clock-o fa-fw',
        widget_classes='',
        min_entries=1,
    )

    spatial = fields.DynamicFieldList(
        fields.FormField(
            zfields.SpatialFieldForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget()),
        ),
        label="Spatial coverage",
        add_label='Add another location',
        description='Optional. Spatial coverage of your data.'
                    ' Coordinates: western most longitude, eastern most'
                    ' longitude, northern most latitude, southern most'
                    ' latitude. The coordinates must be recorded in decimal'
                    ' degrees.',
                    # ' The coordinates must be recorded in the form hdddmmss'
                    # ' (hemisphere-degrees-minutes-seconds). The subelements'
                    # ' are each right justified and unused positions contain'
                    # ' zeros.',
        icon='fa fa-map-marker fa-fw',
        widget_classes='',
        min_entries=1,
    )

    #
    # Form configuration
    #
    _title = _('New dataset')
    _drafting = True   # enable and disable drafting

    #
    # Grouping of fields
    #
    groups = [
        ('<i class="fa fa-info"></i> Basic information', [
            'doi', 'publication_date', 'title', 'creators',
            'description', 'keywords', 'notes',
        ], {
            # 'classes': '',
            'indication': 'required',
        }),
        ('<i class="fa fa-certificate"></i> License', [
            'access_right', 'embargo_date', 'license',
            'access_conditions', 'access_groups',
        ], {
            # 'classes': '',
            'indication': 'required',
            'description': (
                'Unless you explicitly specify the license conditions below'
                ' for Open Access and Embargoed Access uploads, you agree to'
                ' release your data files under the terms of the Creative'
                ' Commons Zero (CC0) waiver. All authors of the data and'
                ' publications have agreed to the terms of this waiver and'
                ' license.')
        }),
        ('<i class="fa fa-globe"></i> Physical information', [
            'period',
            'frequency',
            'spatial',
        ], {
            'classes': '',
            'indication': 'optional',
        }),
        ('<i class="fa fa-users"></i> Communities', [
            'communities',
        ], {
            # 'classes': '',
            'indication': 'recommended',
            'description': Markup(
                'Any user can create a community on'
                ' %(CFG_SITE_NAME)s (<a href="/communities/">browse'
                ' communities</a>). Specify communities which you wish your'
                ' upload to appear in. The owner of the community (and also'
                ' the default community) will be notified, and can either'
                ' accept or reject your request.' %
                {'CFG_SITE_NAME': CFG_SITE_NAME}),
        }),
        ('<i class="fa fa-bars"></i> Related Identifiers', [
            'related_identifiers'
        ], {
            'classes': '',
            'indication': 'optional',
        }),
        ('<i class="fa fa-tags"></i> Subjects', [
            'subjects'
        ], {
            'classes': '',
            'indication': 'optional',
            'description': 'Specify subjects from a taxonomy or controlled '
            'vocabulary. Each term must be uniquely identified '
            '(e.g. a URL). For free form text, use the keywords'
            ' field in basic information section.',
        }),
    ]


class SoftwareForm(BasicForm):

    """Software Upload Form."""
    upload_type = fields.StringField(
        widget=widgets.HiddenInput(),
        default="software",
    )

    # Requirements
    os = zfields.RequirementsField(
        label="OS",
        default='os-notspec',
        domain_os=True,
        domain_flavor=False,
        validators=[validators.optional()],
        filters=[
            strip_string,
        ],
        icon='fa fa-laptop fa-fw',
    )
    flavor = zfields.RequirementsField(
        label="Flavor",
        default='flavor-notspec',
        domain_os=False,
        domain_flavor=True,
        validators=[validators.optional()],
        filters=[
            strip_string,
        ],
        icon='fa fa-laptop fa-fw',
    )
    app_env = zfields.ApplicationEnvironmentsField(
        label="Application environment",
        validators=[validators.optional()],
        icon='fa fa-laptop fa-fw',
    )

    #
    # Form configuration
    #
    _title = _('New software')
    _drafting = True   # enable and disable drafting

    #
    # Grouping of fields
    #
    groups = [
        ('<i class="fa fa-info"></i> Basic information', [
            'doi', 'publication_date', 'title', 'creators',
            'description', 'keywords', 'notes',
        ], {
            # 'classes': '',
            'indication': 'required',
        }),
        ('<i class="fa fa-laptop"></i> Requirements', [
            'os', 'flavor', 'app_env',
        ], {
            # 'classes': '',
            'indication': 'recommended',
            'description': (
                'Requirements are recommended in order to allow ...')
        }),
        ('<i class="fa fa-certificate"></i> License', [
            'access_right', 'embargo_date', 'license',
            'access_conditions', 'access_groups',
        ], {
            # 'classes': '',
            'indication': 'required',
            'description': (
                'Unless you explicitly specify the license conditions below'
                ' for Open Access and Embargoed Access uploads, you agree to'
                ' release your data files under the terms of the Creative'
                ' Commons Zero (CC0) waiver. All authors of the data and'
                ' publications have agreed to the terms of this waiver and'
                ' license.')
        }),
        ('<i class="fa fa-users"></i> Communities', [
            'communities',
        ], {
            # 'classes': '',
            'indication': 'recommended',
            'description': Markup(
                'Any user can create a community collection on'
                ' %(CFG_SITE_NAME)s (<a href="/communities/">browse'
                ' communities</a>). Specify communities which you wish your'
                ' upload to appear in. The owner of the community will'
                ' be notified, and can either accept or reject your'
                ' request.' % {'CFG_SITE_NAME': CFG_SITE_NAME}),
        }),
        ('<i class="fa fa-bars"></i> Related Identifiers', [
            'related_identifiers'
        ], {
            'classes': '',
            'indication': 'optional',
        }),
        ('<i class="fa fa-tags"></i> Subjects', [
            'subjects'
        ], {
            'classes': '',
            'indication': 'optional',
            'description': 'Specify subjects from a taxonomy or controlled '
            'vocabulary. Each term must be uniquely identified '
            '(e.g. a URL). For free form text, use the keywords'
            ' field in basic information section.',
        }),
    ]


class AnalysisForm(BasicForm):

    """Analysis Upload Form."""
    upload_type = fields.StringField(
        widget=widgets.HiddenInput(),
        default="analysis",
    )

    # Inputs
    rel_dataset = fields.DynamicFieldList(
        fields.FormField(
            InputRecordDatasetFieldForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget()),
        ),
        validators=[
            validators.DataRequired(message="This field is required."),
            list_length(min_num=1),
            rel_record_validator
        ],
        label="Input dataset",
        add_label="Add input dataset identifier",
        description='Required. Input dataset title/identifier.',
        icon='fa fa-table fa-fw',
        default='',
        widget=TagListWidget(template="{{title}}"),
        widget_classes=' dynamic-field-list',
    )

    rel_software = fields.DynamicFieldList(
        fields.FormField(
            InputRecordSoftwareFieldForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget()),
        ),
        validators=[
            validators.DataRequired(message="This field is required."),
            list_length(min_num=1),
            rel_record_validator
        ],
        label="Input software",
        add_label="Add input software identifier",
        description='Required. Input software title/identifier.',
        icon='fa fa-table fa-fw',
        default='',
        widget=TagListWidget(template="{{title}}"),
        widget_classes=' dynamic-field-list',
    )

    # Requirements
    os = zfields.RequirementsField(
        label="OS",
        default='os-notspec',
        domain_os=True,
        domain_flavor=False,
        validators=[validators.optional()],
        filters=[
            strip_string,
        ],
        icon='fa fa-laptop fa-fw',
    )
    flavor = zfields.RequirementsField(
        label="Flavor",
        default='flavor-notspec',
        domain_os=False,
        domain_flavor=True,
        validators=[validators.optional()],
        filters=[
            strip_string,
        ],
        icon='fa fa-laptop fa-fw',
    )
    app_env = zfields.ApplicationEnvironmentsField(
        label="Application environment",
        validators=[validators.optional()],
        icon='fa fa-laptop fa-fw',
    )

    #
    # Form configuration
    #
    _title = _('New analysis')
    _drafting = True   # enable and disable drafting

    #
    # Grouping of fields
    #
    groups = [
        ('<i class="fa fa-info"></i> Basic information', [
            'doi', 'publication_date', 'title', 'creators',
            'description', 'keywords', 'notes',
        ], {
            # 'classes': '',
            'indication': 'required',
        }),
        ('<i class="fa fa-asterisk"></i> Inputs', [
            'rel_dataset', 'rel_software',
        ], {
            # 'classes': '',
            'indication': 'required',
            'description': (
                'Specifiy the inputs of your analysis. Datasets and'
                ' softwares can  be associated to this upload using'
                ' the record title in this portal or the associated'
                ' internal PID, or the internal or external DOI. At'
                ' least a dataset'
                ' and a software must be specified. The autocomplete'
                ' option is only available for the record title;'
                ' PIDs or DOIs must be entered completely.')
        }),
        ('<i class="fa fa-laptop"></i> Requirements', [
            'os', 'flavor', 'app_env',
        ], {
            'indication': 'recommended',
            'description': (
                'Requirements are recommended in order to best'
                ' fit the needs of your analysis.')
        }),
        ('<i class="fa fa-certificate"></i> License', [
            'access_right', 'embargo_date', 'license',
            'access_conditions', 'access_groups',
        ], {
            'indication': 'required',
            'description': (
                'Unless you explicitly specify the license conditions below'
                ' for Open Access and Embargoed Access uploads, you agree to'
                ' release your data files under the terms of the Creative'
                ' Commons Zero (CC0) waiver. All authors of the data and'
                ' publications have agreed to the terms of this waiver and'
                ' license.')
        }),
        ('<i class="fa fa-users"></i> Communities', [
            'communities',
        ], {
            'indication': 'recommended',
            'description': Markup(
                'Any user can create a community collection on'
                ' %(CFG_SITE_NAME)s (<a href="/communities/">browse'
                ' communities</a>). Specify communities which you wish your'
                ' upload to appear in. The owner of the community will'
                ' be notified, and can either accept or reject your'
                ' request.' % {'CFG_SITE_NAME': CFG_SITE_NAME}),
        }),
        ('<i class="fa fa-bars"></i> Related Identifiers', [
            'related_identifiers'
        ], {
            'classes': '',
            'indication': 'optional',
        }),
        ('<i class="fa fa-tags"></i> Subjects', [
            'subjects'
        ], {
            'classes': '',
            'indication': 'optional',
            'description': 'Specify subjects from a taxonomy or controlled '
            'vocabulary. Each term must be uniquely identified '
            '(e.g. a URL). For free form text, use the keywords'
            ' field in basic information section.',
        }),
    ]


def filter_fields(groups):
    def _inner(element):
        element = list(element)
        element[1] = filter(lambda x: x in groups, element[1])
        return tuple(element)
    return _inner


class EditFormMixin(object):
    """Mixin class for forms that needs editing."""

    recid = fields.IntegerField(
        validators=[
            unchangeable(),
        ],
        widget=widgets.HiddenInput(),
        label=""
    )
    modification_date = fields.DateTimeField(
        validators=[
            unchangeable(),
        ],
        widget=widgets.HiddenInput(),
        label="",
        default=date.today(),
    )


class BasicEditForm(BasicForm, EditFormMixin):
    """Specialized form for editing a record."""
    doi = None
    _title = _('Edit upload')
    template = "deposit/edit.html"


class DMPEditForm(BasicEditForm, DatasetForm):
    pass


class DatasetEditForm(BasicEditForm, DatasetForm):
    pass


class SoftwareEditForm(BasicEditForm, SoftwareForm):
    pass


class AnalysisEditForm(BasicEditForm, AnalysisForm):
    pass
