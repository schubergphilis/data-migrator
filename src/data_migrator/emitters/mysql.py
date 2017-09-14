#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from data_migrator.emitters.base import BaseEmitter
from data_migrator.models.fields import HiddenField
from data_migrator.utils import sql_escape, default_logger

log = default_logger()


class MySQLEmitter(BaseEmitter):
    '''MySQL emitter to output MySQL specific insert statements

    Attributes:
        base_template: base template to output the object
        extension (str): file extension for output file of this emitter.
            Defaults to .sql
    '''
    base_template = '''INSERT %sINTO `%s` (%s) VALUES (%s);'''
    extension = '.sql'

    def __init__(self, *args, **kwargs):
        super(MySQLEmitter, self).__init__(*args, **kwargs)
        self._prepare()

    def emit(self, l):
        '''Output the result set of an object as MYSQL insert statement'''
        res = []
        if hasattr(l, self.meta.remark):
            res.append("# %s" % getattr(l, self.meta.remark))
        res.append(self._template % l.emit(escaper=sql_escape))
        return res

    def preamble(self, headers):
        '''override the preamble method to make it specific for MySQL'''
        # before we spit out the data
        _meta = self.meta
        h1 = [
            "transformation for %s to table %s" % (_meta.model_name, _meta.table_name),
            "input headers: %s" % ",".join(headers),
            'stats: %s' % ",".join(["%s=%d" % (k, v) for k, v in self.manager.stats().items()]),
        ]
        r = []
        r += ['# %s' % l for l in h1]
        r += [""]
        if isinstance(_meta.prefix, list):
            r += ["%s" % l for l in _meta.prefix]
        else:
            r += [
                "SET SQL_SAFE_UPDATES = 0; -- you need this to delete without WHERE clause",
                "DELETE FROM `%s`;" % _meta.table_name,   #nosec
                "ALTER TABLE `%s` AUTO_INCREMENT = 1;" % _meta.table_name,
            ]
        r += [""]
        return r

    def _prepare(self):
        # generate the base query template
        c = [f.name for k, f in self.meta.fields.items() if not isinstance(f, HiddenField)]
        columns = ", ".join(["`" + x + "`" for x in c])
        replacements = ", ".join(["%(" + x + ")s" for x in c])
        _ignore = 'IGNORE ' if self.meta.drop_non_unique else ''
        template = self.base_template % (_ignore, self.meta.table_name, columns, replacements)
        log.debug('emit template: %s', template)
        self._template = template
