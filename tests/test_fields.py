#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator import models
from data_migrator.utils import sql_escape
from data_migrator.exceptions import ValidationException, DataException
from data_migrator.exceptions import DefinitionException

class TestFields(unittest.TestCase):

    def test_basics(self):
        f = models.IntField(pos=0, name='f')
        self.assertEqual(f.default, 0)
        self.assertFalse(f.key)
        self.assertFalse(f.required)
        self.assertEqual(f.scan(row=["10", "20"]), 10)
        self.assertEqual(f.emit(10), 10)
        self.assertEqual(f.json_schema(), {'f': {'type': 'integer'}})

    def test_replacement_string(self):
        f = models.StringField(replacement='hello {}', name='f')
        self.assertEqual(f.emit("world"), "hello world")
        self.assertEqual(f.json_schema(), {'f': {'type': 'string'}})

    def test_replacement_escape_string(self):
        f = models.StringField(replacement='hello {}', name='f')
        self.assertEqual(f.emit("world", escaper=lambda x: "xx%sxx" % x),
                         "hello world")
        self.assertEqual(f.json_schema(), {'f': {'type': 'string'}})

    def test_functions(self):
        f1 = lambda x: abs(int(x))
        f2 = lambda x: "number = %s"%x
        f = models.IntField(pos=0, parse=f1, replacement=f2)
        self.assertEqual(f.scan(row=["-10", "20"]), 10)
        self.assertEqual(f.emit(10), 'number = 10')
        self.assertEqual(f.emit(10, escaper=lambda x: "xx%sxx" % x),
                         'number = 10')
        f3 = models.IntField(pos=0, parse=f1, replacement="number = {}")
        self.assertEqual(f3.scan(row=["-10", "20"]), 10)
        self.assertEqual(f3.emit(10), 'number = 10')
        self.assertEqual(f3.emit(10, escaper=lambda x: "xx%sxx" % x),
                         'number = 10')

    def test_default_null(self):
        f = models.IntField(pos=0, nullable="NULL", default=10)
        self.assertEqual(f.scan(row=["NULL", "20"]), None)
        self.assertEqual(f.default, 10)
        self.assertEqual(f.emit(None), 10)

    def test_set_fields(self):
        f = models.IntField(pos=0, key=True, required=True)
        self.assertTrue(f.key)
        self.assertTrue(f.required)

    def test_exception_int(self):
        f = models.IntField(pos=0)
        self.assertRaises(ValueError, f.scan, row=["BLA", "20"])

    def test_max_length_notset(self):
        f = models.StringField(pos=0, max_length='something wrong')
        self.assertEqual(f.emit("blablabla"), "blablabla")
        self.assertFalse(f.max_length, None)

    def test_max_length_fail(self):
        self.assertRaises(DefinitionException, models.IntField,
                          pos=0, max_length=10)

    def test_string_length(self):
        f = models.StringField(pos=0, max_length=3, name='f')
        self.assertEqual(f.emit("blablabla"), "bla")
        self.assertEqual(f.json_schema(), {'f': {'type': 'string', 'maxLength': 3}})

    def test_null_string(self):
        f = models.NullStringField(pos=0, name='f')
        r = f.scan(row=["NULL"])
        self.assertIsNone(r)
        self.assertEqual(f.emit(r, escaper=sql_escape), "NULL")
        self.assertEqual(f.json_schema(), {'f': {'type': ['string', 'null']}})

    def test_null_int(self):
        f = models.NullIntField(pos=0, name='f')
        r = f.scan(row=["NULL"])
        self.assertIsNone(r)
        self.assertEqual(f.emit(r, escaper=sql_escape), "NULL")
        self.assertEqual(f.json_schema(), {'f': {'type': ['integer', 'null']}})

    def test_parse_value(self):
        f = models.IntField(pos=0, parse=lambda x: int(x) * 2)
        self.assertEqual(f.scan(row=["10", "20"]), 20)

    def test_parse_row(self):
        f = models.IntField(parse=lambda x: int(x[1]) * 2)
        self.assertEqual(f.scan(row=["10", "20"]), 40)

    def test_validation(self):
        f = models.IntField(pos=0, validate=lambda x: int(x) < 100)
        self.assertRaises(ValidationException, f.scan, row=["200", "20"])

    def test_mapping_field(self):
        f = models.MappingField(pos=0, default="bad", data_map={"10": "hello", "200": "world"})
        self.assertEqual(f.scan(row=["200", "20"]), "200")
        self.assertEqual(f.emit("10"), "hello")
        self.assertEqual(f.emit("200"), "world")
        self.assertEqual(f.emit("mis"), "bad")
        self.assertEqual(f.emit(None), "bad")

    def test_mapping_field_list(self):
        f = models.MappingField(pos=0, default=[], data_map={"10": ["hello"], "200": ["world"]})
        self.assertEqual(f.emit("10"), ["hello"])
        self.assertEqual(f.emit("200"), ["world"])
        self.assertEqual(f.emit("mis"), [])
        f.as_json = True
        self.assertEqual(f.emit("10"), '["hello"]')
        self.assertEqual(f.emit("200"), '["world"]')
        self.assertEqual(f.emit("mis"), '[]')

    def test_mapping_field_strict(self):
        f = models.MappingField(pos=0, strict=True, default="bad", data_map={"10": "hello", "200": "world"})
        self.assertRaises(DataException, f.emit, "mis")

    def test_uuid_field(self):
        f = models.UUIDField(name='f')
        self.assertIsNone(f.default)
        self.assertEqual(f.emit("some value"), "some value")
        self.assertEqual(f.json_schema(), {'f': {'type': 'string'}})

    def test_uuid_field_default(self):
        f = models.UUIDField(default='bla')
        self.assertEqual(f.emit("some value"), "some value")
        self.assertNotEqual(f.default, 'bla')
        self.assertIsNone(f.default)

if __name__ == '__main__':
    unittest.main()
