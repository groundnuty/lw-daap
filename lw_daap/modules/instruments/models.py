from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

from flask_login import current_user
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from invenio.config import CFG_SITE_LANG

from invenio.base.i18n import _
from invenio.ext.sqlalchemy import db
from invenio.modules.accounts.models import User
from invenio.base.globals import cfg

from invenio.modules.search.models import \
    Collection, CollectionCollection, CollectionFormat, Collectionname, Format
from invenio.modules.access.models import \
    AccACTION, AccARGUMENT, AccAuthorization, AccROLE, UserAccROLE
from invenio.modules.access.firerole import compile_role_definition, serialize

from flask import current_app


class Instrument(db.Model):
    __tablename__ = 'instrument'

    """ Fields """
    id = db.Column(db.Integer(255, unsigned=True),
                        nullable=False, primary_key=True,
                        )
    user_id = db.Column(db.Integer(255, unsigned=True), db.ForeignKey(User.id),
                        nullable=False,
                        )

    name = db.Column(db.String(length=255),
                     nullable=True, default='',
                     info=dict(
                         label=_("Name"),
                         description=_(''),
                         )
                     )

    access_right = db.Column(db.String(length=12),
                            nullable=True, default='',
                            info=dict(
                                label=_("Access right"),
                                description=_(''),
                                )
                            )

    embargo_date = db.Column(db.DateTime,
                            nullable=True, default='',
                            info=dict(
                                label=_("Embargo date"),
                                description=_(''),
                                )
                           )

    conditions = db.Column(db.String(length=4000),
                            nullable=True, default='',
                            info=dict(
                                label=_("Conditions"),
                                description=_(''),
                                )
                           )

    license = db.Column(db.String(length=50),
                            nullable=True, default='',
                            info=dict(
                                label=_("License"),
                                description=_(''),
                                )
                           )


    """ Relationships """

    user = db.relationship(
        User, backref=db.backref("instruments", uselist=False,
                                 cascade="all, delete-orphan"))

    #
    # Collection management
    #
    def get_collection_name(self):
        return '%s-%s' % (cfg['INSTRUMENTS_COLLECTION_PREFIX'], self.id)

    def get_collection_dbquery(self):
        return '%s:%s' % ("980__a", self.get_collection_name())

    def get_instrument_records(self, record_types=[], public=None, curated=None):
        """ Return all records of this instruments"""
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

    def save_collectionname(self, collection, name):
        if collection.id:
            c_name = Collectionname.query.filter_by(
                id_collection=collection.id, ln=CFG_SITE_LANG, type='ln'
            ).first()
            if c_name:
                update_changed_fields(c_name, dict(value=name))
                return c_name

        c_name = Collectionname(
            collection=collection,
            ln=CFG_SITE_LANG,
            type='ln',
            value=name,
        )
        db.session.add(c_name)
        return c_name

    def save_collectioncollection(self, collection):
        """Create or update CollectionCollection object."""
        dad = Collection.query.filter_by(
            name=cfg['INSTRUMENTS_PARENT_NAME']).first()

        if collection.id:
            c_tree = CollectionCollection.query.filter_by(
                id_dad=dad.id,
                id_son=collection.id
            ).first()
            if c_tree:
                update_changed_fields(c_tree, dict(
                    type=cfg['INSTRUMENTS_COLLECTION_TYPE'],
                    score=cfg['INSTRUMENTS_COLLECTION_SCORE']))
                return c_tree

        c_tree = CollectionCollection(
            dad=dad,
            son=collection,
            type=cfg['INSTRUMENTS_COLLECTION_TYPE'],
            score=cfg['INSTRUMENTS_COLLECTION_SCORE'],
        )
        db.session.add(c_tree)
        return c_tree

    def save_collectionformat(self, collection):
        """Create or update CollectionFormat object."""
        fmt = Format.query.filter_by(code=cfg['INSTRUMENTS_OUTPUTFORMAT']).first()

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
        role_name = 'instrument_role_%s' % self.id
        role = AccROLE.query.filter_by(name=role_name).first()
        if not role:
            rule = 'allow group "%s"\ndeny any' % self.get_group_name()
            role = AccROLE(
                name=role_name,
                description='Owner of instruments %s' % self.name,
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
                if ur.id_user == self.user_id:
                    db.session.delete(ur)
                else:
                    userrole = ur

        if not userrole:
            userrole = UserAccROLE(id_user=self.user_id, role=role)
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
        self.save_collectionname(c, self.name)
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
        return 'instruments-group-%d' % self.id

    def save_group(self):
        g = self.group
        if not g:
            g = Group.create(self.get_group_name(),
                             description='Group for instruments %s' % self.id,
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
        return self.user_id == uid or self.group.name in groups

    def is_empty(self):
        if self.eresable:
            # Ensure instruments has not records.
            from invenio.legacy.search_engine import search_pattern
            q = '980__:%s' % self.get_collection_name()
            recids = search_pattern(p=q)
            if len(recids) != 0:
                self.eresable = False
                db.session.commit()
                return False
            else:
                return True
        return False

    @classmethod
    def get_instrument(cls, id):
        try:
            return cls.query.get(int(id))
        except ValueError:
            return None

    @classmethod
    def filter_instruments(cls, p, so):
        """Search for instruments.

        Helper function which takes from database only those instruments which
        match search criteria. Uses parameter 'so' to set instruments in the
        correct order.

        Parameter 'page' is introduced to restrict results and return only
        slice of them for the current page. If page == 0 function will return
        all instruments that match the pattern.
        """
        query = cls.query
        if p:
            query = query.filter(db.or_(
                cls.id.like("%" + p + "%"),
                cls.name.like("%" + p + "%"),
            ))
        if so in cfg['INSTRUMENTS_SORTING_OPTIONS']:
            order = so == 'name' and db.asc or db.desc
            query = query.order_by(order(getattr(cls, so)))
        return query

#    @classmethod
#    def get_user_instruments(cls, user):
#        gids = [g.id for g in Group.query_by_uid(user.get_id())]
#        return Instrument.query.filter(Instrument.id_group.in_(gids))


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