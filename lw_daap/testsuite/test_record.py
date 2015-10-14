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

from __future__ import print_function, absolute_import
import copy

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase

from flask import url_for

rec = {'provisional_communities': ['zenodo'], 'doi': '10.5072/lw_daap.132', u'description': u'<p>sdfds</p>', u'license': {'url': u'http://www.opendefinition.org/licenses/cc-zero', 'source': 'opendefinition.org', 'identifier': u'cc-zero', 'license': u'Creative Commons CCZero'}, u'title': u'asd', 'grants': [], 'fft': [{'comment': '0', u'path': u'/home/ubuntu/.virtualenvs/daap/var/data/deposit/storage/72/7b63a9a3-5b0c-4ec4-897a-d44e94363419-AC_Raiz_FNMT-RCM_SHA256.cer', u'name': u'AC_Raiz_FNMT-RCM_SHA256', 'restriction': ''}], u'access_right': u'open', 'thesis_supervisors': [], u'keywords': [], 'owner': {'username': u'admin', 'deposition_id': 72L, 'id': 1L, 'email': u'info@invenio-software.org'}, u'subjects': [], 'recid': 132L,  'contributors': [], u'authors': [{u'affiliation': u'asd', u'name': u'asd,asd'}], 'communities': [], u'publication_date': u'2015-08-20', '_additional_authors': [], '_first_author': {u'affiliation': u'asd', u'name': u'asd,asd'}, 'related_identifiers': [],
"communities": ['unacom'],
#'upload_type': {'type': 'publication', 'publication_type': 'book'} 
'upload_type': 'dataset',
}

class RecordTest(InvenioTestCase):
    def test_make_record(self):
        from invenio.modules.records.api import Record
        record = Record(json=rec, master_format='marc')
        marc = record.produce('json_for_marc')
        print("MARC: %s" % marc)
        print("DOI: %s" % record.get('doi'))
        print("UPLOAD TYPE: %s" % record.get('upload_type', ''))
        print("PRE: %s" % rec.get('upload_type', ''))
        print("LEGACY: %s" % record.legacy_export_as_marc())
        self.assertTrue(False)


TEST_SUITE = make_test_suite(RecordTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
