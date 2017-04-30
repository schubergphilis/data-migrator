#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import uuid
import json
from functools import partial

from data_migrator.exceptions import ValidationException, DataException
from data_migrator.utils import isstr


def new_exception(field, exc_class, msg, *args):
    msg = "%s[%s]: " + msg
    return exc_class(msg % ((field.__class__.__name__, field.name) + args))


def _replace(format_str, x):
    return format_str.format(x)


class BaseField(object):
    '''Base column definition for the transformation DSL
    '''
    creation_order = 0

    def __init__(self,
                 pos=-1, name="",
                 default=None, nullable="NULL",
                 key=False, required=False,
                 replacement=None, parse=None, validate=None,
                 max_length=None, unique=False,
                 validate_output=None):

        # default value if null
        self.default = default if default is not None else getattr(self.__class__, 'default', default)
        # key indicated key field
        self.key = key
        # fixed position in the row to read
        self.max_length = max_length
        # name of this field (will be set in Model class construction)
        self.name = name
        # input string that defines null -> None
        self.nullable = nullable
        # some function to apply to value
        self.parse = parse or getattr(self.__class__, 'parse', None)
        self.pos = int(pos)
        # replace string to use in output
        if isstr(replacement):
            replacement = partial(_replace, replacement)
        self.replace = getattr(self.__class__, 'replace', replacement)
        # required indicates must be filled in
        self.required = required
        # unique indicates a unique field
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
        v = None
        if self.pos >= 0:
            # do null check if enabled
            if self.nullable is not None and row[self.pos] == self.nullable:
                return v
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
        if self.max_length and isstr(v):
            v = v[:self.max_length]
        v = v or self.default
        if self.validate_output and not self.validate_output(v):
            raise ValidationException("not able to validate %s=%s" % (self.name, v))
        # allow external function (e.g. SQL escape)
        if escaper:
            v = escaper(v)
        # check if we have a replacement string to take into account
        if self.replace:
            v = self.replace(v)
        return v

    def _value(self, v):
        return v


class HiddenField(BaseField):
    '''Non emitting Field for validation and checking.

    a field that accepts, but does not emit. It is useful for uniqueness
    checked and more. Combine this with a row parse and check the complete row.
    '''
    pass


class IntField(BaseField):
    '''Basic integer field handler'''
    default = 0

    def _value(self, v):
        return int(v) if isstr(v) else v


class NullIntField(BaseField):
    '''Null integer field handler.

    a field that accepts the column to be integer and can also be None, which
    is not the same as 0 (zero).
    '''
    def _value(self, v):
        return int(v) if isstr(v) else v


class StringField(BaseField):
    '''String field handler, a field that accepts the column to be string.'''
    default = ""

    def _value(self, v):
        return v.strip() if isinstance(v, str) else v


class NullStringField(BaseField):
    '''Null String field handler.

    a field that accepts the column to be string and can also be None, which
    is not the same as empty string ("").
    '''
    def _value(self, v):
        return v.strip() if isinstance(v, str) else v


class BooleanField(BaseField):
    '''Boolean field handler.

    a bool that takes any cased permutation of true, yes, 1 and translates this
    into ``True`` or ``False`` otherwise.
    '''
    default = False

    def _value(self, v):
        try:
            return v.lower()[0] in ['y', 't', '1']
        except (AttributeError, IndexError):
            return False


class DefaultField(BaseField):
    '''DefaultField always returns the default value'''
    def emit(self, v, escaper=None):
        """Emit is overwritten return default always"""
        return super(DefaultField, self).emit(self.default, escaper)

    def _value(self, v):
        '''override so we can never set'''
        return self.default


class NullField(DefaultField):
    '''NULL returning field by generating None'''
    pass


class UUIDField(BaseField):
    '''UUID generating field.

    a field that generates a ``str(uuid.uuid4())``
    '''
    def __init__(self, *args, **kwargs):
        kwargs['default'] = None
        super(UUIDField, self).__init__(*args, **kwargs)

    def _value(self, v):
        '''override and automatically set'''
        return str(uuid.uuid4())


class JSONField(BaseField):
    '''a field that takes the values and spits out a JSON encoding string.
    Great for maps and lists to be stored in a string like field.
    '''
    def emit(self, v, escaper=None):
        """Emit is overwritten to add the to_json option"""
        if v is None:
            v = self.default if self.default is not None else v
        v = json.dumps(v)
        return super(JSONField, self).emit(v, escaper)


class MappingField(BaseField):
    '''Map based field translator.

    a field that takes the values translates these according to a map. Great
    for identity column replacements. If needed output can be translated as
    ``json``, for example if the map returns lists.
    '''
    def __init__(self, data_map, as_json=False, strict=False, **kwargs):
        """
        Args:
            data_map: The data_map needed to translate. Note the fields returns
                :attr:`~Field.default` if it is not able to map the key.
            as_json: If ``True``, the field will be output as json encoded.
                Default is ``False``
            strict: If ``True``, the value must by found in the map.
                Default is ``False``
        """
        super(MappingField, self).__init__(**kwargs)
        if strict and self.default:
            data_map[self.default] = self.default
        self.data_map = data_map
        self.as_json = as_json
        self.strict = strict

    def emit(self, v, escaper=None):
        """Emit is overwritten to add the to_json option"""
        if v is None:
            v = self.default if self.default is not None else v
        if self.strict:
            try:
                v = self.data_map[v]
            except KeyError:
                raise DataException("%s - %s not in map" % (self.name, v))
        else:
            v = self.data_map.get(v, self.default if self.default is not None
                                  else v)
        if self.as_json:
            v = json.dumps(v)
        return super(MappingField, self).emit(v, escaper)
