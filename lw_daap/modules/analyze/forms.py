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

from wtforms import SelectField, StringField, HiddenField, \
    validators, ValidationError

from invenio.utils.forms import InvenioBaseForm


class LaunchFormData:
    """
    Helper Class to pass when initializing the LaunchForm
    """

    def _get_value_from_id(self, reqs, id):
        for k, v in reqs.items():
            if v['id'] == id:
                return k
        return None

    def __init__(self, reqs, title=None, flavor=None,
                 os=None, app_env=None, recid=None, **kwargs):
        if title:
            self.name = title[0]
        if flavor:
            self.flavor = self._get_value_from_id(reqs['flavors'], flavor[0])
        if os:
            self.image = self._get_value_from_id(reqs['images'], os[0])
        if app_env:
            self.app_env = self._get_value_from_id(reqs['app_envs'],
                                                   app_env[0])
        if recid:
            self.recid = recid[0]


class LaunchForm(InvenioBaseForm):
    recid = HiddenField()

    name = StringField(
        label='Instance Name',
        description='Required. A name that helps to identify your instance',
        validators=[validators.DataRequired(),
                    validators.length(
                        max=50,
                        message=("The identifier must be less "
                                 "than 50 characters long.")),
                    ],
    )

    flavor = SelectField(
        label='Flavor',
        description='Required. Size of the VM to start',
    )

    image = SelectField(
        label='Operating System',
        description='Required. Operating System to use',
    )

    app_env = SelectField(
        label='Application environment',
        description='Required. Some info?',
    )

    def __init__(self, **kwargs):
        if 'user_profile' in kwargs:
            self.user_profile = kwargs['user_profile']
        else:
            self.user_profile = None
        super(LaunchForm, self).__init__(**kwargs)

    def _build_choices(self, reqs, req_type, title_field='title'):
        return [(k, v[title_field]) for k, v in reqs.get(req_type, {}).items()]

    def fill_fields_choices(self, reqs):
        self.flavor.choices = self._build_choices(reqs, 'flavors', 'id')
        self.image.choices = self._build_choices(reqs, 'images')
        self.app_env.choices = self._build_choices(reqs, 'app_envs')

    def validate_image(form, field):
        if (field.data in ['centos-6', 'centos-7'] and
                form.app_env.data != 'ssh'):
            msg = ('Centos 6 and Centos 7 currently only support ssh.')
            raise ValidationError(msg)

    def validate_app_env(form, field):
        if field.data == 'ssh' and form.user_profile:
            if not form.user_profile.ssh_public_key:
                msg = ('You need a ssh key before using this application '
                       'environment. You can set one at your profile '
                       'settings.')
                raise ValidationError(msg)
