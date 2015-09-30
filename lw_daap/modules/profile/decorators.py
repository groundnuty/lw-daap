from __future__ import absolute_import

from functools import wraps

from flask import current_app, flash, redirect, url_for
from flask_login import current_user

from .proxy_utils import get_client_proxy_info
from .models import userProfile

def delegation_required(func):
    """
    Checks if a valid delegation is available for the user
    Otherwise redirects to profile.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        info = get_client_proxy_info(userProfile.get_or_create())
        if info.get('user_proxy', False):
            return func(*args, **kwargs)
        else:
            flash('You need a valid credential to access the e-infrastructure',
                  'danger')
            return redirect(url_for('userProfile.delegate'))
    return decorated_view
