#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re

_PHONE_CHARS=re.compile('[^\+\d]+')
_INTERNATIONAL_ZERO_START=re.compile('^00')
_MUNICIPALY_ZERO_START=re.compile('^0')

def clean_phone(v):
    '''Cleans phone numbers to dutch clean format

    clean_phone clean phone numbers, replaces all characters and spaces
    adds dutch country code (+31) if no country code is provide

        >>> [clean_phone(x) for x in ['00 31 6 - 20 20 20 20','06 20 20 20 20','020 -123 345 6','+440.203.020.23','+440a203a020a23']
        ['+31620202020','+31620202020','+31201233456','+4402030203','+4402030203']

    Args:
        v: value to clean

    Returns:
        cleaned phone number
    '''

    v = _PHONE_CHARS.sub('', v)
    v = _INTERNATIONAL_ZERO_START.sub('+', v)
    v = _MUNICIPALY_ZERO_START.sub('+31', v)
    return v
