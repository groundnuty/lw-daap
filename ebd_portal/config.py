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

try:
    from ebd_portal.instance_config import *
except ImportError:
    pass
