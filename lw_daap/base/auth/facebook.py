#
# invenio.oauth2client configuration for facebook
#

REMOTE_APP = dict(
    title='facebook',
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
    userinfo = remote.get('userinfo').data
    return dict(email=userinfo.get('email'), nickname=userinfo.get('email'))
