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

import json

from flask import current_app


def format_element(bfo, spatial=[]):
    if not spatial:
        return ''
    norths = []
    souths = []
    easts = []
    wests = []
    polygons = []
    markers = []
    coords = ((float(c['north']), float(c['south']),
               float(c['east']), float(c['west'])) for c in spatial)
    current_app.logger.debug("COORDS: %s" % coords)
    for n, s, e, w in coords:
        norths.append(n)
        souths.append(s)
        easts.append(e)
        wests.append(w)
        if n == s and e == w:
            markers.append((n, w))
        else:
            polygons.append(((n, w), (s, w), (s, e), (n, e)))
    center = (((max(norths) + min(souths)) / 2.),
              ((max(easts) + min(wests)) / 2.))
    bounds = ((min(souths), min(wests)), (max(norths), max(easts)))    
    r = ["<div id='spatial'",
         "class='map'",
         "data-center='%s'" % json.dumps(center),
         "data-polygons='%s'" % json.dumps(polygons),
         "data-markers='%s'" % json.dumps(markers),
         "data-bounds='%s'" % json.dumps(bounds),   
         "></div>",
        ]
    return ' '.join(r)


def escape_values(bfo):
    return 0

