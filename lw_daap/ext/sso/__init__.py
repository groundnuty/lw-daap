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

# This file is part of Invenio.
# Copyright (C) 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Initialize and configure *Flask-SSO* extension."""

from flask import flash, redirect
from flask_sso import SSO


#: Default attribute map
SSO_ATTRIBUTE_MAP = {
     "Shib-Identity-Provider": (True, "idp"),
}

sso = SSO()


def setup_app(app):
    """Setup SSO extension."""
    app.config['CFG_EXTERNAL_AUTH_USING_SSO'] = True
    app.config.setdefault('SSO_ATTRIBUTE_MAP', SSO_ATTRIBUTE_MAP)
    sso.init_app(app)

    @sso.login_handler
    def login_callback(user_info):
        """Login user base on SSO context (create one if necessary).
        Function should not raise an exception if `user_info` is not valid
        or `User` was not found in database.
        """
        from invenio.modules.accounts.models import User
        from invenio.ext.login import (authenticate, login_redirect,
                                       current_user)
        from invenio.ext.sqlalchemy import db

        try:
            auth = authenticate(user_info['uid'], login_method='SSO')
            if auth is None:
                user = User()
                user.nickname = user_info['uid']
                user.email = user_info['email']
                user.password = ''
                user.settings = {'login_method': 'SSO'}
                db.session.add(user)
                db.session.commit()
                auth = authenticate(user_info['email'], login_method='SSO')
                if auth is None:
                    return redirect('/')
            current_user.save()
        except:
            flash('Problem with login (%s)' % (str(user_info)), 'error')
            return redirect('/')

        return login_redirect()

    return app
