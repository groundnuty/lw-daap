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
#

# LifeWatch Open Science Framework
# Configuration

from datetime import timedelta
from invenio.base.config import EXTENSIONS
import warnings
import lw_daap.base.auth.github
import lw_daap.base.auth.google
import lw_daap.base.auth.facebook

import sys
reload(sys)
sys.setdefaultencoding('utf8')

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

warnings.filterwarnings('ignore')


# Global config
CFG_SITE_LANGS = ["en"]

CFG_SITE_NAME = "LifeWatch Open Science Framework"
CFG_SITE_DESCRIPTION = "LifeWatch Open Science Framework DESC"
CFG_SITE_NAME_INTL = {
    "en": CFG_SITE_NAME
}

CFG_EMAIL_BACKEND = "flask_email.backends.smtp.Mail"

CFG_SITE_SUPPORT_EMAIL = "support@mail"
CFG_SITE_ADMIN_EMAIL = "support@mail"
CFG_WEBALERT_ALERT_ENGINE_EMAIL = "support@mail"
CFG_WEBCOMMENT_ALERT_ENGINE_EMAIL = "support@mail"
CFG_ACCESS_CONTROL_LEVEL_ACCOUNTS = 5

COMMUNITIES_PARENT_NAME = 'Communities'
COMMUNITIES_PARENT_NAME_PROVISIONAL = COMMUNITIES_PARENT_NAME
COMMUNITIES_ID_PREFIX = 'community'
COMMUNITIES_ID_PREFIX_PROVISIONAL = 'provisional-community'
COMMUNITIES_PORTALBOXES = [
    'communities/portalbox_main.html',
]
COMMUNITIES_PERIODIC_TASKS = {
    'ranking_deamon': {
        'run_every': timedelta(minutes=20),
    },
}
CFG_LWDAAP_BIBSCHED_CHECK_PERIOD = timedelta(minutes=20)

DISABLE_WARNINGS = True


# BLUEPRINTS_URL_PREFIXES = {
#    "search": "/search",
# }


PACKAGES = [
    "lw_daap.base",
    "lw_daap.modules.deposit",
    "lw_daap.modules.communities",
    "lw_daap.modules.invenio_deposit",
    "lw_daap.modules.invenio_groups",
    "lw_daap.modules.github",
    "lw_daap.modules.analyze",
    "lw_daap.modules.record_actions",
    "lw_daap.modules.profile",
    "lw_daap.modules.projects",
    "lw_daap.modules.instrument",
    "lw_daap.modules.usergroupinstrument",
    "lw_daap.modules.userinstrument",
    "lw_daap.deploy",
    "invenio.base",
    "invenio.modules.*",
]


PACKAGES_EXCLUDE = [
    "invenio.modules.deposit",
    "invenio.modules.groups",
    "invenio.modules.messages",
    "invenio.modules.documentation",
    "invenio.modules.workflows",
    "invenio.modules.annotations",
]


EXTENSIONS += [
    "invenio.ext.sso"
]


DEPOSIT_TYPES = [
    "lw_daap.modules.deposit.workflows.dmp:dmp",
    "lw_daap.modules.deposit.workflows.dataset:dataset",
    "lw_daap.modules.deposit.workflows.software:software",
    "lw_daap.modules.deposit.workflows.analysis:analysis",
    "lw_daap.modules.deposit.workflows.instrument:instrument",
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

RECORDS_BREADCRUMB_TITLE_KEY = 'title'

# OAuth configuration
OAUTHCLIENT_REMOTE_APPS = dict(
    github=lw_daap.base.auth.github.REMOTE_APP,
    google=lw_daap.base.auth.google.REMOTE_APP,
    facebook=lw_daap.base.auth.facebook.REMOTE_APP,
)

SSO_ATTRIBUTE_MAP = {
    "Shib-Identity-Provider": (True, "idp"),
    "persistent-id": (True, "persistent-id"),
    # "HTTP_SHIB_SHARED_TOKEN": (True, "shared_token"),
    "cn": (True, "cn"),
    # "HTTP_SHIB_MAILi": (True, "email"),
    "givenName": (False, "first_name"),
    "unscoped-affiliation": (False, "unscoped-affiliation"),
    "affiliation": (False, "affiliation"),
    "manager": (False, "manager"),
    "entitlement": (False, "entitlement"),
    "eppn": (False, "eppn"),
    "sn": (False, "last_name"),
}
CFG_EXTERNAL_AUTH_HIDDEN_GROUPS = ()
CFG_EXTERNAL_AUTH_HIDDEN_GROUPS_RE = ()


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
