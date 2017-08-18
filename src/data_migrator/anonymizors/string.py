#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
import string

from data_migrator.anonymizors.base import BaseAnonymizor

class SimpleStringAnonymizor(BaseAnonymizor):
    '''SimpleStringAnonymizor translates to random printable chars'''

    def __call__(self, v):
        return "".join([random.choice(string.printable) for x in v])

def _string_type(v):
    '''helper function to translate types'''
    if v in string.ascii_lowercase:
        return random.choice(string.ascii_lowercase)
    elif v in string.ascii_uppercase:
        return random.choice(string.ascii_uppercase)
    elif v in string.digits:
        return random.choice(string.digits)
    elif v in string.whitespace or v in string.punctuation:
        return v
    else:
        return "-"

class TextAnonymizor(BaseAnonymizor):
    '''TextAnonymizor translates to random chars taking whitespace and
    and punctuation into account.
    '''

    def __call__(self, v):
        return "".join([_string_type(x) for x in v])
