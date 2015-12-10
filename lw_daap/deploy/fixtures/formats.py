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
# add hbpro format
#

from invenio.modules.search import fixtures as defaults


class FormatData(defaults.FormatData):
    class FormatHBPro:
        code = u'hbpro'
        last_updated = None
        description = (u'HTML brief output format provisional,'
                       'used for curation.')

        content_type = u'text/html'
        visibility = 1
        name = u'HTML brief Provisional'

    class FormatHBPrj:
        code = u'hbprj'
        last_updated = None
        description = (u'HTML brief output format project,'
                       'used in project views.')
        content_type = u'text/html'
        visibility = 1
        name = u'HTML brief Project'

    class FormatHBIns:
        code = u'hbins'
        last_updated = None
        description = (u'HTML brief output format instrument,'
                       'used in instrument views.')
        content_type = u'text/html'
        visibility = 1
        name = u'HTML brief Instrument'
