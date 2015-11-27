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

"""Validation functions."""
from wtforms_components import DateRange


class StartEndDate(DateRange):

    """Require start date before end date."""

    def __init__(self, min_from=None, max_from=None, **kwargs):
        super(StartEndDate, self).__init__(**kwargs)
        self.min_from = min_from
        self.max_from = max_from

    def __call__(self, form, field):
        if self.min_from:
            self.min = getattr(form, self.min_from).data
        if self.max_from:
            self.max = getattr(form, self.max_from).data
        super(StartEndDate, self).__call__(form, field)
