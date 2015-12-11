__author__ = 'Rafael'

from invenio.base.globals import cfg
import json
import urllib2, base64, urllib
from flask import current_app

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

def createInstrument(name, embargoDate, accessRight, idUser, license, conditions, databaseUser, portalUser):
    """
    Create an instruments
    """
    lfw_service_json = getServiceJsonParamenters();
    lfw_url = lfw_service_json['lfw_service']
    
    url = '%sinstrument' % (lfw_url)
    req = urllib2.Request(url)
    f = {'name' : name,
         'embargoDate' : embargoDate,
         'accessRight' : accessRight,
         'idUser' : idUser,
         'license' : license,
         'conditions' : conditions,
         'owner': {
             'idUser': idUser,
             'databaseUser': databaseUser,
             'portalUser': portalUser
         }
        }
    data = urllib.urlencode(f)

    base64string = getBase64StringAuth(lfw_service_json)
    req.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(req, data=data)

    if result.read().strip() == "false":
       return False
    else:
       return True

def getAllInstruments():
    """
    Get all instruments
    """
    lfw_service_json = getServiceJsonParamenters()
    lfw_url = lfw_service_json['lfw_service']
    req = urllib2.Request('%s/instruments' % lfw_url)
    base64string = getBase64StringAuth(lfw_service_json)
    req.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(req)
    return result.read().strip()