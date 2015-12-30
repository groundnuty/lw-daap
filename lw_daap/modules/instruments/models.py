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

from lw_daap.modules.deposit.fields.access_rights_field import ACCESS_RIGHTS_CHOICES
from lw_daap.modules.deposit.fields.license_field import _kb_license_choices
from .forms import InstrumentForm
from invenio.base.helpers import unicodifier
from werkzeug.datastructures import MultiDict
from .service_utils import findGroupByInstrumentId

CFG_FIELD_FLAGS = [
    'hidden',
    'disabled'
]

class DepositionError(Exception):
    """Base class for deposition errors."""
    pass

class FormDoesNotExists(DepositionError):
    """Raise when a draft does not exists."""
    pass


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

    access_conditions = db.Column(db.String(length=4000),
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

    form_class = InstrumentForm

    flags = {}

    values = {}



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
    def get_or_create(cls):
        instance = cls.get()
        if instance:
            return instance
        else:
            return cls.create()

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


    def get_access_right(self):
        for tuple in ACCESS_RIGHTS_CHOICES:
            if tuple[0] == self.access_right:
                return tuple[1]

    def get_license(self):
        licenses = _kb_license_choices(True, True, True)
        for tuple in licenses:
            if tuple[0] == self.license:
                return tuple[1]

    def get_groups(self):
        import json
        groups = findGroupByInstrumentId(self.id)
        groups_text = ""
        for group in json.loads(groups):
            groups_text += group['name'] + " | "
        return groups_text[:-3]

    def complete(self):
        """
        Set state of draft to completed.
        """
        self.completed = True

    def get_form(self, formdata=None, load_draft=True,
                 validate_draft=False):
        """
        Create form instance with draft data and form data if provided.

        :param formdata: Incoming form data.
        :param files: Files to ingest into form
        :param load_draft: True to initialize form with draft data.
        :param validate_draft: Set to true to validate draft data, when no form
             data is provided.
        """
        if not self.has_form():
            raise FormDoesNotExists(self.id)

        draft_data = unicodifier(self.values) if load_draft else {}
        formdata = MultiDict(formdata or {})

        form = self.form_class(
            formdata=formdata, **draft_data
        )

        if formdata:
            form.reset_field_data(exclude=formdata.keys())

        # Set field flags
        if load_draft and self.flags:
            form.set_flags(self.flags)

        if validate_draft and draft_data and formdata is None:
            form.validate()

        return form

    def has_form(self):
        return self.form_class is not None

    def process(self, data, complete_form=False):
        """
        Process, validate and store incoming form data and return response.
        """


        # The form is initialized with form and draft data. The original
        # draft_data is accessible in Field.object_data, Field.raw_data is the
        # new form data and Field.data is the processed form data or the
        # original draft data.
        #
        # Behind the scences, Form.process() is called, which in turns call
        # Field.process_data(), Field.process_formdata() and any filters
        # defined.
        #
        # Field.object_data contains the value of process_data(), while
        # Field.data contains the value of process_formdata() and any filters
        # applied.


        # Run form validation which will call Field.pre_valiate(),
        # Field.validators, Form.validate_<field>() and Field.post_validate().
        # Afterwards Field.data has been validated and any errors will be
        # present in Field.errors.
        # validated = form.validate()
        form = self.get_form(formdata=data)
        validated = form.validate()

        # Call Form.run_processors() which in turn will call
        # Field.run_processors() that allow fields to set flags (hide/show)
        # and values of other fields after the entire formdata has been
        # processed and validated.
        validated_flags, validated_data, validated_msgs = (
            form.get_flags(), form.data, form.messages
        )

        form.post_process(formfields=[] if complete_form else data.keys())
        post_processed_flags, post_processed_data, post_processed_msgs = (
            form.get_flags(), form.data, form.messages
        )

        # Save form values
        self.update(form)

        # Build result dictionary
        process_field_names = None if complete_form else data.keys()


        # Determine if some fields where changed during post-processing.
        changed_values = dict(
            (name, value) for name, value in post_processed_data.items()
            if validated_data[name] != value
        )

        # Determine changed flags
        changed_flags = dict(
            (name, flags) for name, flags in post_processed_flags.items()
            if validated_flags.get(name, []) != flags
        )
        # Determine changed messages
        changed_msgs = dict(
            (name, messages) for name, messages in post_processed_msgs.items()
            if validated_msgs.get(name, []) != messages or
            process_field_names is None or name in process_field_names
        )

        result = {}


        if changed_msgs:
            result['messages'] = changed_msgs
        if changed_values:
            result['values'] = changed_values


        if 'access_right' in data:
            if post_processed_data['access_right'] == 'open':
                result['hidden_off'] = ['name', 'license', 'access_right']
                result['hidden_on'] = ['embargo_date', 'access_groups', 'access_conditions']
                result['disabled_off'] = ['name', 'license', 'access_right']
                result['disabled_on'] = ['embargo_date', 'access_groups', 'access_conditions']
            if post_processed_data['access_right'] == 'embargoed':
                result['hidden_off'] = ['name', 'license', 'access_right', 'embargo_date']
                result['hidden_on'] = ['access_groups', 'access_conditions']
                result['disabled_off'] = ['name', 'license', 'access_right', 'embargo_date']
                result['disabled_on'] = ['access_groups', 'access_conditions']
            if post_processed_data['access_right'] == 'restricted':
                result['hidden_off'] = ['name', 'access_right', 'access_groups', 'access_conditions']
                result['hidden_on'] = ['license', 'embargo_date']
                result['disabled_off'] = ['name', 'access_right', 'access_groups', 'access_conditions']
                result['disabled_on'] = ['license', 'embargo_date']
            if post_processed_data['access_right'] == 'closed':
                result['hidden_off'] = ['name', 'access_right']
                result['hidden_on'] = ['access_groups', 'access_conditions', 'license', 'embargo_date']
                result['disabled_off'] = ['name', 'access_right']
                result['disabled_on'] = ['access_groups', 'access_conditions', 'license', 'embargo_date']

        return form, validated, result

    def update(self, form):
        """
        Update draft values and flags with data from form.
        """
        data = dict((key, value) for key, value in form.data.items()
                    if value is not None)
        self.values = data
        self.flags = form.get_flags()

    def __str__(self):
        instrumentStr = self.name + ',' + self.access_right + ',' + \
                        self.access_conditions + ',' + self.license + ',' + str(self.embargo_date)
        return instrumentStr