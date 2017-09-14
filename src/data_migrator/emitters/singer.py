#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json

from data_migrator.emitters.base import BaseEmitter
from data_migrator.utils import default_logger

log = default_logger()


class SingerEmitter(BaseEmitter):
    '''Singer.IO emitter to output transformations into singer format

    Attributes:
        extension (str): file extension for output file of this emitter.
            Defaults to .sng
    '''
    extension = '.sng'

    def __init__(self, *args, **kwargs):
        super(SingerEmitter, self).__init__(*args, **kwargs)

    def emit(self, l):
        '''Output the result set of an object a singer.io record'''
        res = []
        if hasattr(l, self.meta.remark):
            res.append("# %s" % getattr(l, self.meta.remark))
        _record = {'type': "RECORD", "stream": self.meta.table_name, "record": l.emit()}
        res.append(json.dumps(_record))
        return res

    def preamble(self, headers):
        '''Singer has a schema as preamble'''
        # before we spit out the data
        _schema = self.model_class.json_schema()
        _schema = {'type': "SCHEMA", "stream": self.meta.table_name, "schema": _schema, "key_properties": _schema.get('required', [])}
        return [json.dumps(_schema)]

    def postamble(self):
        '''Singer has a state as postamble'''
        _state = self.model_class.json_schema()
        _state = {'type': "STATE", "stream": self.meta.table_name, "value": []}
        return [json.dumps(_state)]
