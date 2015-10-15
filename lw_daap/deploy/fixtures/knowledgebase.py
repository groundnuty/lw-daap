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

## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from __future__ import absolute_import
from fixture import DataSet
import csv
from os.path import dirname, join


class KnwKBData(DataSet):
    class licenses:
        id = 1
        name = "licenses"
        description = ""
        type = "w"

    class requirements:
        id = 2
        name = "requirements"
        description = ""
        type = "w"

class KnwKBRVALData(DataSet):
    pass
    """ Install license data into knowledge base """


data = (
    ('kb_licenses.csv', KnwKBData.licenses.id),
    ('kb_requirements.csv', KnwKBData.requirements.id),
)

idx = 0
for filename, kb_id in data:
    with open(join(dirname(__file__), filename), 'r') as f:
        reader = csv.reader(
            f, delimiter=',', quotechar='"', doublequote=False, escapechar='\\'
        )
        for row in reader:
            class obj:
                m_key = row[1]
                m_value = row[2]
                id_knwKB = kb_id
            obj.__name__ = "kbval{0}".format(idx)
            setattr(KnwKBRVALData, obj.__name__, obj)
            idx += 1
