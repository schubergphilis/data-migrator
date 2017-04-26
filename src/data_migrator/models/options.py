#!/usr/bin/python
# -*- coding: UTF-8 -*-

from collections import OrderedDict

from data_migrator.exceptions import DefinitionException

_options = {
    'drop_if_none': [],
    'drop_non_unique': False,
    'emitter': None,
    'fail_non_unique': False,
    'fail_not_validated': False,
    'file_name': None,
    'prefix': None,
    'remark': 'remark'
}


class _EmptyMeta:
    pass


class Options(object):
    def __init__(self, cls, meta, fields):
        self.cls = cls
        self.meta = meta or _EmptyMeta
        self.model_name = cls.__name__
        self.table_name = getattr(self.meta, 'table_name', cls.__name__.lower())

        # Set all options based on dict, retrieve from meta
        for k, d in _options.items():
            setattr(self, k, getattr(self.meta, k, d))
        for k in self.meta.__dict__.keys():
            if k[0:2] != '__' and k not in list(_options.keys()) + ['table_name', 'manager']:
                raise DefinitionException("%s, %s not a valid meta key" % (self.model_name, k))

        # store all fields, sorted
        self.fields = OrderedDict(sorted(fields.items(), key=lambda x: x[1].creation_order))
        # retrieve the highest column from the field definitions
        self.max_pos = max([-1]+[f.pos for f in fields.values()])
        # extract unique fields for further processing
        self.unique_fields = [n for n, f in fields.items() if f.unique]

        for k in self.drop_if_none:
            if k not in fields.keys():
                raise DefinitionException("%s: drop_if_none %s not in field list", self.model_name, k)

    def __repr__(self):
        try:
            u = str(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
            u = '[Bad Unicode data]'
        return '<%s: %s>' % (self.__class__.__name__, u)

    def __str__(self):
        return '%s: %s' % (self.__class__.__name__, ",".join(["%s=%s" % (k, v) for k, v in self.__dict__.items()]))
