from functools import wraps

from flask import current_app
from flask_login import current_user

def login_required(func):
    '''
    This is a re-implementation of flask_login.login_required using
    user.is_authenticated() as function instead of property
    '''
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view
