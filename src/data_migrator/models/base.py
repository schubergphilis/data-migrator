#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from six import with_metaclass

from data_migrator.exceptions import DataException
from .manager import SimpleManager
from .fields import BaseField, HiddenField
from .options import Options


class ModelBase(type):
    """Metaclass for all models.

    Note:
        the model structure is the foundation of *data-migrator* and
        is taken from Django (https://github.com/django/django)
    """
    def __new__(mcs, name, bases, attrs):
        super_new = super(ModelBase, mcs).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(mcs, name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(mcs, name, bases, {'__module__': module})

        # Check if we have a meta class
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        # declare the fields
        fields = {}
        for n, d in attrs.items():
            if isinstance(d, BaseField):
                fields[n] = d
                setattr(d, 'name', getattr(d, 'name') or n)

        # now prepare the meta class/options
        setattr(new_class, '_meta', Options(new_class, meta, fields=fields))

        # instantiate the manager
        _manager = getattr(meta, 'manager', SimpleManager)()
        _manager._prepare(new_class)
        setattr(new_class, 'objects', _manager)

        return new_class


class Model(with_metaclass(ModelBase)):
    """Model is foundation for every transformation.

    Each non-abstract :class:`~.Model` class must have a
    :class:`~.BaseManager` instance added to it. *data-migrator* ensures that
    in your model class you have  at least a standard :class:`~.SimpleManager`
    specified, on case you do add your own specialization of
    :class:`~.BaseManager` through the Meta class :attr:`~.Options.manager`
    attribute.

    Attributes:
        objects: reference to manager
    """
    # __metaclass__=ModelBase

    def __init__(self, **kwargs):
        _meta = self.__class__._meta
        # set value fields from kwargs if declared
        # if strict raise those not declared
        _fields = _meta.fields
        f = list(_fields.keys())[:]
        for k, v in kwargs.items():
            if k == _meta.remark:
                setattr(self, k, v)
            elif k in f:
                setattr(self, k, _fields[k]._value(v))
                f.remove(k)
            elif _meta.strict:
                raise DataException("trying to set unknown field %s" % k)
            else:
                setattr(self, k, v)
        # add missing fields
        for k in f:
            _f = _fields[k]
            setattr(self, k, _f._value(_f.default))

    def scan(self, row):
        '''scan model from row based on field definition scanners.

        Returns:
            self, so that methods can be chained
        '''
        _fields = self.__class__._meta.fields
        for k in _fields.keys():
            setattr(self, k, _fields[k].scan(row))
        return self

    def emit(self, escaper=None):
        '''output and escape this object instance to a dict.

        Returns:
            map: object transfored according to field definitions

        Note:
            HiddenFields are not emitted
        '''
        res = {}
        _fields = self.__class__._meta.fields
        for k, f in _fields.items():
            if not isinstance(f, HiddenField):
                res[f.name] = f.emit(self.__dict__[k], escaper)
        return res

    def update(self, **kwargs):
        '''Update method for chaining operations.

        Returns:
            self, so that methods can be chained

        Raises:
            :exc:`~.DataException`: raised if trying to set non defined field
                and strict model.
        '''
        _meta = self.__class__._meta
        _fields = self.__class__._meta.fields.keys()
        for k, v in kwargs.items():
            if k in _fields or not _meta.strict:
                setattr(self, k, v)
            else:
                raise DataException("trying to set unknown field %s" % k)
        return self

    def save(self):
        '''Save this object and add it to the list.

        Returns:
            self, so that methods can be chained
        '''
        self.objects.save(self)
        return self

    @classmethod
    def json_schema(cls):
        '''generate the json schema representation of this model.

        Returns:
            dict with python representation of json schema.
        '''
        _fields = [f for f in cls._meta.fields.values()
                   if not isinstance(f, HiddenField)]
        _required = [x.name for x in _fields if x.required]
        _key = [x.name for x in _fields if x.key]
        _required = list(set(_required + _key))
        _res = {}
        for f in _fields:
            _res.update(f.json_schema())
        _res = {
            "$schema": "http://json-schema.org/draft-04/schema",
            'properties': _res,
            'type': 'object'
        }
        if _required:
            _res['required'] = _required
        if cls._meta.strict:
            _res['additionalProperties'] = False
        elif cls._meta.strict is not None:
            _res['additionalProperties'] = True
        return _res

    def __repr__(self):
        try:
            u = str(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
            u = '[Bad Unicode data]'
        return '<%s: %s>' % (self.__class__.__name__, u)

    def __str__(self):
        return '%s object' % self.__class__.__name__
