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

"""Resolve Period helper functions."""

import datetime
import time

def resolve_period(values, which):
    if not isinstance(values, list):
        values = [values]
    period = []
    for v in values:
        period.append(datetime.date(*(time.strptime(v or '', '%Y-%m-%d')[0:3])))
    if which == 'start':
        return period[0]
    elif which == 'end':
        return period[-1] 
