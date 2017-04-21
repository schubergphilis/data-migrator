#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""helper functions for py2 -> p3 compat"""

def isstr(s):
    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)
