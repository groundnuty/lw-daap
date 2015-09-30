from __future__ import absolute_import

from functools import wraps

from flask import current_app, redirect, url_for
from flask_login import current_user

from .proxy_utils import get_client_proxy_info
from .models import userProfile

def delegation_required():
    next_url="http://aeonium.eu"
    """
    Checks if a valid delegation is available for the user
    Otherwise redirects to profile.
    """
    def delegation(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated():
                return current_app.login_manager.unauthorized()
            info = get_client_proxy_info(userProfile.get_or_create())
            if info.get('user_proxy', False):
                return func(*args, **kwargs)
            else:
                return redirect(url_for('userProfile.delegate', next=next_url))
        return decorated_view
    return delegation
