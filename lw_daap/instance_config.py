#
# Add here any relevant configuration that needs to be overriden
# for deployment
#

#
# Site URLs
# These _MUST_ be set for proper redirection to login
CFG_SITE_URL = 'http://localhost'
CFG_SITE_SECURE_URL = 'https://localhost'

#
# Configure here the emails shown for contact in the portal
CFG_SITE_SUPPORT_EMAIL = "support-lwosf@someserver.com"
CFG_SITE_ADMIN_EMAIL = "admin-lwosf@someserver.com"

#
# Database configuration
# use "db" as CFG_DATABASE_HOST if using the mysql from the docker container
#
CFG_DATABASE_HOST = 'db'
CFG_DATABASE_NAME = 'lwosf'
CFG_DATABASE_USER = 'lwosf'
CFG_DATABASE_PASS = u'my123p$ss'
CFG_DATABASE_TYPE = u'mysql'
CFG_DATABASE_PORT = 3306

#
# IDP entity IDs.
#
CFG_IDP_LIFEWATCH = 'http://lifewatch.idp:8080/idp/shibboleth'
CFG_IDP_CSIC = 'http://csic.idp:8080/idp/shibboleth'

#
# Use here the URL of the DMPTool instance
#
CFG_DMPTOOL_URL = 'http://localhost/dmptool'

#
# emails configuration
#
# 'flask_email.backends.console.Mail' does not send emails but shows them in
# the console
# 'flask_email.backends.smtp.Mail' sends them with SMTP.
CFG_EMAIL_BACKEND = 'flask_email.backends.console.Mail'

# When using flask_email.backends.smtp.Mail
# set also the following variables:
# CFG_MISCUTIL_SMTP_HOST = "smtp.hostname.com"
# CFG_MISCUTIL_SMTP_PORT = 22
# CFG_MISCUTIL_SMTP_USER = "username"
# CFG_MISCUTIL_SMTP_PASS = "userpassword"
# CFG_MISCUTIL_SMTP_TLS = False


#
# OpenStack Configuration
#
#CFG_OPENSTACK_AUTH_URL = "https://localhost:5000/v2.0"
#CFG_OPENSTACK_TENANT = "tenant"

# Set here the URL for the bridge machine
#CFG_ANALYZE_ETCD_URL = 'http://localhost:4001'

#
# Github integration
#
#GITHUB_APP_CREDENTIALS = dict(
#   consumer_key="...",
#   consumer_secret="...",
#)

#
# Dropbox integration
#
#DEPOSIT_DROPBOX_API_KEY = "..."

#
# Mapbox integration (displaying maps on records)
#
#MAPBOX_API_TOKEN = "..."
#MAPBOX_API_APP = "..."
