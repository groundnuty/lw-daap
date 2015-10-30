# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
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

"""Project forms."""

from __future__ import absolute_import

from invenio.base.i18n import _
from invenio.utils.forms import InvenioBaseForm, InvenioForm as Form

from wtforms import HiddenField, StringField, TextAreaField, validators

from .models import Project


class SearchForm(Form):
    """Search Form."""
    p = StringField(
        validators=[validators.DataRequired()]
    )


class DeleteProjectForm(Form):
    delete = HiddenField(default='yes', validators=[validators.DataRequired()])


class ProjectForm(Form):
    """Project form."""

    field_sets = [
        ('Information', [
            'title', 'description',
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

    #
    # Fields
    #
    title = StringField(
        description='Required.',
        validators=[validators.DataRequired()]
    )

    description = TextAreaField(
        description=_(
            'Optional. A short description of the  project,'
            ' which will be displayed on the index page of the project.'),
    )

    field_icons = {
        'title': 'file-alt',
        'description': 'pencil',
    }


class EditProjectForm(ProjectForm):
    pass
