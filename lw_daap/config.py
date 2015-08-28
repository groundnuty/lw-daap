#
# LifeWatch Data Access and Preservation
# Configuration

import invenio.modules.oauthclient.contrib.github

import lw_daap.base.auth.google
import lw_daap.base.auth.facebook

# Global config
CFG_SITE_LANGS = ["en"]

CFG_SITE_NAME = "LifeWatch Data Access and Preservation"
CFG_SITE_NAME_INTL = {
    "en": CFG_SITE_NAME
}
CFG_SITE_SUPPORT_EMAIL = "support@aeonium.eu"
CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS = 5

COMMUNITIES_PARENT_NAME=CFG_SITE_NAME
COMMUNITIES_PARENT_NAME_PROVISIONAL=CFG_SITE_NAME
COMMUNITIES_ID_PREFIX = 'community'
COMMUNITIES_ID_PREFIX_PROVISIONAL = 'provisional-community'

PACKAGES = [
    "lw_daap.base",
#    "lw_daap.modules.accessrequests",
    "lw_daap.modules.deposit",
    "lw_daap.modules.communities",
    "lw_daap.deploy",
    "invenio.base",
    "invenio.modules.*",
]


PACKAGES_EXCLUDE= [
    "invenio.modules.messages",
    "invenio.modules.documentation",
    "invenio.modules.oauth2server",
    "invenio.modules.workflows",
    "invenio.modules.annotations",
]


DEPOSIT_TYPES = [
    "lw_daap.modules.deposit.workflows.dataset:dataset",
    "lw_daap.modules.deposit.workflows.software:software",
    "lw_daap.modules.deposit.workflows.analysis:analysis",
]
DEPOSIT_DEFAULT_TYPE = "lw_daap.modules.deposit.workflows.dataset:dataset"

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

# OAuth configuration
OAUTHCLIENT_REMOTE_APPS = dict(
    github=invenio.modules.oauthclient.contrib.github.REMOTE_APP,
    google=lw_daap.base.auth.google.REMOTE_APP,
    facebook=lw_daap.base.auth.facebook.REMOTE_APP,
)

try:
    from lw_daap.secrets import *
except ImportError:
    pass


try:
    from lw_daap.instance_config import *
except ImportError:
    pass
