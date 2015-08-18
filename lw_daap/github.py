
REMOTE_APP = dict(
    title='GitHub',
    description='Software collaboration platform.',
    icon='fa fa-github',
    authorized_handler="invenio.modules.oauthclient.handlers"
                       ":authorized_signup_handler",
    disconnect_handler="invenio.modules.oauthclient.handlers"
                       ":disconnect_handler",
    signup_handler=dict(
        info="invenio.modules.oauthclient.contrib.github:account_info",
        setup="invenio.modules.oauthclient.contrib.github:account_setup",
        view="invenio.modules.oauthclient.handlers:signup_handler",
    ),
    params=dict(
        request_token_params={'scope': 'user:email'},
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_method='POST',
        authorize_url="https://github.com/login/oauth/authorize",
        app_key="GITHUB_APP_CREDENTIALS",
    )
)


def account_info(remote, resp):
    """ Retrieve remote account information used to find local user. """
    gh = github3.login(token=resp['access_token'])
    ghuser = gh.user()
    return dict(email=ghuser.email, nickname=ghuser.login)


def account_setup(remote, token):
    """ Perform additional setup after user have been logged in. """
    pass
