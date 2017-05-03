#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Explicit exceptions for this package
"""


class InternalException(Exception):
    """Unexpected internal error"""
    pass


class DefinitionException(Exception):
    """Error in definition"""
    pass


class ValidationException(Exception):
    """Validate Error in input data"""
    pass


class DataException(Exception):
    """Error in input data"""
    pass


class NonUniqueDataException(Exception):
    """Non unique data based on key found"""
    pass


class NullDataException(Exception):
    """data = NULL exception"""
    pass
