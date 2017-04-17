#!/usr/bin/python
# -*- coding: UTF-8 -*-

import uuid
import json

from data_migrator.exceptions import ValidationException

def new_exception(field, exc_class, msg, *args):
    msg = "%s[%s]: " + msg
    return exc_class(msg % ((field.__class__.__name__, field.name) + args))

class BaseField(object):
    '''Base column definition for the transformation DSL'''
    creation_order = 0

    def __init__(self,
        pos=-1, name="",
        default=None, null="NULL",
        replace=None, parse=None, validate=None,
        max_length=None, unique=False,
        validate_output=None):

        # default value if null
        self._default = default if default is not None else getattr(self.__class__, '_default', default)
        # fixed position in the row to read
        self.max_length = max_length
        # name of this field (will be set in Model class construction)
        self.name = name
        # input string that defines null -> None
        self.null = null
        # some function to apply to value
        self.parse = parse or getattr(self.__class__, 'parse', None)
        self.pos = int(pos)
        # replace string to use in output
        self.replace = getattr(self.__class__, 'replace', replace)
        self.unique = unique
        # some function to apply to value
        self.validate = validate or getattr(self.__class__, 'validate', None)
        # output validator
        self.validate_output = validate_output

        self.creation_order = BaseField.creation_order
        BaseField.creation_order += 1

    def scan(self, row):
        '''scan row and harvest distinct value'''
        # see if we want to read a column in the row
        v = self._default
        if self.pos >= 0:
            # do null check if enabled
            if self.null is not None and row[self.pos] == self.null:
                return self._default
            v = row[self.pos]
            if self.validate and not self.validate(v):
                raise ValidationException('field %r input data did not validate' % self.name)
            # apply intermediate function on output, default is stripping
            if self.parse:
                v = self.parse(v)
        elif self.parse:
            v = self.parse(row) or v
            # delegate to inner function, to reuse this logic
        return self._value(v)

    def emit(self, v, escaper=None):
        if self.max_length and isinstance(v, basestring):
            v = v[:self.max_length]
        if self.validate_output and not self.validate_output(v):
            raise ValidationException("not able to validate %s=%s" % (self.name, v))
        # allow external function (e.g. SQL escape)
        if escaper:
            v = escaper(v)
        # check if we have a replacement string to take into account
        if self.replace:
            v = self.replace(v)
        return v

    def default(self):
        return self._value(self._default)

    def _value(self, value):
        return value

class HiddenField(BaseField):
    '''Field for validation and checking, will not be emitted'''
    pass


class IntField(BaseField):
    '''Basic integer field handler'''
    _default = 0
    def _value(self, value):
        return int(value)

class NullIntField(BaseField):
    '''Null integer field handler'''
    def _value(self, value):
        return int(value)

class StringField(BaseField):
    '''String field handler'''
    _default = ""
    def _value(self, value):
        return value.strip()

class NullStringField(BaseField):
    '''Null String field handler'''
    def _value(self, value):
        return value.strip() if isinstance(value, str) else value

class BooleanField(BaseField):
    '''Boolean field handler'''
    _default = False
    def _value(self, value):
        try:
            return value.lower()[0] in ['y', 't', '1']
        except (AttributeError, IndexError):
            return False

class UUIDField(BaseField):
    '''UUID generating field'''
    def _value(self, value):
        return str(uuid.uuid4())

class NullField(BaseField):
    '''NULL returning field'''
    def _value(self, value):
        return None


class JSONField(BaseField):
    def emit(self, v, escaper=None):
        v = json.dumps(v)
        return super(JSONField, self).emit(v, escaper)

class MappingField(BaseField):
    '''Map based field translator'''
    def __init__(self, data_map={}, as_json=False, **kwargs):
        super(MappingField, self).__init__(**kwargs)
        self.data_map = data_map
        self.as_json = as_json

    def _value(self, v):
        if v is None:
            return v
        else:
            return self.data_map.get(v, self._default or v)

    def emit(self, v, escaper=None):
        if self.as_json:
            v = json.dumps(v)
        return super(MappingField, self).emit(v, escaper)
