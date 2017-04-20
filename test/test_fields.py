#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator import models
from data_migrator.utils import sql_escape
from data_migrator.exceptions import ValidationException, DataException

class TestFields(unittest.TestCase):

    def test_basics(self):
        '''get the basics of parsing and emitting'''
        f = models.IntField(pos=0)
        self.assertEquals(f.default(), 0)
        self.assertEquals(f.scan(row=["10","20"]), 10)
        self.assertEquals(f.emit(10), 10)

    def test_functions(self):
        '''check the functions for parsing and emitting'''
        f1 = lambda x:abs(int(x))
        f2 = lambda x:"number = %s"%x
        f = models.IntField(pos=0, parse=f1, replace=f2)
        self.assertEquals(f.scan(row=["-10","20"]), 10)
        self.assertEquals(f.emit(10), 'number = 10')
        self.assertEquals(f.emit(10, escaper=lambda x:"xx%sxx" % x), 'number = xx10xx')

    def test_default_null(self):
        '''null handling'''
        f = models.IntField(pos=0, null="NULL", default=10)
        self.assertEquals(f.scan(row=["NULL","20"]), None)
        self.assertEquals(f.default(), 10)
        self.assertEquals(f.emit(None), 10)

    def test_exception(self):
        '''exception generation'''
        f = models.IntField(pos=0)
        self.assertRaises(ValueError, f.scan, row=["BLA","20"])

    def test_string_length(self):
        '''build in string trimming'''
        f = models.StringField(pos=0, max_length=3)
        self.assertEquals(f.emit("blablabla"), "bla")

    def test_null_string(self):
        '''dedicated null string fields'''
        f = models.NullStringField(pos=0)
        r = f.scan(row=["NULL"])
        self.assertIsNone(r)
        self.assertEquals(f.emit(r, escaper=sql_escape), "NULL")

    def test_null_int(self):
        '''dedicated null string fields'''
        f = models.NullIntField(pos=0)
        r = f.scan(row=["NULL"])
        self.assertIsNone(r)
        self.assertEquals(f.emit(r, escaper=sql_escape), "NULL")

    def test_parse_value(self):
        '''add a parse function for a field'''
        f = models.IntField(pos=0, parse=lambda x: int(x) * 2)
        self.assertEquals(f.scan(row=["10","20"]), 20)

    def test_parse_row(self):
        '''add a parse function for a field'''
        f = models.IntField(parse=lambda x: int(x[1]) * 2)
        self.assertEquals(f.scan(row=["10","20"]), 40)

    def test_validation(self):
        '''validation exception generation'''
        f = models.IntField(pos=0, validate=lambda x: x < 100)
        self.assertRaises(ValidationException, f.scan, row=["200","20"])

    def test_mapping_field(self):
        '''test mapping field'''
        f = models.MappingField(pos=0, default="bad", data_map={"10": "hello", "200": "world"})
        self.assertEquals(f.scan(row=["200","20"]), "200")
        self.assertEquals(f.emit("10"), "hello")
        self.assertEquals(f.emit("200"), "world")
        self.assertEquals(f.emit("mis"), "bad")

    def test_mapping_field_list(self):
        '''test mapping field with lists'''
        f = models.MappingField(pos=0, default=[], data_map={"10": ["hello"], "200": ["world"]})
        self.assertEquals(f.emit("10"), ["hello"])
        self.assertEquals(f.emit("200"), ["world"])
        self.assertEquals(f.emit("mis"), [])

    def test_mapping_field_strict(self):
        '''test mapping field'''
        f = models.MappingField(pos=0, strict=True, default="bad", data_map={"10": "hello", "200": "world"})
        self.assertRaises(DataException, f.emit, "mis")


if __name__ == '__main__':
    unittest.main()
