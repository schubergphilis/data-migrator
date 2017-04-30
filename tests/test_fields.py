#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator import models
from data_migrator.utils import sql_escape
from data_migrator.exceptions import ValidationException, DataException

class TestFields(unittest.TestCase):

    def test_basics(self):
        '''get the basics of parsing and emitting'''
        f = models.IntField(pos=0, name='f')
        self.assertEqual(f.default, 0)
        self.assertFalse(f.key)
        self.assertFalse(f.required)
        self.assertEqual(f.scan(row=["10", "20"]), 10)
        self.assertEqual(f.emit(10), 10)
        self.assertEqual(f.json_schema(), {'f':'integer'})

    def test_replacement_string(self):
        '''replacement facility'''
        f = models.StringField(replacement='hello {}', name='f')
        self.assertEqual(f.emit("world"), "hello world")
        self.assertEqual(f.json_schema(), {'f':'string'})

    def test_functions(self):
        '''check the functions for parsing and emitting'''
        f1 = lambda x: abs(int(x))
        f2 = lambda x: "number = %s"%x
        f = models.IntField(pos=0, parse=f1, replacement=f2)
        self.assertEqual(f.scan(row=["-10", "20"]), 10)
        self.assertEqual(f.emit(10), 'number = 10')
        self.assertEqual(f.emit(10, escaper=lambda x: "xx%sxx" % x), 'number = xx10xx')

    def test_default_null(self):
        '''null handling'''
        f = models.IntField(pos=0, nullable="NULL", default=10)
        self.assertEqual(f.scan(row=["NULL", "20"]), None)
        self.assertEqual(f.default, 10)
        self.assertEqual(f.emit(None), 10)

    def test_set_fields(self):
        '''null handling'''
        f = models.IntField(pos=0, key=True, required=True)
        self.assertTrue(f.key)
        self.assertTrue(f.required)

    def test_exception_int(self):
        '''exception generation'''
        f = models.IntField(pos=0)
        self.assertRaises(ValueError, f.scan, row=["BLA", "20"])

    def test_string_length(self):
        '''build in string trimming'''
        f = models.StringField(pos=0, max_length=3)
        self.assertEqual(f.emit("blablabla"), "bla")

    def test_null_string(self):
        '''dedicated null string fields'''
        f = models.NullStringField(pos=0, name='f')
        r = f.scan(row=["NULL"])
        self.assertIsNone(r)
        self.assertEqual(f.emit(r, escaper=sql_escape), "NULL")
        self.assertEqual(f.json_schema(), {'f':['string', 'null']})

    def test_null_int(self):
        '''dedicated null string fields'''
        f = models.NullIntField(pos=0, name='f')
        r = f.scan(row=["NULL"])
        self.assertIsNone(r)
        self.assertEqual(f.emit(r, escaper=sql_escape), "NULL")
        self.assertEqual(f.json_schema(), {'f':['integer', 'null']})

    def test_parse_value(self):
        '''add a parse function for a field'''
        f = models.IntField(pos=0, parse=lambda x: int(x) * 2)
        self.assertEqual(f.scan(row=["10", "20"]), 20)

    def test_parse_row(self):
        '''add a parse function for a field'''
        f = models.IntField(parse=lambda x: int(x[1]) * 2)
        self.assertEqual(f.scan(row=["10", "20"]), 40)

    def test_validation(self):
        '''validation exception generation'''
        f = models.IntField(pos=0, validate=lambda x: int(x) < 100)
        self.assertRaises(ValidationException, f.scan, row=["200", "20"])

    def test_mapping_field(self):
        '''basic mapping field'''
        f = models.MappingField(pos=0, default="bad", data_map={"10": "hello", "200": "world"})
        self.assertEqual(f.scan(row=["200", "20"]), "200")
        self.assertEqual(f.emit("10"), "hello")
        self.assertEqual(f.emit("200"), "world")
        self.assertEqual(f.emit("mis"), "bad")
        self.assertEqual(f.emit(None), "bad")

    def test_mapping_field_list(self):
        '''mapping field with lists'''
        f = models.MappingField(pos=0, default=[], data_map={"10": ["hello"], "200": ["world"]})
        self.assertEqual(f.emit("10"), ["hello"])
        self.assertEqual(f.emit("200"), ["world"])
        self.assertEqual(f.emit("mis"), [])
        f.as_json = True
        self.assertEqual(f.emit("10"), '["hello"]')
        self.assertEqual(f.emit("200"), '["world"]')
        self.assertEqual(f.emit("mis"), '[]')

    def test_mapping_field_strict(self):
        '''mapping field in a strict way'''
        f = models.MappingField(pos=0, strict=True, default="bad", data_map={"10": "hello", "200": "world"})
        self.assertRaises(DataException, f.emit, "mis")

    def test_uuid_field(self):
        '''uuid field'''
        f = models.UUIDField(name='f')
        self.assertIsNone(f.default)
        self.assertEqual(f.emit("some value"), "some value")
        self.assertEqual(f.json_schema(), {'f':'string'})

    def test_uuid_field_default(self):
        '''uuid field, trying to set default'''
        f = models.UUIDField(default='bla')
        self.assertEqual(f.emit("some value"), "some value")
        self.assertNotEqual(f.default, 'bla')
        self.assertIsNone(f.default)

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



if __name__ == '__main__':
    unittest.main()
