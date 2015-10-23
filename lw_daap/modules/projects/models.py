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

from invenio.ext.sqlalchemy import db
from invenio.modules.accounts.models import User
from invenio.modules.search.models import Collection

from invenio.modules.workflows.models import BibWorkflowObject, Workflow

class DepositionError(Exception):
    """Base class for deposition errors."""
    pass

class InvalidDepositionType(DepositionError):
    """Raise when a deposition type cannot be found."""
    pass

class Project(db.Model):
    """
    Represents a project
    """
    __tablename__ = 'project'

    id = db.Column(db.Integer(15, unsigned=True), primary_key=True)
    """Project id"""

    title = db.Column(db.String(length=255), nullable=False, default='')
    """ Project title """

    description = db.Column(db.Text(), nullable=False, default='')
    """ Project short description """

    # collection
    #id_collection = db.Column(
    #    db.Integer(15, unsigned=True), db.ForeignKey(Collection.id),
    #    nullable=True, default=None
    #)
    #collection = db.relationship(
    #    Collection, uselist=False, backref='community',
    #    foreign_keys=[id_collection]
    #)

    # owner
    #id_user = db.Column(
    #    db.Integer(15, unsigned=True), db.ForeignKey(User.id),
    #    nullable=False
    #)
    #owner = db.relationship(User, backref='communities',
    #                        foreign_keys=[id_user])

    @classmethod
    def get_projects(cls, user=None, type=None):
        params = [
            Workflow.module_name == 'webdeposit',
        ]

        if user:
            params.append(BibWorkflowObject.id_user == user.get_id())
        else:
            params.append(BibWorkflowObject.id_user != 0)

        if type:
            params.append(Workflow.name == type.get_identifier())

        objects = BibWorkflowObject.query.join("workflow").options(
            db.contains_eager('workflow')).filter(*params).order_by(
            BibWorkflowObject.modified.desc()).all()

        #def _create_obj(o):
        #    try:
        #        obj = cls(o)
        #    except InvalidDepositionType as err:
        #        current_app.logger.exception(err)
        #        return None
        #    if type is None or obj.type == type:
        #        return obj
        #    return None

        #return filter(lambda x: x is not None, map(_create_obj, objects))
        return "myfirstproject"

