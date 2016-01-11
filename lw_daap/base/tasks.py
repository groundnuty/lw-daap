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


from __future__ import absolute_import

from celery.task.base import PeriodicTask
from celery.utils.log import get_task_logger

from invenio.base.globals import cfg
from invenio.legacy.dbquery import run_sql
from invenio.legacy.bibsched import webapi
from invenio.legacy.bibsched import cli

logger = get_task_logger(__name__)


class BibschedCheck(PeriodicTask):
    """
    Checks that everything is running fine in bibsched and
    sets things back as expected is something weird is found
    """
    run_every = cfg['CFG_LWDAAP_BIBSCHED_CHECK_PERIOD']

    def run(self, *args, **kwargs):
        # clean up queue
        tasks = webapi.get_bibsched_tasks()
        for t in tasks:
            task_id, proc, priority, user, runtime, status, progress = t
            if 'ERROR' in status:
                logger.info("Re-init task %s", task_id)
                cli.bibsched_set_status(task_id, "WAITING")
                cli.bibsched_set_progress(task_id, "")
                cli.bibsched_set_host(task_id, "")

        if webapi.get_bibsched_mode() != 'AUTOMATIC':
            # manual, put it back to auto
            logger.info("Putting back bibsched to auto mode")
            run_sql('UPDATE schSTATUS SET value = "" WHERE '
                    'name = "resume_after"')
            run_sql('UPDATE schSTATUS SET value = "1" WHERE '
                    'name = "auto_mode"')
