#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
import string as _string

from data_migrator.anonymizors.base import BaseAnonymizor

class SimpleStringAnonymizor(BaseAnonymizor):
    '''SimpleStringAnonymizor translates to random printable chars'''

    def __call__(self, v):
        return "".join([random.choice(_string.printable) for x in v])

def _string_type(v):
    '''helper function to translate types'''
    if v in _string.ascii_lowercase:
        return random.choice(_string.ascii_lowercase)
    elif v in _string.ascii_uppercase:
        return random.choice(_string.ascii_uppercase)
    elif v in _string.digits:
        return random.choice(_string.digits)
    elif v in _string.whitespace or v in _string.punctuation:
        return v
    else:
        return "-"

class TextAnonymizor(BaseAnonymizor):
    '''TextAnonymizor translates to random chars taking whitespace and
    and punctuation into account.
    '''

    def __call__(self, v):
        return "".join([_string_type(x) for x in v])
