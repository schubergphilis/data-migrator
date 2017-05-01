#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from collections import OrderedDict

from data_migrator.exceptions import DefinitionException

# list of extendable options for the Meta class
_options = {
    'drop_if_none': [],
    'drop_non_unique': False,
    'emitter': None,
    'fail_non_unique': False,
    'fail_not_validated': False,
    'file_name': None,
    'prefix': None,
    'strict': None,
    'remark': 'remark'
}


class _EmptyMeta:
    pass


class Options(object):
    def __init__(self, cls, meta, fields):
        """Options is the Model Meta data container

        The Options class is the true meta data container and parser for a
        :class:`~.Model`. It contains all flag and fields references for model
        handling. Use these flags in the Meta sub class of a :class:`~.Model`.

        Args:
            cls: the Model this Options object is refering too
            meta: the reference to a Meta class
            fields (list): list of all field definitions

        Attributes:
            drop_if_none (list): names of the columns to check for None, Is a
                list of field names as defined. If set *data-migrator* will
                check if fields are not None and drop if one of the columns is.
            drop_non_unique (boolean): If ``True``, *data-migrator* will drop
                values if the column uniqueness check fails (after parsing).
                Default is ``False``.

                Any field can be defined as a unique column. Any field set so,
                is checked after scanning and just before save-ing.
            emitter (:class:`~.BaseEmitter`): If set, *data-migrator* will use
                this emitter instead of the default emitter.
            fail_non_unique (boolean): If ``True``, *data-migrator* will fail
                as a whole if the column uniqueness check fails (after
                parsing). Default is ``False``.

                Any field can be defined as a unique column. Any field set so,
                is checked after scanning and just before save-ing.
            fail_non_validated (boolean): If ``True``, *data-migrator* will
                fail as a whole if the column validation check fails (after
                parsing). Default is ``False``.

                Any field can have its own validator, this is a rough method to
                prevent bad data from being transformed and loaded.
            file_name (string): If set, *data-migrator* will use this as
                file_name for the emitter instead of the default filename based
                on model_name.
            table_name (string): If set, *data-migrator* will use this as
                table_name for the emitter instead of the default table_name
                based on model_name.
            prefix (string): If set, *data-migrator* will use this list of
                statements as a preamble in the generation of the output
                statements.

                By default an emitter uses this to clear the old state.
            remark (string): If set, *data-migrator* will use this as the
                remark attribute in the Model, default='remark'. Use this for
                example if you have a ``remark`` field in your model and need
                to free the keyword.
            strict (boolean): If ``True``, *data-migrator* will be strict on
                the model and does not allow values outside of the definitions.
                Default is ``None``.
            manager (:class:`~.BaseManager`): If set, *data-migrator* will use
                this as the manager for this model.

                This is useful if the ``transform`` method needs to be
                overridden.

        Raises:
            :class:`~.DefinitionException`: raised if any of the defintions is
                not to spec.
        """
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
