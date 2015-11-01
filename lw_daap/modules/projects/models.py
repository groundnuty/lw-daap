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

from invenio.base.globals import cfg
from invenio.config import CFG_SITE_LANG
from invenio.ext.sqlalchemy import db
from invenio.modules.access.firerole import compile_role_definition, serialize
from invenio.modules.access.models import \
    AccACTION, AccARGUMENT, AccAuthorization, AccROLE, UserAccROLE
from invenio.modules.accounts.models import User
from invenio.modules.search.models import \
    Collection, CollectionCollection, CollectionFormat, Collectionname, Format

from lw_daap.modules.invenio_groups.models import \
    Group, PrivacyPolicy, SubscriptionPolicy

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

    # group
    id_group = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(Group.id),
        nullable=True, default=None
    )
    group = db.relationship(Group, backref='projects',
                            foreign_keys=[id_group])

    #
    # Collection management
    #
    def get_collection_name(self):
        return '%s-%s' % (cfg['PROJECTS_COLLECTION_PREFIX'], self.id)

    def get_collection_dbquery(self):
        return '%s:%s' % ("980__a", self.get_collection_name())

    def get_project_records(self, record_types=[], public=None, curated=None):
        """ Return all records of this project"""
        from invenio.legacy.search_engine import search_pattern_parenthesised
        from invenio.modules.records.models import Record
        q = ['980__:%s' % self.get_collection_name()]
        if record_types:
            qtypes = ['980__:%s' % t for t in record_types]
            if len(qtypes) > 1:
                q.append('(%s)' % ' OR '.join(qtypes))
            else:
                q.extend(qtypes)
        if public is not None:
            q.append('983__b:%s' % public)
        if curated is not None:
            q.append('983__a:%s' % curated)
        p = (' AND '.join(q))
        recids = search_pattern_parenthesised(p=p)
        records = Record.query.filter(Record.id.in_(recids))
        return records

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

    def save_acl(self, c):
        # Role - use Community id, because role name is limited to 32 chars.
        role_name = 'project_role_%s' % self.id
        role = AccROLE.query.filter_by(name=role_name).first()
        if not role:
            rule = 'allow group "%s"\ndeny any' % self.get_group_name()
            role = AccROLE(
                name=role_name,
                description='Owner of project %s' % self.title,
                firerole_def_ser=serialize(compile_role_definition(rule)),
                firerole_def_src=rule)
            db.session.add(role)

        # Argument
        fields = dict(keyword='collection', value=c.name)
        arg = AccARGUMENT.query.filter_by(**fields).first()
        if not arg:
            arg = AccARGUMENT(**fields)
            db.session.add(arg)

        # Action
        action = AccACTION.query.filter_by(name='viewrestrcoll').first()

        # User role
        alluserroles = UserAccROLE.query.filter_by(role=role).all()
        userrole = None
        if alluserroles:
            # Remove any user which is not the owner
            for ur in alluserroles:
                if ur.id_user == self.id_user:
                    db.session.delete(ur)
                else:
                    userrole = ur

        if not userrole:
            userrole = UserAccROLE(id_user=self.id_user, role=role)
            db.session.add(userrole)

        # Authorization
        auth = AccAuthorization.query.filter_by(role=role, action=action,
                                                argument=arg).first()
        if not auth:
            auth = AccAuthorization(role=role, action=action, argument=arg,
                                    argumentlistid=1)

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
        self.save_acl(c)
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

    def get_group_name(self):
        return 'project-group-%d' % self.id

    def save_group(self):
        g = self.group
        if not g:
            g = Group.create(self.get_group_name(),
                             description='Group for project %s' % self.id,
                             privacy_policy=PrivacyPolicy.MEMBERS,
                             subscription_policy=SubscriptionPolicy.APPROVAL,
                             is_managed=False,
                             admins=[self.owner])
            g.add_member(self.owner)
            self.group = g
            db.session.commit()

    def is_user_allowed(self, user=None):
        if not user:
            from flask_login import current_user
            user = current_user
        uid = user.get_id()
        groups = user.get('group', [])
        return self.id_user == uid or self.group.name in groups

    @classmethod
    def get_project_by_collection(cls, collection):
        prefix = '%s-' % cfg['PROJECTS_COLLECTION_PREFIX']
        id = collection[collection.startswith(prefix) and len(prefix):]
        return cls.query.get(id)

    @classmethod
    def get_name_by_collection(cls, collection):
        return cls.get_project_by_collection(collection).title

    @classmethod
    def get_project_by_id(cls, id):
        return cls.query.get('2args')

    @classmethod
    def filter_projects(cls, p, so):
        """Search for projects.

        Helper function which takes from database only those projects which
        match search criteria. Uses parameter 'so' to set projects in the
        correct order.

        Parameter 'page' is introduced to restrict results and return only
        slice of them for the current page. If page == 0 function will return
        all projects that match the pattern.
        """
        query = cls.query
        if p:
            query = query.filter(db.or_(
                cls.id.like("%" + p + "%"),
                cls.title.like("%" + p + "%"),
                cls.description.like("%" + p + "%"),
            ))
        if so in cfg['PROJECTS_SORTING_OPTIONS']:
            order = so == 'title' and db.asc or db.desc
            query = query.order_by(order(getattr(cls, so)))
        return query

    @classmethod
    def get_user_projects(cls, user):
        gids = [g.id for g in Group.query_by_uid(user.get_id())]
        return Project.query.filter(Project.id_group.in_(gids))


#
# Directly taken from invenio.modules.communities
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
