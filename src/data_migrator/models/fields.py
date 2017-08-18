#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import uuid
import json
from functools import partial

from data_migrator.exceptions import ValidationException, DataException
from data_migrator.exceptions import DefinitionException
from data_migrator.utils import isstr


def new_exception(field, exc_class, msg, *args):
    msg = "%s[%s]: " + msg
    return exc_class(msg % ((field.__class__.__name__, field.name) + args))


def _replace(format_str, x):
    return format_str.format(x)


class BaseField(object):
    '''Base column definition for the transformation DSL

    The following arguments are available to all field types. All are optional.

    Arguments:
        pos (int): If positive or zero this denotes the column in the source
            data to select and store in this field. If not set (or negative)
            the fields is interpreted as not selecting just a column from the
            source but to take the full row in the parse function
        name (str): The name of this field. By default this is the name
            provided in the model declaration. This attribute is to replace
            that name by the final column name.
        default: The default value to use if the source column is found to be
            a ``null`` field or if the parse function returns None. This
            attribute has default values for Fields that are not
            Null<xxx>Fields. For example NullStringField has both NULL and
            empty string as empty value. :class:`~.StringField` only has empty
            string as empty value. With this field it can be changed to some
            other standard value. Consider a Country field as string and
            setting it to the home country by default.
        key (boolean): If set, this indicates the field is a key field for
            identification of the object.
        nullable (str): If set it will match the source column value and
            consider this a ``None`` value. By default this attribute is set
            to ``None``. Note that for none Null fields ``None`` will be
            translated to :attr:`~.default`.
        replacement: If set, this is a pre-emit replacement function. This
            could be used to insert dynamic replacement lookup select queries,
            adding more indirection into the data generation.
            Value could be either function or a string.
        required (boolean): If set, this indicates the field is required to be
            set.
        parse: If set this is the parsing function to replace the read value
            into something to use further down the data migration. Use this for
            example to clean phone numbers, translate country definitions into
            alpha3 codes, or to translate ID's into values based on a
            separately loaded lookup table.
        validate: Expects a function that returns a boolean, and used to
            validate the input data. Expecting data within a range or a
            specific format, add a column validator here. Raises
            :exc:`~.ValidationException` if set and false.
        max_length (int): In case of :class:`~.StringField` use this to trim
            string values to maximum length.
        unique (boolean): If ``True``, *data-migrator* will check uniqueness of
            intermediate values (after parsing). Default is ``False``.

            In relationship with the default manager this will keep track of
            values for this field. The manager can raise exceptions if
            uniqueness is violated. Note that it is up to the manager to either
            fail or drop the record if the exception is raised.
        anonymizer: Add an additional function that will be called at emit to
            anonymize the data
        validate_output: A pre-emit validator used to scan the bare output and
            raise exceptions if output is not as expected.
        creation_order: An automatically generated attribute used to determine
            order of specification, and used in the emitting of dataset.
    '''
    creation_order = 0
    schema_type = 'object'

    def __init__(self,
                 pos=-1, name="",
                 default=None, nullable="NULL",
                 key=False, required=False,
                 replacement=None, parse=None, validate=None,
                 anonymize=None,
                 max_length=None, unique=False,
                 validate_output=None):

        # default value if null
        self.default = default if default is not None else getattr(self.__class__, 'default', default)
        # key indicated key field
        self.key = key
        # fixed position in the row to read
        if max_length and self.schema_type != "string":
            raise DefinitionException("Cannot set max_length on on string")
        self.max_length = max_length if isinstance(max_length, int) else None
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
        # anonymize is the anonymization function
        self.anonymize = anonymize() if isinstance(anonymize, type) \
            else anonymize
        # some function to apply to value
        self.validate = validate or getattr(self.__class__, 'validate', None)
        # output validator
        self.validate_output = validate_output

        # creation_order is required for orderdict to retain order of fields
        self.creation_order = BaseField.creation_order
        BaseField.creation_order += 1

    def scan(self, row):
        '''scan row and harvest distinct value.

        Takes a row of data and parses the required fields out of this.

        Args:
            row (list): array of source data

        Returns:
            parsed and processed value.

        Raises:
            :class:`~.ValidationException`: raised if explicit validation
                fails.
        '''
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
        '''helper function to export this field.

        Expects a value from the model to be emitted

        Args:
            v: value to emit
            escaper: escaper function to apply on value

        Returns:
            emitted value.

        Raises:
            :class:`~.ValidationException`: raised if explicit validation
                fails.'''
        if self.max_length and isstr(v):
            v = v[:self.max_length]
        if v is None:
            v = self.default if self.default is not None else v
        if self.validate_output and not self.validate_output(v):
            raise ValidationException("not able to validate %s=%s" % (self.name, v))
        # allow external function (e.g. SQL escape)
        # anonymize this data
        if self.anonymize:
            v = self.anonymize(v)
        # check if we have a replacement string to take into account
        if self.replace:
            v = self.replace(v)
        elif escaper:
            v = escaper(v)
        return v

    def json_schema(self, name=None):
        '''generate json_schema representation of this field

        Args:
            name: name if not taken from this field

        Returns:
            python representation of json schema
        '''
        t = self.schema_type
        if 'Null' in self.__class__.__name__:
            t = [t, "null"]
        t = {'type': t}
        if self.key:
            t['key'] = True
        if self.max_length and self.schema_type == "string":
            t['maxLength'] = self.max_length
        return {name or self.name: t}

    def _value(self, v):  # pylint: disable=R0201
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
    schema_type = 'integer'

    def _value(self, v):
        return int(v) if isstr(v) else v


class NullIntField(BaseField):
    '''Null integer field handler.

    a field that accepts the column to be integer and can also be None, which
    is not the same as 0 (zero).
    '''
    schema_type = 'integer'

    def _value(self, v):
        return int(v) if isstr(v) else v


class StringField(BaseField):
    '''String field handler, a field that accepts the column to be string.'''
    default = ""
    schema_type = 'string'

    def _value(self, v):
        return v.strip() if isinstance(v, str) else v


class NullStringField(BaseField):
    '''Null String field handler.

    a field that accepts the column to be string and can also be None, which
    is not the same as empty string ("").
    '''
    schema_type = 'string'

    def _value(self, v):
        return v.strip() if isinstance(v, str) else v


class BooleanField(BaseField):
    '''Boolean field handler.

    a bool that takes any cased permutation of true, yes, 1 and translates this
    into ``True`` or ``False`` otherwise.
    '''
    default = False
    schema_type = 'boolean'

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
    def json_schema(self, name=None):
        '''generate json_schema representation of this field'''
        return {name or self.name: {'type': 'null'}}


class UUIDField(BaseField):
    '''UUID generating field.

    a field that generates a ``str(uuid.uuid4())``
    '''
    schema_type = 'string'

    def __init__(self, *args, **kwargs):
        kwargs['default'] = None
        super(UUIDField, self).__init__(*args, **kwargs)

    def _value(self, v):
        '''override and automatically set'''
        return str(uuid.uuid4())

class ObjectField(BaseField):
    '''JSON object field'''
    default = {}
    schema_type = 'object'

DictField = ObjectField

class ArrayField(BaseField):
    '''JSON array field'''
    default = []
    schema_type = 'array'

ListField = ArrayField

class JSONField(BaseField):
    '''a field that takes the values and spits out a JSON encoding string.
    Great for maps and lists to be stored in a string like db field.
    '''
    def emit(self, v, escaper=None):
        """Emit is overwritten to add the to_json option."""
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


class ModelField(BaseField):
    '''Model relation for hierarchical structures.

    a field that takes another model to build hierarchical structures.
    '''
    def __init__(self, fields, strict=None, **kwargs):
        """
        Args:
            fields: relationship to another model.
            strict (boolean): model is considered strict.
        """
        super(ModelField, self).__init__(**kwargs)
        self.strict = strict
        self.fields = fields

    def json_schema(self, name=None):
        name = name or self.name
        _res = super(ModelField, self).json_schema()[name]
        _p = {}
        if isinstance(self.fields, list):
            for i in self.fields:
                _p.update(i.json_schema())
        elif isinstance(self.fields, dict):
            for k, v in self.fields.items():
                _p.update(v.json_schema(name=k))
        else:
            _p.update(self.fields.json_schema(name=self.fields.name))
        _res['properties'] = _p
        if self.strict is not None:
            _res['additionalProperties'] = not self.strict
        return {name: _res}

    def emit(self, v, escaper=None):
        """Emit is overwritten to add the to_json option"""
        if v is None:
            v = self.default if self.default is not None else v
        else:
            v = model.emit(v, escaper) ###FIXME: not sure this is correct
        # anonymize this data
        if self.anonymize:
            v = self.anonymize(v)
        return v
