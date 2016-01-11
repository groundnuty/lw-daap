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

"""mod_proxy_uwsgi application loader."""

import sys
import urllib

from six.moves.urllib.parse import urlparse

from invenio.base.factory import create_wsgi_app

# You can't write to stdout in mod_wsgi, but some of our
# dependecies do this! (e.g. 4Suite)
sys.stdout = sys.stderr

# This is to fix the way mod_proxy_uwsgi puts a '/' on the PATH_INFO
class WSGIScriptAliasFix(object):
    def __init__(self, app):
        """Initialize wsgi app wrapper."""
        self.app = app

    def __call__(self, environ, start_response):
        """Parse path from ``REQUEST_URI`` to fix ``PATH_INFO``."""
        script_name = environ['SCRIPT_NAME']
        if script_name[-1] == '/':
            script_name = script_name[:-1]
        if environ.get('WSGI_SCRIPT_ALIAS') == script_name:
            path_info = urllib.unquote_plus(
                urlparse(environ.get('REQUEST_URI')).path
            )  # addresses issue with url encoded arguments in Flask routes
            environ['SCRIPT_NAME'] = ''
            environ['PATH_INFO'] = path_info
        return self.app(environ, start_response)


application = create_wsgi_app()
application.wsgi_app = WSGIScriptAliasFix(application.wsgi_app)
