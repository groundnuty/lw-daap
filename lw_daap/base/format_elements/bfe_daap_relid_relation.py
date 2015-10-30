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

from wtforms import widgets


def format_element(bfo, relation={}):
    choices = {
        'isCitedBy': 'cites this upload',
        'cites': 'is cited by this upload',
        'isSupplementTo': 'is supplemented by this upload',
        'isSupplementedBy': 'is a supplement to this upload',
        'isNewVersionOf': 'is previous version of this upload',
        'isPreviousVersionOf': 'is new version of this upload',
        'isPartOf': 'has this upload as part',
        'hasPart': 'is part of this upload',
        'isAnaBy': 'is analyzed by this upload',
        'analyzes': 'analyzes this upload',
        'isCompiledBy': 'compiled/created this upload',
        'compiles': 'is compiled/created by this upload',
        'isIdenticalTo': 'is identical to upload',
        'isAlternativeIdentifier': 'is alternate identifier',
        }
    return choices[relation]


def escape_values(bfo):
    return 0
