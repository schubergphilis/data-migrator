#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
commonly used dutch support functions for cleaning and anonymization
'''

import re
import string

from data_migrator.anonymizors.base import BaseAnonymizor
from data_migrator.utils.compat import choices

_PHONE_CHARS = re.compile(r'[^\+\d]+')
_INTERNATIONAL_ZERO_START = re.compile('^00')
_MUNICIPALY_ZERO_START = re.compile('^0')


def clean_phone(v):
    '''Cleans phone numbers to dutch clean format

    clean_phone clean phone numbers, replaces all characters and spaces
    adds dutch country code (+31) if no country code is provide

        >>> clean_phone('00 31 6 - 20 20 20 20')
        '+31620202020'
        >>> clean_phone('06 20 20 20 20')
        '+31620202020'
        >>> clean_phone('020 -123 345 6')
        '+31201233456'
        >>> clean_phone('+440.203.020.23')
        '+44020302023'
        >>> clean_phone('+440a203a020a23')
        '+44020302023'
        >>> clean_phone('+440 ada 203.020 // 23')
        '+44020302023'
        >>> clean_phone('31 (6) - 20 20 20 20')
        '+31620202020'

    Args:
        v (str): value to clean

    Returns:
        str: cleaned phone number
    '''

    v = _PHONE_CHARS.sub('', v)
    v = _INTERNATIONAL_ZERO_START.sub('+', v)
    v = _MUNICIPALY_ZERO_START.sub('+31', v)
    if v.startswith('316'):
        v = '+' + v
    return v


ZIP_CODE = re.compile('^([0-9]{4})[\t ]*([a-zA-Z]{2})$')


def clean_zip_code(v):
    '''Cleans a dutch zipcode

        >>> clean_zip_code('1234 aa')
        '1234AA'
        >>> clean_zip_code('1234AB')
        '1234AB'
        >>> clean_zip_code('1234   Ba')
        '1234BA'
        >>> clean_zip_code('1 2 3 4 A B')
        '1 2 3 4 A B'
        >>> clean_zip_code('blabla')
        'blabla'

    Args:
        v (str): zipcode to clean

    Returns:
        str: cleaned zip code
    '''
    v = v.strip()
    try:
        z = ZIP_CODE.match(v).groups()
        r = "%s%s" % (z[0], z[1].upper())  # Dutch zip code is 1234AB
    except AttributeError:
        r = v
    return r


class PhoneAnonymizor(BaseAnonymizor):
    '''PhoneAnonymizor generates a random dutch phonenumber, like +3142097272

        >>> len(PhoneAnonymizor()('020-1234583'))
        11
        >>> len(PhoneAnonymizor()('06-12345678'))
        11
    '''

    def __call__(self, v):
        return "+31" + "".join(choices(string.digits, k=8))


class ZipCodeAnonymizor(BaseAnonymizor):
    '''ZipCodeAnonymizor generates a random dutch zipcode, like '4897 LD'

        >>> len(ZipCodeAnonymizor()('1234 aa'))
        7
    '''

    def __call__(self, v):
        return "".join(choices(string.digits, k=4) + [" "] +
            choices(string.ascii_uppercase, k=2))
