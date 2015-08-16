CFG_SITE_LANGS = ["en"]

CFG_SITE_NAME = "LifeWatch Data Access and Preservation"
CFG_SITE_NAME_INTL = {
    "en": CFG_SITE_NAME
}
CFG_SITE_SUPPORT_EMAIL = "info@lifewatch.eu"
CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS = 3

COMMUNITIES_PARENT_NAME="communities-collection"
COMMUNITIES_PARENT_NAME_PROVISIONAL="communities-collection"

PACKAGES = [
    "lw_daap.base",
    "lw_daap.modules.deposit",
    "invenio.base",
    "invenio.modules.*",
]

PACKAGES_EXCLUDE= [
    "invenio.modules.documentation",
    "invenio.modules.messages",
]

OAUTHCLIENT_REMOTE_APPS = dict(
    github=dict(
        title='GitHub',
        icon='fa fa-github',
        
	authorized_handler="invenio.modules.oauthclient.handlers" ":authorized_default_handler",
        disconnect_handler="invenio.modules.oauthclient.handlers" ":disconnect_handler",
        


        params=dict(
            request_token_params={
                'scope': 'user:email,admin:repo_hook,read:org'
            },
            base_url='https://api.github.com/',
            request_token_url=None,
            access_token_url="https://github.com/login/oauth/access_token",
            access_token_method='POST',
            authorize_url="https://github.com/login/oauth/authorize",
            app_key="GITHUB_APP_CREDENTIALS",
        )
    ),
)

DEPOSIT_TYPES = [
    "lw_daap.modules.deposit.workflows.upload:upload",
]
DEPOSIT_DEFAULT_TYPE = "lw_daap.modules.deposit.workflows.upload:upload"

# Don't commit anything. Testmode implies prefix is set to 10.5072
CFG_DATACITE_TESTMODE = True

# Test prefix (use with or without test mode):
CFG_DATACITE_DOI_PREFIX = "10.5072"

DEPOSIT_CONTRIBUTOR_TYPES = [
    dict(label='Contact person', marc='prc', datacite='ContactPerson'),
    dict(label='Data collector', marc='col', datacite='DataCollector'),
    dict(label='Data curator', marc='cur', datacite='DataCurator'),
    dict(label='Data manager', marc='dtm', datacite='DataManager'),
    dict(label='Editor', marc='edt', datacite='Editor'),
    dict(label='Researcher', marc='res', datacite='Researcher'),
    dict(label='Rights holder', marc='cph', datacite='RightsHolder'),
    dict(label='Sponsor', marc='spn', datacite='Sponsor'),
    dict(label='Other', marc='oth', datacite='Other'),
]
# DataCite XSLs must also be updated.

DEPOSIT_CONTRIBUTOR_TYPE_CHOICES = [(x['datacite'], x['label'])
                                    for x in DEPOSIT_CONTRIBUTOR_TYPES]

DEPOSIT_CONTRIBUTOR_MARC2DATACITE = dict(
    [(x['marc'], x['datacite']) for x in DEPOSIT_CONTRIBUTOR_TYPES])

DEPOSIT_CONTRIBUTOR_DATACITE2MARC = dict(
    [(x['datacite'], x['marc']) for x in DEPOSIT_CONTRIBUTOR_TYPES])

CFG_DATABASE_NAME = "lwdaap"
CFG_DATABASE_USER = "lwdaap"

# <-- Debug toolbar configuration
DEBUG = True
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
# -->

RECORDS_BREADCRUMB_TITLE_KEY = 'title'  

try:
    from lw_daap.secrets import *
except ImportError:
    pass

try:
    from lw_daap.instance_config import *
except ImportError:
    pass
