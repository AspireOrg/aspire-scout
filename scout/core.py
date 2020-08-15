from bson import Int64
from copy import copy
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_EVEN, getcontext
from decimal import Decimal as PyDecimal
from flask_mongoengine import MongoEngine
from flask import request
from flask_assets import Environment
from flask_jwt import JWT
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from functools import wraps
from cachelib.file import FileSystemCache
from mongoengine.base import BaseField
from mongoengine.errors import SaveConditionError
import logging
import itertools
import json

from scout.libs.redislib import RedisLib
from scout.libs.aspire import Aspire


db = MongoEngine()
assets = Environment()
limiter = Limiter(key_func=get_ipaddr)
redis = RedisLib()
cache = FileSystemCache('./.cache/')
logger = logging.getLogger('scout')
formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
aspire = Aspire()


def UTC():
    return datetime.now(timezone.utc)


def ignored_default(default_val, *exceptions):
    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exceptions:
                return default_val
        return _dec
    return dec


class DecimalQuerySet(db.QuerySet):

    def average(self, *args, **kwargs):
        return long_to_decimal(int(super().average(*args, **kwargs)))

    def sum(self, *args, **kwargs):
        return long_to_decimal(int(super().sum(*args, **kwargs)))

    def api_pagination(self, request, limit_max=100, limit_min=1, limit_default=None):
        if limit_default is None:
            limit_default = limit_max

        sint = ignored_default(limit_default, ValueError)(int)
        limit = sint(request.args.get("limit", limit_default))
        if limit > limit_max:
            limit = limit_max
        elif limit < limit_min:
            limit = limit_min
        if limit < 1:
            limit = 1

        sint = ignored_default(1, ValueError)(int)
        skip = (sint(request.args.get("page", 1)) * limit) - limit
        if skip < 0:
            skip = 0
        self.no_sub_classes()

        return self.only(*self._document._serialize).skip(skip).limit(limit)


class DocumentLockError(Exception):
    pass


class Note(db.DynamicEmbeddedDocument):
    note = db.StringField(required=True)
    date = db.DateTimeField(default=UTC, required=True)
    added_by = db.ReferenceField('User')


class Document(db.DynamicDocument):
    locked = db.BooleanField(default=False)
    modified = db.DateTimeField(default=UTC, required=True)
    created = db.DateTimeField(default=UTC, required=True)
    notes = db.ListField(db.EmbeddedDocumentField(Note))

    meta = {
        "allow_inheritance": True,
        "abstract": True,
        "queryset_class": DecimalQuerySet
    }

    def clean(self):
        for name, item in self._fields.items():
            if not isinstance(item, CryptoDecimalField):
                continue

            val = getattr(self, name)
            if not val:
                continue

            if item.min_value and val < item.min_value:
                raise ApiValidationError("%s must be at least %0.8f" % (item.human_name, item.min_value))

            if item.max_value and val > item.max_value:
                raise ApiValidationError("%s must be less than %0.8f" % (item.human_name, item.min_value))

    # DO NOT OVERWRITE THIS PLEASE.
    # PREVENTS TWO THINGS FROM MODIFYING THE SAME DOCUMENT AT THE SAME TIME.
    def save(self, *args, save_condition=dict(), expected_lock=False, **kwargs):

        save_condition["locked"] = expected_lock

        if self.modified is not None:
            save_condition["modified"] = self.modified
            self.modified = UTC()

        return super().save(save_condition=save_condition, *args, **kwargs)

    # MAKES SURE TO UPDATE THE MODIFIED FIELD SO THAT THE ABOVE WORKS AS WELL.
    def modify(self, query={}, **update):
        return super().modify(query=query, **update)

    def save_with_transaction(self, session):
        self.validate()
        cxn = self._get_collection()
        insert_one_result = cxn.insert_one(self.to_mongo(), session=session)
        return insert_one_result.inserted_id


class DocumentLock:
    def __init__(self, document):
        self.document = document

    def __enter__(self):
        self.document.locked = True
        self.document.save(expected_lock=False, save_condition={"locked": False})
        return self.document

    def __exit__(self, type, value, traceback):
        self.document.locked = False
        self.document.save(expected_lock=True, save_condition={"locked": True})


class Decimal(PyDecimal):
    def __new__(cls, value):
        getcontext().prec = 64
        return PyDecimal(value).quantize(PyDecimal('1.00000000'), rounding=ROUND_HALF_EVEN).normalize()


PRECISION = Decimal('1.0E8')
SATOSHI = Decimal('1.0E-8')


def decimal_to_long(value, precision=PRECISION):
    if not isinstance(value, PyDecimal):
        raise Exception("Value is type {0} not Decimal.".format(type(value)))
    return int(value * precision)


def long_to_decimal(value, precision=PRECISION):
    if not isinstance(value, (Int64, int)):
        raise Exception("Value is type {0} not int.".format(type(value)))
    getcontext().prec = 64
    return Decimal(PyDecimal(value / precision))


class CryptoDecimalField(db.LongField):

    def __init__(self, *args, human_name="Decimal field", **kwargs):
        self.human_name = human_name
        super().__init__(*args, **kwargs)

    def to_mongo(self, value):
        if isinstance(value, float):
            return decimal_to_long(Decimal(value))
        elif isinstance(value, PyDecimal):
            return decimal_to_long(value)
        elif isinstance(value, (Int64, int)):
            return value
        raise Exception("Type {0} is not accounted for.".format(type(value)))

    def to_python(self, value):
        if isinstance(value, float):
            return Decimal(value)
        elif isinstance(value, int):
            return long_to_decimal(value)
        elif isinstance(value, PyDecimal):
            return value
        raise Exception("Type {0} is not accounted for.".format(type(value)))

    def prepare_query_value(self, op, v):
        return self.to_mongo(v)

    def validate(self, value):
        if self.min_value is not None and value < self.min_value:
            self.error('CryptoDecimalField value is too small ({0} < {1})'.format(value, self.min_value))

        if self.max_value is not None and value > self.max_value:
            self.error('CryptoDecimalField value is too large ({0} > {1})'.format(value, self.max_value))


class TimeDeltaField(BaseField):
    """A timedelta field.
    Looks to the outside world like a datatime.timedelta, but stores
    in the database as an integer (or float) number of seconds.
    """
    def validate(self, value):
        if not isinstance(value, (timedelta, int, float)):
            self.error(u'cannot parse timedelta "%r"' % value)

    def to_mongo(self, value):
        return self.prepare_query_value(None, value)

    def to_python(self, value):
        return timedelta(seconds=value)

    def prepare_query_value(self, op, value):
        if value is None:
            return value
        if isinstance(value, timedelta):
            return self.total_seconds(value)
        if isinstance(value, (int, float)):
            return value

    @staticmethod
    def total_seconds(value):
        """Implements Python 2.7's datetime.timedelta.total_seconds()
        for backwards compatibility with Python 2.5 and 2.6.
        """
        try:
            return value.total_seconds()
        except AttributeError:
            return (value.days * 24 * 3600) + \
                   (value.seconds) + \
                   (value.microseconds / 1000000.0)
