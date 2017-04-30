#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
commonly used dutch support functions
'''

import re

_PHONE_CHARS = re.compile(r'[^\+\d]+')
_INTERNATIONAL_ZERO_START = re.compile('^00')
_MUNICIPALY_ZERO_START = re.compile('^0')


def clean_phone(v):
    '''Cleans phone numbers to dutch clean format

    clean_phone clean phone numbers, replaces all characters and spaces
    adds dutch country code (+31) if no country code is provide

        >>> [clean_phone(x) for x in ['00 31 6 - 20 20 20 20','06 20 20 20 20',
        '020 -123 345 6','+440.203.020.23','+440a203a020a23']
        ['+31620202020','+31620202020','+31201233456','+4402030203',
        '+4402030203']

    Args:
        v (str): value to clean

    Returns:
        str: cleaned phone number
    '''

    v = _PHONE_CHARS.sub('', v)
    v = _INTERNATIONAL_ZERO_START.sub('+', v)
    v = _MUNICIPALY_ZERO_START.sub('+31', v)
    return v


ZIP_CODE = re.compile('^([0-9]{4})[\t ]*([a-zA-Z]{2})$')


def clean_zip_code(v):
    '''Cleans a dutch zipcode

        >>> [clean_zip_code(x) for x in ['1234 aa', '1234AB', '1234   Ba']]
        ['1234AA', '1234AB', '1234BA']

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
