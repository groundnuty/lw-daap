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

#
# invenio.oauth2client configuration for facebook
#

REMOTE_APP = dict(
    title='Facebook',
    description='Internet social platform.',
    icon='fa fa-facebook',
    authorized_handler="invenio.modules.oauthclient.handlers"
                       ":authorized_signup_handler",
    disconnect_handler="invenio.modules.oauthclient.handlers"
                       ":disconnect_handler",
    signup_handler=dict(
        info="lw_daap.base.auth.facebook:account_info",
        view="invenio.modules.oauthclient.handlers:signup_handler",
    ),
    params=dict(
        request_token_params={
            'scope': 'email'
        },
        base_url='https://graph.facebook.com',
        request_token_url=None,
        access_token_url='/oauth/access_token',
        access_token_method='POST',
        authorize_url="https://www.facebook.com/dialog/oauth",
        app_key="FACEBOOK_APP_CREDENTIALS",
    )
)


def account_info(remote, resp):
    """ Retrieve remote account information used to find local user. """
    userinfo = remote.get('https://graph.facebook.com/me?fields=email').data
    return dict(email=userinfo.get('email'), nickname=userinfo.get('email'))
