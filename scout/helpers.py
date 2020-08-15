import pkgutil
import importlib
import os
import re

from flask import Blueprint
from flask import render_template
from flask import request
from flask import url_for
from scout.core import decimal_to_long, long_to_decimal, Decimal


def DataRequiredIf2fa(form, field):
    from scout.models import User
    user = User.GetSessionsUser()
    if user.multifactor_login_enabled and not field.data:
        field.errors.append('Two Factor Code Required')
        return False
    return True


def BitgoValueToDecimal(value):
    return long_to_decimal(int(value))


def DecimalToBitgoValue(value):
    return decimal_to_long(Decimal(value))


def is_email_address_valid(email):
    """Validate the email address using a regex."""
    if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
        return False
    return True


def redirect_url(default='index'):
    return request.args.get('next') or request.referrer or url_for(default)


# Need to import all models in factory to avoid "NotRegistered" error in celery sometimes..
def import_all_models():
    for _, name, _ in pkgutil.iter_modules([os.getcwd() + "/cryptos/models"]):
        try:
            importlib.import_module('cryptos.models.%s' % (name))
        except ImportError:
            pass


def yield_all_packages(package_path, package_name, package=None):
    for _, name, _ in pkgutil.iter_modules(package_path):
        if name == 'factory':
            continue
        m = importlib.import_module('%s.%s' % (package_name, name), package=package)
        for item_name in dir(m):
            item = m.__dict__[item_name]
            yield name, item_name, item


def register_commands(manager, package_name, package_path):
    """Register all Command instances on the specified Manager class found
    in all modules for the specified package.
    :param manager: the Manager class
    :param package_name: the package name
    :param package_path: the package path
    """
    for name, item_name, item in yield_all_packages(package_path, package_name):
        # Can assume its a command class like this
        if isinstance(item, type) and hasattr(item, "get_options") and item_name != "Command":
            manager.add_command(item_name, item())


def replace_all(replaceables, directory):
    for n_directory, _, filenames in os.walk(directory):
        if ".git" in n_directory:
            continue

        for filename in filenames:
            if filename in ['.travis.yml', 'ChangeLog.md', 'circle.yml']:
                continue

            _replaceables(replaceables, "".join([n_directory, "/", filename]))


def register_blueprints(app, package_name, package_path, url_prefix):
    """Register all Blueprint instances on the specified Flask application found
    in all modules for the specified package.
    :param app: the Flask application
    :param package_name: the package name
    :param package_path: the package path
    """
    for name, _, item in yield_all_packages(package_path, package_name):
        if isinstance(item, Blueprint):
            app.register_blueprint(item, url_prefix=url_prefix + item.url_prefix)


def replace_in_files(replaceables, directory):
    for filename, vals in replaceables.iteritems():
        _replaceables(vals, "".join([directory, "/", filename]))


def _replaceables(replaceables, fullpath):

    with open(fullpath, "r+") as file:
        try:
            text = file.read().decode('utf-8')
        except:
            return

        for old_name, new_name in replaceables.iteritems():
            text = text.replace(old_name.decode('utf-8'), new_name.decode('utf-8'))

        file.seek(0)
        file.write(text.encode('utf-8'))
        file.truncate()


def read_file(fullpath):
    text = ""
    with open(fullpath, "r+") as file:
        text = str(file.read())
    return text


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def remove_between_lines(fullpath, first, last):
    with open(fullpath, "rw+") as file:
        s = str(file.read())
        s1 = s.split(first)[0]
        s2 = s.split(last)[1]
        file.seek(0)
        file.write("".join([s1, s2]))
        file.truncate()


# https://en.bitcoin.it/wiki/List_of_address_prefixes
results = {0: "1", 1: "Q-Z, a-k, m-o", 2: "o-z", 3: "2", 4: "2 or 3", 5: "3", 6: "3", 7: "3 or 4", 8: "4", 9: "4 or 5", 10: "5", 11: "5", 12: "5 or 6", 13: "6", 14: "6 or 7", 15: "7", 16: "7", 17: "7 or 8", 18: "8", 19: "8 or 9", 20: "9", 21: "9", 22: "9 or A", 23: "A", 24: "A or B", 25: "B", 26: "B", 27: "B or C", 28: "C", 29: "C or D", 30: "D", 31: "D", 32: "D or E", 33: "E", 34: "E or F", 35: "F", 36: "F", 37: "F or G", 38: "G", 39: "G or H", 40: "H", 41: "H", 42: "H or J", 43: "J", 44: "J or K", 45: "K", 46: "K", 47: "K or L", 48: "L", 49: "L or M", 50: "M", 51: "M", 52: "M or N", 53: "N", 54: "N or P", 55: "P", 56: "P", 57: "P or Q", 58: "Q", 59: "Q or R", 60: "R", 61: "R", 62: "R or S", 63: "S", 64: "S or T", 65: "T", 66: "T", 67: "T or U", 68: "U", 69: "U or V", 70: "V", 71: "V", 72: "V or W", 73: "W", 74: "W or X", 75: "X", 76: "X", 77: "X or Y", 78: "Y", 79: "Y or Z", 80: "Z", 81: "Z", 82: "Z or a", 83: "a", 84: "a or b", 85: "b", 86: "b or c", 87: "c", 88: "c", 89: "c or d", 90: "d", 91: "d or e", 92: "e", 93: "e", 94: "e or f", 95: "f", 96: "f or g", 97: "g", 98: "g", 99: "g or h", 100: "h", 101: "h or i", 102: "i", 103: "i", 104: "i or j", 105: "j", 106: "j or k", 107: "k", 108: "k", 109: "k or m", 110: "m", 111: "m or n", 112: "n", 113: "n", 114: "n or o", 115: "o", 116: "o or p", 117: "p", 118: "p", 119: "p or q", 120: "q", 121: "q or r", 122: "r", 123: "r", 124: "r or s", 125: "s", 126: "s or t", 127: "t", 128: "t", 129: "t or u", 130: "u", 131: "u or v", 132: "v", 133: "v", 134: "v or w", 135: "w", 136: "w or x", 137: "x", 138: "x", 139: "x or y", 140: "y", 141: "y or z", 142: "z", 143: "z", 144: "z or 2 34 or", 145: "2", 255: "2"}


def get_base58(char):
    for x, i in results.iteritems():
        if i == char:
            return x
    raise ValueError("".join(["Character '", str(char), "' cannot be Base58 Encoded"]))


def RequestIPCountry():
    return request.headers.get('CF-IPCountry', None)


def RequestIPAddress():
    return request.headers.get('CF-Connecting-IP', request.remote_addr)


def RequestIPv4Address():
    return request.headers.get('CF-Pseudo-IPv4', RequestIPAddress())


def DetermineAPR(arai_amount):
    if arai_amount < Decimal('500000'):
        return Decimal('0.0')
    elif arai_amount < Decimal('1500000'):
        return Decimal('0.04')
    elif arai_amount < Decimal('5000000'):
        return Decimal('0.055')
    else:
        return Decimal('0.07')


def DetermineLevel(arai_amount):
    if arai_amount < Decimal('500000'):
        return None
    elif arai_amount < Decimal('1500000'):
        return 'bronze'
    elif arai_amount < Decimal('5000000'):
        return 'silver'
    else:
        return 'gold'


def DeterminePayout(arai_amount, apr, days=90):
    from scout.models import PersistentConfig
    arai_rate = PersistentConfig.get_from_name(name='arai_rate').real_value
    return Decimal(Decimal(days / 365) * apr * arai_amount * arai_rate)


def sbool(x):
    return str(x).lower() in ["1", "true", "yes"]
