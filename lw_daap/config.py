#
# LifeWatch Data Access and Preservation
# Configuration

import sys
reload(sys)  
sys.setdefaultencoding('utf8')

from invenio.base.config import EXTENSIONS

# MonkeyPatch the UserInfo so it gets our group stuff
# must be done quite early!
import invenio.ext.login.legacy_user
old_login = invenio.ext.login.legacy_user.UserInfo._login
def new_login(self, uid, force=False):
    from lw_daap.modules.invenio_groups.models import Group
    data = old_login(self, uid, force)
    data['group'] = map(lambda x: x.name, Group.query_by_uid(uid))
    return data
invenio.ext.login.legacy_user.UserInfo._login = new_login

import warnings
warnings.filterwarnings('ignore')

import lw_daap.base.auth.github
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

DISABLE_WARNINGS = True

PACKAGES = [
    "lw_daap.base",
    "lw_daap.modules.communities",
    "lw_daap.modules.deposit",
    "lw_daap.modules.invenio_deposit",
    "lw_daap.modules.invenio_groups",
    "lw_daap.modules.github",
    "lw_daap.modules.pids",
    "lw_daap.modules.profile",
    "lw_daap.deploy",
    "invenio.base",
    "invenio.modules.*",
]


PACKAGES_EXCLUDE= [
    "invenio.modules.deposit",
    "invenio.modules.groups",
    "invenio.modules.messages",
    "invenio.modules.documentation",
    "invenio.modules.workflows",
    "invenio.modules.annotations",
]

#EXTENSIONS.remove('invenio.ext.legacy')

DEPOSIT_TYPES = [
    "lw_daap.modules.deposit.workflows.dataset:dataset",
    "lw_daap.modules.deposit.workflows.software:software",
    "lw_daap.modules.deposit.workflows.analysis:analysis",
]

DEPOSIT_DEFAULT_TYPE = "lw_daap.modules.deposit.workflows.dataset:dataset"
DEPOSIT_MAX_UPLOAD_SIZE = "1000mb"
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
ASSETS_DEBUG = True
ASSETS_AUTO_BUILD = True
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
# -->

RECORDS_BREADCRUMB_TITLE_KEY = 'title'

# OAuth configuration
OAUTHCLIENT_REMOTE_APPS = dict(
    github=lw_daap.base.auth.github.REMOTE_APP,
    google=lw_daap.base.auth.google.REMOTE_APP,
    facebook=lw_daap.base.auth.facebook.REMOTE_APP,
)

WEBHOOKS_DEBUG_RECEIVER_URLS = {
    'github': 'http://github.aeonium.ultrahook.com?access_token=%(token)s',
}

try:
    from lw_daap.secrets import *
except ImportError:
    pass


try:
    from lw_daap.instance_config import *
except ImportError:
    pass
