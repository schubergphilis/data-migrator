#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json

from data_migrator.emitters.base import BaseEmitter
from data_migrator.utils import default_logger

log = default_logger()


class JSONEmitter(BaseEmitter):
    '''JSON emitter to output as JSON Messages


    Attributes:
        extension (str): file extension for output file of this emitter.
            Defaults to .json
    '''
    extension = '.json'

    def __init__(self, *args, **kwargs):
        super(JSONEmitter, self).__init__(*args, **kwargs)

    def emit(self, l):
        '''Output the result set of an object as JSON dump'''
        return [json.dumps(l.emit())]

    def preamble(self, headers=None):
        pass
