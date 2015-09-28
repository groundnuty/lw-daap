
from invenio.ext.assets import Bundle, RequireJSFilter
from invenio.base.bundles import jquery as _j, invenio as _i

js = Bundle(
    "js/profile/proxy.js",
    output="profile.js",
    filters=RequireJSFilter(exclude=[_j, _i]),
    weight=51,
    bower={
        "asn1js": "latest",
        "jsrsasign": "latest",
        "jquery-validation": "latest",
    },
)

