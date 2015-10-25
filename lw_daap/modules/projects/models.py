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

from datetime import datetime

from invenio.ext.sqlalchemy import db
from invenio.base.globals import cfg
from invenio.config import CFG_SITE_LANG
from invenio.modules.accounts.models import User
from invenio.modules.search.models import \
    Collection, CollectionCollection, \
    CollectionFormat, Collectionname, Format


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

    creation_date = db.Column(db.DateTime(), nullable=False,
                              default=datetime.now)
    """ creation date of the project"""

    modification_date = db.Column(db.DateTime(), nullable=False,
                                  default=datetime.now)
    """ date of last modification"""

    is_public = db.Column(db.Boolean, nullable=False, default=False)
    """ does the project have any public records?"""

    # collection
    id_collection = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(Collection.id),
        nullable=True, default=None
    )
    collection = db.relationship(
        Collection, uselist=False, backref='project',
        foreign_keys=[id_collection]
    )

    # owner
    id_user = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(User.id),
        nullable=False
    )
    owner = db.relationship(User, backref='projects',
                            foreign_keys=[id_user])


    #
    # Collection management
    #
    def get_collection_name(self):
        return '%s-%s' % (cfg['PROJECTS_COLLECTION_PREFIX'], self.id)

    def get_collection_dbquery(self):
        return '%s:%s' % ("980__a", self.get_collection_name())

    def save_collectionname(self, collection, title):
        if collection.id:
            c_name = Collectionname.query.filter_by(
                id_collection=collection.id, ln=CFG_SITE_LANG, type='ln'
            ).first()
            if c_name:
                update_changed_fields(c_name, dict(value=title))
                return c_name

        c_name = Collectionname(
            collection=collection,
            ln=CFG_SITE_LANG,
            type='ln',
            value=title,
        )
        db.session.add(c_name)
        return c_name
    
    def save_collectioncollection(self, collection):
        """Create or update CollectionCollection object."""
        dad = Collection.query.filter_by(
            name=cfg['PROJECTS_PARENT_NAME']).first()

        if collection.id:
            c_tree = CollectionCollection.query.filter_by(
                id_dad=dad.id,
                id_son=collection.id
            ).first()
            if c_tree:
                update_changed_fields(c_tree, dict(
                    type=cfg['PROJECTS_COLLECTION_TYPE'],
                    score=cfg['PROJECTS_COLLECTION_SCORE']))
                return c_tree

        c_tree = CollectionCollection(
            dad=dad,
            son=collection,
            type=cfg['PROJECTS_COLLECTION_TYPE'],
            score=cfg['PROJECTS_COLLECTION_SCORE'],
        )
        db.session.add(c_tree)
        return c_tree

    def save_collectionformat(self, collection):
        """Create or update CollectionFormat object."""
        fmt = Format.query.filter_by(code=cfg['PROJECTS_OUTPUTFORMAT']).first()

        if collection.id:
            c_fmt = CollectionFormat.query.filter_by(
                id_collection=collection.id
            ).first()
            if c_fmt:
                update_changed_fields(c_fmt, dict(id_format=fmt.id, score=1))
                return c_fmt

        c_fmt = CollectionFormat(
            collection=collection,
            id_format=fmt.id,
        )
        db.session.add(c_fmt)
        return c_fmt

    def save_collection(self):
        collection_name = self.get_collection_name()
        c = Collection.query.filter_by(name=collection_name).first()
        fields = dict(
            name=collection_name,
            dbquery=self.get_collection_dbquery()
        ) 
        if c:
            update_changed_fields(c, fields)
        else:
            c = Collection(**fields)
            db.session.add(c)
            db.session.commit()
        self.collection = c
        self.save_collectionname(c, self.title)
        self.save_collectioncollection(c)
        self.save_collectionformat(c)
        db.session.commit()

    def delete_collection(self):
        if self.collection:
            CollectionFormat.query.filter_by(
                id_collection=self.collection.id).delete()
            Collectionname.query.filter_by(
                id_collection=self.collection.id).delete()
            CollectionCollection.query.filter_by(
                id_son=self.collection.id).delete()
            db.session.delete(self.collection)
            db.session.commit()

    @classmethod
    def filter_projects(cls, p=None, so=None):
        # TODO
        return cls.query.filter()

#
#
#
def update_changed_fields(obj, fields):
    """Utility method to update fields on an object if they have changed.

    Will also report back if any changes where made.
    """
    dirty = False
    for attr, newval in fields.items():
        val = getattr(obj, attr)
        if val != newval:
            setattr(obj, attr, newval)
            dirty = True
    return dirty
