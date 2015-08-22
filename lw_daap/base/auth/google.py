#
# invenio.oauth2client configuration for google
#

REMOTE_APP = dict(
    title='google',
    description='Software collaboration platform.',
    icon='fa fa-google',
    authorized_handler="invenio.modules.oauthclient.handlers"
                       ":authorized_signup_handler",
    disconnect_handler="invenio.modules.oauthclient.handlers"
                       ":disconnect_handler",
    signup_handler=dict(
        info="lw_daap.base.auth.google:account_info",
        view="invenio.modules.oauthclient.handlers:signup_handler",       
    ),
    params=dict(
        request_token_params={
            'scope': 'https://www.googleapis.com/auth/userinfo.email'
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_url="https://accounts.google.com/o/oauth2/token",
        access_token_method='POST',
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        app_key="GOOGLE_APP_CREDENTIALS",
    )
)


def account_info(remote, resp):
    """ Retrieve remote account information used to find local user. """
    userinfo = remote.get('userinfo').data
    return dict(email=userinfo.get('email'), nickname=userinfo.get('email'))
