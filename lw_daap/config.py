CFG_SITE_LANGS = ["en"]

CFG_SITE_NAME = "LifeWatch Data Access and Preservation"
CFG_SITE_NAME_INTL = {
    "en": CFG_SITE_NAME
}
CFG_SITE_SUPPORT_EMAIL = "info@lifewatch.eu"

COMMUNITIES_ID_PREFIX_PROVISIONAL = " "

PACKAGES = [
    "lw_daap.base",
    "invenio.base",
    "invenio.modules.communities",
    'invenio.modules.access',
    'invenio.modules.accounts',
    'invenio.modules.alerts',
    'invenio.modules.apikeys',
    'invenio.modules.authorprofiles',
    'invenio.modules.baskets',
    'invenio.modules.bulletin',
    'invenio.modules.circulation',
    'invenio.modules.classifier',
    'invenio.modules.cloudconnector',
    'invenio.modules.comments',
    'invenio.modules.communities',
    'invenio.modules.converter',
    'invenio.modules.dashboard',
    'invenio.modules.deposit',
    'invenio.modules.documentation',
    'invenio.modules.documents',
    'invenio.modules.editor',
    'invenio.modules.encoder',
    'invenio.modules.exporter',
    'invenio.modules.formatter',
    'invenio.modules.groups',
    'invenio.modules.indexer',
    'invenio.modules.jsonalchemy',
    'invenio.modules.knowledge',
    'invenio.modules.linkbacks',
    'invenio.modules.matcher',
    'invenio.modules.merger',
    'invenio.modules.messages',
    'invenio.modules.oaiharvester',
    'invenio.modules.oairepository',
    'invenio.modules.oauth2server',
    'invenio.modules.oauthclient',
    'invenio.modules.pages',
    'invenio.modules.pidstore',
    'invenio.modules.previewer',
    'invenio.modules.ranker',
    'invenio.modules.records',
    'invenio.modules.redirector',
    'invenio.modules.refextract',
    'invenio.modules.scheduler',
    'invenio.modules.search',
    'invenio.modules.sequencegenerator',
    'invenio.modules.sorter',
    'invenio.modules.statistics',
    'invenio.modules.submit',
    'invenio.modules.sword',
    'invenio.modules.tags',
    'invenio.modules.textminer',
    'invenio.modules.tickets',
    'invenio.modules.upgrader',
    'invenio.modules.uploader',
    'invenio.modules.webhooks',
    'invenio.modules.workflows',
]

PACKAGES = [
    "lw_daap.base",
    "invenio.base",
    "invenio.modules.*",
]

PACKAGES_EXCLUDE= []

CFG_DATABASE_NAME = "lwdaap"
CFG_DATABASE_USER = "lwdaap"

# <-- Debug toolbar configuration
DEBUG = True
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
# -->

RECORDS_BREADCRUMB_TITLE_KEY = 'title'  

try:
    from lw_daap.instance_config import *
except ImportError:
    pass
