#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator import models

class TestFields(unittest.TestCase):

    def test_jsonfield(self):
        f = models.JSONField()
        self.assertEqual(f.emit("10"), '"10"')
        self.assertEqual(f.emit(["200"]), '["200"]')
        self.assertEqual(f.emit("mis"), '"mis"')
        self.assertEqual(f.emit(None), "null")
        f = models.JSONField(default=[])
        self.assertEqual(f.emit(None), "[]")
        f = models.JSONField(default="bla")
        self.assertEqual(f.emit(None), '"bla"')

    def test_arrayfield(self):
        f = models.ArrayField(name='f')
        self.assertEqual(f.json_schema(), {'f': {'type': 'array'}})
        f2 = models.ListField(name='f', key=True)
        self.assertEqual(f2.json_schema(), {'f': {'type': 'array', 'key': True}})

    def test_objectfield(self):
        f = models.DictField(name='f', key=True)
        self.assertEqual(f.json_schema(), {'f': {'type': 'object', 'key': True}})
        f2 = models.ObjectField(name='f')
        self.assertEqual(f2.json_schema(), {'f': {'type': 'object'}})

    def test_modelfield(self):
        f2 = models.ModelField(name='f', strict=True, fields={'left': models.NullIntField(required=True), 'right': models.StringField(max_length=20)})
        self.assertEqual(f2.json_schema(),
                         {'f': {
                            'additionalProperties': False,
                            'properties': {
                                'left': {'type': ['integer', 'null']},
                               'right': {'maxLength': 20, 'type': 'string'}},
                            'type': 'object'
                            }})

if __name__ == '__main__':
    unittest.main()
