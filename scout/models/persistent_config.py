from bson.objectid import ObjectId
from mongoengine import signals
from mongoengine.errors import NotUniqueError

from scout.core import db
from scout.core import Document
from scout.core import Decimal


VALUE_TYPES = {
    'bool': bool,
    'Decimal': Decimal,
    'int': int,
    'str': str
}

CONFIG_MEMORY = {}


class PersistentConfig(Document):

    name = db.StringField(required=True, unique=True)
    value = db.StringField(required=True)
    value_type = db.StringField(required=True, choices=list(VALUE_TYPES.keys()))

    meta = {
        'collection': 'pconfig'
    }

    def __unicode__(self):
        return ''.join([self.name, ' (', self.value_type, ')'])

    @staticmethod
    def setup(app):
        pass

    @classmethod
    def get_from_name(cls, name):
        if ObjectId.is_valid(name):
            perm = cls.objects(id=name).first()
        else:
            if name in CONFIG_MEMORY:
                perm = CONFIG_MEMORY[name]
            else:
                perm = cls.objects(name=name).first()
                CONFIG_MEMORY[perm.name] = perm
        return perm

    @property
    def real_value(self):
        return self.verify_type(self.value)

    def verify_type(self, value):
        req_type = VALUE_TYPES[self.value_type]
        if req_type is bool:
            return str(value).lower() in ['true']
        else:
            return req_type(str(value))

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.value = str(document.verify_type(document.value))
        CONFIG_MEMORY[document.name] = document


signals.pre_save.connect(PersistentConfig.pre_save, sender=PersistentConfig)
