from decimal import Decimal
from bson.objectid import ObjectId
from scout.core import redis
from scout.core import decimal_to_long
from scout.core import long_to_decimal
import json


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return {
                '__type__': '__objectid__',
                'obj_id': str(obj)
            }
        elif isinstance(obj, Decimal):
            return {
                '__type__': '__decimal__',
                'val': decimal_to_long(obj)
            }
        else:
            return json.JSONEncoder.default(self, obj)


def my_decoder(obj):
    if '__type__' in obj:
        if obj['__type__'] == '__objectid__':
            return ObjectId(obj['obj_id'])
        elif obj['__type__'] == '__decimal__':
            return long_to_decimal(obj['obj_id'])
    return obj


# Encoder function
def dumps(obj):
    return json.dumps(obj, cls=CustomEncoder)


# Decoder function
def loads(obj):
    return json.loads(obj.decode('utf8'), object_hook=my_decoder)


def redis_lock(key, expire):
    def redis_locker(func):
        def lock(*args, **kwargs):

            tmp_key = key
            if "$" in tmp_key:
                tmp_key = tmp_key.replace("$function", str(kwargs.get('function', 'null_func')))
                coin_id = kwargs.get('coin_id', None)
                if coin_id is None:
                    coin_id = kwargs.get('wallet_id', 'null_id')
                tmp_key = tmp_key.replace("$id", str(coin_id))

            lock_aquired = redis.set(tmp_key, "lock", ex=expire, nx=True)
            if lock_aquired:
                try:
                    ret = func(*args, **kwargs)
                except:
                    redis.delete(tmp_key)
                    raise
                redis.delete(tmp_key)
                return ret

            # raise Exception("Could not obtain lock on key: '" + str(tmp_key) + "'")
        return lock
    return redis_locker
