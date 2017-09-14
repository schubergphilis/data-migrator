#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from data_migrator.emitters.base import BaseEmitter
from data_migrator.models.fields import HiddenField
from data_migrator.utils import default_logger, sql_escape

log = default_logger()


class CSVEmitter(BaseEmitter):
    '''CSV emitter to output delimited data

    Attributes:
        base_template: base template to output the object
        extension (str): file extension for output file of this emitter.
            Defaults to .csv
    '''
    extension = '.csv'
    base_template = '''%s'''

    def __init__(self, *args, **kwargs):
        super(CSVEmitter, self).__init__(*args, **kwargs)
        self._prepare()

    def emit(self, l):
        '''Output the result set of an object as CSV string'''
        res = []
        if hasattr(l, self.meta.remark):
            res.append("# %s" % getattr(l, self.meta.remark))
        res.append(self._template % l.emit(escaper=sql_escape))
        return res

    def preamble(self, headers=None):
        # before we spit out the data
        r = [self._headers]
        return r

    def _prepare(self):
        # generate the base query template
        c = [f.name for k, f in self.meta.fields.items()
            if not isinstance(f, HiddenField)]
        headers = ", ".join(c)
        replacements = ", ".join(["%(" + x + ")s" for x in c])
        template = self.base_template % (replacements)
        log.debug('emit template: %s', template)
        self._template = template
        self._headers = headers
