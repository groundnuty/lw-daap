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

#
#

from fixture import DataSet
from invenio.modules.search import fixtures as default

siteCollection = default.CollectionData.siteCollection

siteCollection.dbquery = '980__a:community-*'

class CollectionData(DataSet):
    class analysis(object):
        id = 2
        name = 'Analysis'
        dbquery = '980__a:analysis AND 980__a:community-*' 

    class dataset(object):
        id = 3
        name = 'Dataset'
        dbquery = '980__a:dataset AND 980__a:community-*'

    class software(object):
        id = 4
        name = 'Software'
        dbquery = '980__a:software AND 980__a:community-*'

    class dmp(object):
        id = 5
        name = 'DMP'
        dbquery = '980__a:dmp AND 980__a:community-*'

    class communityparent(object):
        id = 6
        name = 'Communities'



class CollectionCollectionData(DataSet):
    class site_analysis:
        dad = siteCollection
        son = CollectionData.analysis
        score = 0
        type = 'r'

    class site_dataset:
        dad = siteCollection
        son = CollectionData.dataset
        score = 0
        type = 'r'

    class site_software:
        dad = siteCollection
        son = CollectionData.software
        score = 0
        type = 'r'

    class site_dataset:
        dad = siteCollection
        son = CollectionData.dmp
        score = 0
        type = 'r'
