# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Viavansi S.L..
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
# Some helper functions to deal with Lifewatch service.
#

from invenio.base.globals import cfg
import json
import urllib2, base64

def getServiceJsonParamenters():
    """
    Returns the Lifewatch service parameters in JSON format
    """
    lfw_service = cfg.get('CFG_LFW_SERVICE')
    lfw_service_json = json.dumps(lfw_service)
    lfw_service_json = json.loads(lfw_service_json)
    return lfw_service_json

def getBase64StringAuth(lfw_service_json):
    user = lfw_service_json['lfw_user']
    passw = lfw_service_json['lfw_pass']
    return base64.encodestring('%s:%s' % (user, passw)).replace('\n', '')

def existDBUser(userDB):
    """
    Returns true if the DB user exist in the database
    """
    lfw_service_json = getServiceJsonParamenters();
    lfw_url = lfw_service_json['lfw_service']
    req = urllib2.Request('%sdatabase/existdbuser?dbuser=%s' % (lfw_url, userDB))
    base64string = getBase64StringAuth(lfw_service_json)
    req.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(req)
    if not result.read().strip():
       return False
    else:
       return True

def createDBUser(userDB, passDB):
    """
    Create a database user.
    """
    lfw_service_json = getServiceJsonParamenters()
    lfw_url = lfw_service_json['lfw_service']
    req = urllib2.Request('%s/database/createdbuser?dbuser=%s&dbpassword=%s' % (lfw_url, userDB, passDB))
    base64string = getBase64StringAuth(lfw_service_json)
    req.add_header("Authorization", "Basic %s" % base64string)
    urllib2.urlopen(req)

def changeDBPassword(userDB, passDB):
    """
    Create a database user.
    """
    lfw_service_json = getServiceJsonParamenters()
    lfw_url = lfw_service_json['lfw_service']
    req = urllib2.Request('%s/database/changedbpassword?dbuser=%s&dbpassword=%s' % (lfw_url, userDB, passDB))
    base64string = getBase64StringAuth(lfw_service_json)
    req.add_header("Authorization", "Basic %s" % base64string)
    urllib2.urlopen(req)



def findByDatabaseUser(userDB):
    """
    Returns true if the DB user exist in the database
    """
    lfw_service_json = getServiceJsonParamenters();
    lfw_url = lfw_service_json['lfw_service']
    req = urllib2.Request('%s/user/findbydatabaseuser?databaseUser=%s' % (lfw_url, userDB))
    base64string = getBase64StringAuth(lfw_service_json)
    req.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(req)
    if not result.read().strip():
       return False
    else:
       return True

def findByPortalUser(portalUser):
    """
    Returns true if the Portal user exist in the database
    """
    lfw_service_json = getServiceJsonParamenters();
    lfw_url = lfw_service_json['lfw_service']
    req = urllib2.Request('%suser/findbyportaluser?portalUser=%s' % (lfw_url, portalUser))
    base64string = getBase64StringAuth(lfw_service_json)
    req.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(req)
    if not result.read().strip():
       return False
    else:
       return True

def addUserDB(userDB, portalUser):
    """
    Add a new user to the database
    """
    lfw_service_json = getServiceJsonParamenters()
    lfw_url = lfw_service_json['lfw_service']
    req = urllib2.Request('%s/user/adduser?databaseUser=%s&portalUser=%s' % (lfw_url, userDB, portalUser))
    base64string = getBase64StringAuth(lfw_service_json)
    req.add_header("Authorization", "Basic %s" % base64string)
    urllib2.urlopen(req)

