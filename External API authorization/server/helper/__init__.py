import re

import phonenumbers

from . import DBOperator
from . import validator
from .generator import *


def determining_login_type(input_string):
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', input_string):
        return 'email'
    try:
        if phonenumbers.is_valid_number(phonenumbers.parse(input_string)):
            return 'phone'
    except phonenumbers.phonenumberutil.NumberParseException: ...

    return 'username'