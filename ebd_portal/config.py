CFG_SITE_LANGS = ["en"]

CFG_SITE_NAME = "Open Data Portal EBD"
CFG_SITE_NAME_INTL = {
    "en": CFG_SITE_NAME
}

PACKAGES = [
    "ebd_portal.base",
    "invenio.modules.*",
    "invenio.base",
]

CFG_DATABASE_NAME = "ebd"
CFG_DATABASE_USER = "ebd"

# <-- Debug toolbar configuration
DEBUG = True
DEBUG_TB_ENABLED = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
# -->

RECORDS_BREADCRUMB_TITLE_KEY = 'title'  

try:
    from ebd_portal.instance_config import *
except ImportError:
    pass
