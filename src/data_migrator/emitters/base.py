#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class BaseEmitter(object):
    '''Base for emitters of the *data-migrator*.

    Attributes:
        manager (BaseManager): reference to the manager that is calling this
            emitter to export objects from that manager
        model_class (Model): reference to the model linked to the class
        extension (str): file extension for output file of this emitter

    note: :attr:`~.model_class` and :attr:`~.manager` are linked together
    '''

    def __init__(self, extension=None, manager=None):
        # reference to the manager that is calling this emitter to
        # export objects from the manager
        self.manager = manager
        self.model_class = manager.model_class
        self.meta = self.model_class._meta
        self.extension = extension or getattr(self.__class__,
                'extension', '.txt')

    def emit(self, l):
        '''output the result set of an object.

        Args:
            l (Model): object to transform
        Returns:
            list: generated strings
        '''
        raise NotImplementedError

    def filename(self):
        '''generate filename for this emitter.

        generates a filename bases on :attr:`~.BaseEmitter.extension` and
        either :attr:`~.Options.file_name` or :attr:`~.Options.table_name`

        Returns:
            str: filename
        '''
        _ext = self.extension
        if _ext[0] != '.':
            _ext = '.' + _ext
        _filename = self.meta.file_name or (self.meta.table_name + _ext)
        return _filename

    def preamble(self, headers):
        '''generate a premable for the file to emit.

        Args:
            headers (list): additional header to provide outside the emitter
                (e.g. statistics)
        Returns:
            list: preamble lines
        '''
        raise NotImplementedError

    def postamble(self):
        '''generate a postamble for the file to emit.

        Returns:
            list: postamble lines
        '''
        return []
