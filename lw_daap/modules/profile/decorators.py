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

from __future__ import absolute_import

from functools import wraps

from flask import current_app, redirect, url_for, request
from flask_login import current_user

from .proxy_utils import get_client_proxy_info
from .models import UserProfile


def delegation_required():
    """
    Checks if a valid delegation is available for the user
    Otherwise redirects to profile.
    """
    def delegation(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated():
                return current_app.login_manager.unauthorized()
            info = get_client_proxy_info(UserProfile.get_or_create())
            if info.get('user_proxy', False):
                return func(*args, **kwargs)
            else:
                return redirect(url_for('userprofile.delegate',
                                        next_url=request.base_url))
        return decorated_view
    return delegation
