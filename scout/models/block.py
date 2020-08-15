from scout.core import db
from scout.core import Document


class Block(Document):

    number = db.IntField(required=True, unique=True)
    bhash = db.StringField(required=True, unique=True)
    prev_bhash = db.StringField(required=True, unique=True)
    time = db.DateTimeField(required=True)

    meta = {
        'collection': 'blocks'
    }

    def __unicode__(self):
        return ''.join([self.name, ' (', self.value_type, ')'])
