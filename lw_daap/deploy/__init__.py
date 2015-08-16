
from __future__ import absolute_import

from .receivers import post_handler_demosite_populate, \
    post_handler_database_create, clean_data_files
from invenio.base.scripts.demosite import populate
from invenio.base.scripts.database import create, recreate, drop, init
from invenio.base.signals import post_command

post_command.connect(post_handler_demosite_populate, sender=populate)
post_command.connect(post_handler_database_create, sender=create)
post_command.connect(post_handler_database_create, sender=recreate)
post_command.connect(clean_data_files, sender=init)
post_command.connect(clean_data_files, sender=drop)
