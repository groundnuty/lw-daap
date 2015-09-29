from __future__ import absolute_import

from datetime import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
import humanize
import pytz

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import current_user
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu, current_menu

from invenio.base.i18n import _
from invenio.ext.sslify import ssl_required
from invenio.ext.login import reset_password

from lw_daap.ext.login import login_required

from .forms import  *
from .models import *

CFG_PRIV_KEY_PASSWD = b'lwdaap-passwd'
import re
CERT_RE = re.compile("-----BEGIN CERTIFICATE-----\r?\n"
                     ".+?\r?\n"
                     "-----END CERTIFICATE-----\r?\n?", re.DOTALL)



blueprint = Blueprint(
    'userProfile',
    __name__,
    url_prefix="/account/settings",
    static_folder="static",
    template_folder="templates",
)

def get_client_proxy_info(profile):
    info = {'user_proxy': False}
    if ('SSL_CLIENT_M_SERIAL' not in request.environ or
        'SSL_CLIENT_V_END' not in request.environ or
        'SSL_CLIENT_I_DN' not in request.environ or
        request.environ.get('SSL_CLIENT_VERIFY') != 'SUCCESS'):
        return info
    info['user_dn'] = request.environ['SSL_CLIENT_S_DN']
    info['user_cert'] = request.environ['SSL_CLIENT_CERT']
    if profile.user_proxy:
        px = x509.load_pem_x509_certificate(
            profile.user_proxy.encode('ascii', 'ignore'),
            default_backend()
        )
        time_left = (px.not_valid_after.replace(tzinfo=pytz.utc)
                     - datetime.now(tz=pytz.utc))
        # let's consider a valid proxy if you have at least 10 min
        if time_left.total_seconds > 600:
            info['user_proxy'] = True
            info['user_proxy_time_left'] = humanize.naturaldelta(time_left)
    return info


@blueprint.route("/profile", methods=['GET', 'POST'])
@ssl_required
@login_required
@register_menu(
    blueprint, 'settings.profile',
    _('%(icon)s Profile', icon='<i class="fa fa-user fa-fw"></i>'),
    order=0,
    active_when=lambda: request.endpoint.startswith("userProfile.")
)
@register_breadcrumb(blueprint, 'breadcrumbs.settings.profile', _('Profile'))
def index():
    profile = userProfile.get_or_create()
    form = ProfileForm(request.form, obj=profile)
    if form.validate_on_submit():
        try:
            profile.update(**form.data)
            flash(_('Profile was updated'), 'success')
        except Exception as e:
            flash(str(e), 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                current_app.logger.debug("Error in the %s field - %s" % (
                                         getattr(form, field).label.text,
                                        error))

    ctx = dict(
        form=form,
        profile=profile,
    )
    ctx.update(get_client_proxy_info(profile))
    return render_template(
        "profile/profile.html",
        **ctx
    )

@blueprint.route("/proxy_request")
@ssl_required
@login_required
def csr_request():
    profile = userProfile.get_or_create()

    # Generate our key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # save key pem in profile for later use
    profile.update(csr_priv_key=key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(CFG_PRIV_KEY_PASSWD),
    ))

    # Generate a CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Dummy"),
    ])).sign(key, hashes.SHA256(), default_backend())

    return jsonify(dict(
        csr=csr.public_bytes(serialization.Encoding.PEM)
    ))


@blueprint.route('/delegate-proxy', methods=['POST'])
@ssl_required
@login_required
def delegate_proxy():
    profile = userProfile.get_or_create()
    if not profile.csr_priv_key:
        abort(400)
    try:
        proxy = request.form['x509Proxy']
    except KeyError:
        abort(400)

    pem_chain = CERT_RE.findall(proxy)
    x509_chain = [x509.load_pem_x509_certificate(c.encode('ascii', 'ignore'),
                                                 default_backend())
                  for c in pem_chain]
    if len(x509_chain) < 2:
        # should have 2 certs in the chain
        abort(400)

    proxy = x509_chain[0]
    issuer = x509_chain[1]

    issuer_names = [n for n in proxy.issuer]
    subject_names = [n for n in proxy.subject]

    # should be the same but the last CN
    if issuer_names != subject_names[:-1]:
        abort(400)
    if subject_names[-1].oid != NameOID.COMMON_NAME:
        abort(400)

    private_key = serialization.load_pem_private_key(
        profile.csr_priv_key.encode('ascii'), password=CFG_PRIV_KEY_PASSWD,
        backend=default_backend()
    )

    p_mod = proxy.public_key().public_numbers().n
    priv_mod = private_key.private_numbers().public_numbers.n

    if p_mod != priv_mod:
        # signed with a different key!?
        abort(400)

    # build the new proxy
    new_proxy_chain = [pem_chain[0], profile.csr_priv_key]
    new_proxy_chain.extend(pem_chain[1:])
    profile.update(user_proxy=''.join(new_proxy_chain))

    time_left = (proxy.not_valid_after.replace(tzinfo=pytz.utc)
                 - datetime.now(tz=pytz.utc))

    return jsonify(dict(
        user_proxy=True,
        time_left=humanize.naturaldelta(time_left),
    ))


@blueprint.route('/delete-proxy', methods=['POST'])
@ssl_required
@login_required
def delete_proxy():
    profile = userProfile.get_or_create()
    profile.update(user_proxy=None)
    return ''
