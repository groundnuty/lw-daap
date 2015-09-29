from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

from flask_login import current_user

from invenio.base.i18n import _
from invenio.ext.login.legacy_user import UserInfo
from invenio.ext.sqlalchemy import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

from invenio.modules.accounts.models import User

class userProfile(db.Model):
    __tablename__ = 'userProfile'

    """ Fields """
    user_id = db.Column(db.Integer(255, unsigned=True), db.ForeignKey(User.id),
                        nullable=False, primary_key=True,
                        )

    name = db.Column(db.String(length=255),
                     nullable=True, default='',
                     info=dict(
                            label=_("Name"),
                            description=_(''),
                     ))

    institution = db.Column(db.String(length=255),
                            nullable=True, default='',
                            info=dict(
                                label=_("Institution"),
                                description=_(''),
                            ))

    email = db.Column(db.String(length=255),
                      nullable=True, default='',
                      info=dict(
                            label=_("Contact e-mail"),
                            description=_(''),
                      ))

    social_profiles = db.Column(db.String(length=255),
                                nullable=True, default='',
                                info=dict(
                                    label=_("Social networks"),
                                    description=_(''),
                                ))

    ei_user = db.Column(db.String(length=255),
                        nullable=True, default='',
                        info=dict(
                            label=_("User name"),
                            description=_(''),
                        ))

    ei_pass = db.Column(db.String(length=255),
                        nullable=True, default='',
                        info=dict(
                            label=_("Password"),
                            description=_(''),
                        ))

    user_proxy = db.Column(db.String(length=10000),
                        nullable=True, default='',)

    csr_priv_key = db.Column(db.String(length=10000),
                        nullable=True, default='')

    ssh_public_key = db.Column(db.Text(length=2000),
                               nullable=True, default='',
                               info=dict(
                                   label=_("SSH public key"),
                                   description=_('The ssh public key can be obtained ... COMPLETE THE INSTRUCTIONS!'),
                              ))


    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified = db.Column(db.DateTime, nullable=False, default=datetime.now,
                         onupdate=datetime.now)

    """ Relationships """

    user = db.relationship(
        User, backref=db.backref("userProfile", uselist=False, cascade="all, delete-orphan"))


    @classmethod
    def create(cls):
        try:
            obj = cls(
                user_id = current_user.get_id(),
            )
            db.session.add(obj)
            db.session.commit()
            #PROFILE CREATE SIGNAL
            return obj
        except IntegrityError as e:
            db.session.rollback()
            raise e
        except Exception as e:
            raise e

    @classmethod
    def get(cls):
        try:
            return cls.query.filter_by(user_id=current_user.get_id()).one()
        except NoResultFound:
            return None

    @classmethod
    def get_or_create(cls):
        instance = cls.get()
        if instance:
            return instance
        else:
            return cls.create()

    def update(self, **data):
        for value in data:
            setattr(self, value, data[value])
        try:
            db.session.commit()
            return self;
        except Exception as e:
            raise e
