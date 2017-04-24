#!/usr/bin/python
# -*- coding: UTF-8 -*-
from six import with_metaclass

from .manager import SimpleManager
from .fields import BaseField, HiddenField
from .options import Options
from data_migrator.exceptions import DataException


class ModelBase(type):
    """Metaclass for all models.

    Note:
        the model structure is the foundation of *data-migrator* and
        is taken from Django (https://github.com/django/django)
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelBase, cls).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})

        # Chek if we have a meta class
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        # declare the fields
        fields = {}
        for n,d in attrs.items():
            if isinstance(d, BaseField):
                fields[n] = d
                setattr(d, 'name', getattr(d, 'name') or n)
                # fields[d.name]=d
        setattr(new_class, '_meta', Options(new_class, meta, fields=fields))

        # instantiate the manager
        _manager = getattr(meta, 'manager', SimpleManager)()
        _manager._prepare(new_class)
        setattr(new_class, 'objects', _manager)

        return new_class


class Model(with_metaclass(ModelBase)):
    """Model is foundation for every transformation

    Each non-abstract :class:`~data_migrator.models.Model` class must have a
    :class:`~data_migrator.models.Manager` instance added to it.
    Data-migrator ensures that in your model class you have  at least a
    standard ``SimpleManager`` specified. If you add your own
    :class:`~data_migrator.models.Manager` instance attribute, the default one does
    not appear.

    Attributes:
        objects: reference to manager
    """
    # __metaclass__=ModelBase

    def __init__(self, **kwargs):
        _meta = self.__class__._meta
        # set value fields from kwargs if declared
        # model is very strict raise those not declared
        _fields = _meta.fields
        f = list(_fields.keys())[:]
        for k,v in kwargs.items():
            if k == _meta.remark:
                setattr(self, k, v)
            elif k in f:
                setattr(self, k, _fields[k]._value(v))
                f.remove(k)
            else:
                raise DataException("trying to set unknown field %s" % k)
        # add missing fields, put in None values (to be replaced by default at emit)
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
        for k,f in _fields.items():
            if not isinstance(f, HiddenField):
                res[f.name] = f.emit(self.__dict__[k], escaper)
        return res

    def save(self):
        '''Save this object and add it to the list.

        Returns:
            self, so that methods can be chained
        '''
        self.objects.save(self)
        return self

    def __repr__(self):
        try:
            u = str(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
            u = '[Bad Unicode data]'
        return '<%s: %s>' % (self.__class__.__name__, u)

    def __str__(self):
        return '%s object' % self.__class__.__name__
