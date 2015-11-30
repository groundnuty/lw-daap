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

from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

from flask_login import current_user
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from invenio.base.i18n import _
from invenio.ext.sqlalchemy import db
from invenio.modules.accounts.models import User


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

    access_right = db.Column(db.String(length=255),
                            nullable=True, default='',
                            info=dict(
                                label=_("Access right"),
                                description=_(''),
                                )
                            )

    embargo_date = db.Column(db.DateTime, nullable=True)

    conditions = db.Column(db.String(length=4000),
                            nullable=True, default='',
                            info=dict(
                                label=_("Conditions"),
                                description=_(''),
                                )
                           )

    license = db.Column(db.Integer(2, unsigned=True),
                            nullable=True, default='',
                            info=dict(
                                label=_("License"),
                                description=_(''),
                                )
                           )


    """ Relationships """

    user = db.relationship(
        User, backref=db.backref("instrument", uselist=False,
                                 cascade="all, delete-orphan"))

    @classmethod
    def create(cls):
        try:
            obj = cls(
                user_id=current_user.get_id(),
            )
            db.session.add(obj)
            db.session.commit()
            # PROFILE CREATE SIGNAL
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
            return self
        except Exception as e:
            raise e
