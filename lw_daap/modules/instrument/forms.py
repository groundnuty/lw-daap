# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Rafael Salas Robledo
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function, unicode_literals

from invenio.utils.forms import InvenioBaseForm

from wtforms_alchemy import model_form_factory
from wtforms import StringField, RadioField
from wtforms.widgets import RadioInput, HTMLString
from wtforms import validators, widgets
from wtforms.validators import ValidationError
from wtforms_components import DateRange
from flask.ext.wtf import Form

from lw_daap.modules.invenio_deposit import fields
from lw_daap.modules.deposit import fields as zfields
from invenio.config import CFG_DATACITE_DOI_PREFIX, CFG_SITE_NAME, \
    CFG_SITE_SUPPORT_EMAIL
from lw_daap.modules.invenio_deposit.validation_utils \
    import DOISyntaxValidator, invalid_doi_prefix_validator, list_length, \
    pid_validator, required_if, \
    unchangeable
from lw_daap.modules.invenio_deposit.field_widgets \
    import CKEditorWidget, ColumnInput, ExtendedListWidget, \
    ItemWidget, TagInput, TagListWidget, plupload_widget
from lw_daap.modules.invenio_deposit.processor_utils import PidNormalize, \
    PidSchemeDetection, datacite_lookup, replace_field_data

from lw_daap.modules.deposit.autocomplete import community_autocomplete, accessgroups_autocomplete, \
    inputrecords_autocomplete_dataset, inputrecords_autocomplete_software

from lw_daap.modules.deposit.field_widgets import date_widget, DynamicHiddenListWidget
from lw_daap.modules.invenio_deposit.filter_utils import sanitize_html, \
    strip_string

from invenio.base.i18n import _

from lw_daap.modules.invenio_deposit.form import WebDepositForm

from lw_daap.modules.deposit.forms import accessgroups_obj_value, AccessGroupsForm

from invenio.utils.html import CFG_HTML_BUFFER_ALLOWED_TAG_WHITELIST

from datetime import date

__all__ = (
    'InstrumentForm',
)


class InstrumentForm(Form):
    name = StringField("Name", validators=[validators.DataRequired])

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
