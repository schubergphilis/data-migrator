#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import six

from data_migrator import models

class DefaultModel(models.Model):
    a = models.HiddenField(pos=0)
    b = models.IntField(pos=1, key=True)
    c = models.NullIntField(pos=2)
    d = models.StringField(pos=3)
    e = models.NullStringField(pos=4)
    f = models.BooleanField(pos=5)
    g = models.NullField(pos=6)
    h = models.UUIDField(pos=7)
    i = models.JSONField(pos=8)
    j = models.MappingField(pos=8, data_map={"M":"Male", "F": "Female"})

class TestDefaultModel(unittest.TestCase):

    def test_basic(self):
        m = DefaultModel()
        self.assertIsNone(m.a)
        self.assertEqual(m.b, 0)
        self.assertEqual(m.c, None)
        self.assertEqual(m.d, '')
        self.assertEqual(m.e, None)
        self.assertEqual(m.f, False)
        self.assertIsNone(m.g)
        six.assertRegex(self, m.h, u'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
        self.assertEqual(m.i, None)
        self.assertEqual(m.j, None)

    def test_init(self):
        m = DefaultModel(a="bla", b=2, c=None, d="d", e=None, f=True, g="bla", h="uuid", i=["json"], j="M")
        self.assertEqual(m.a, "bla")
        self.assertEqual(m.b, 2)
        self.assertEqual(m.c, None)
        self.assertEqual(m.d, 'd')
        self.assertEqual(m.e, None)
        self.assertEqual(m.f, False)
        self.assertIsNone(m.g)
        six.assertRegex(self, m.h, u'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
        self.assertEqual(m.i, ["json"])
        self.assertEqual(m.j, "M")

    def test_json_fields(self):
        m = DefaultModel._meta
        f = m.fields
        self.assertEqual(f['a'].json_schema(), {'a': {'type': 'object'}})
        self.assertEqual(f['b'].json_schema(), {'b': {'type': 'integer', 'key': True}})
        self.assertEqual(f['c'].json_schema(), {'c': {'type': ['integer', 'null']}})
        self.assertEqual(f['d'].json_schema(), {'d': {'type': 'string'}})
        self.assertEqual(f['e'].json_schema(), {'e': {'type': ['string', 'null']}})
        self.assertEqual(f['f'].json_schema(), {'f': {'type': 'boolean'}})
        self.assertEqual(f['g'].json_schema(), {'g': {'type': 'null'}})
        self.assertEqual(f['h'].json_schema(), {'h': {'type': 'string'}})
        self.assertEqual(f['i'].json_schema(), {'i': {'type': 'object'}})
        self.assertEqual(f['j'].json_schema(), {'j': {'type': 'object'}})

    def test_json_schema(self):
        self.assertEqual(DefaultModel.json_schema(),
                        {
                            '$schema': 'http://json-schema.org/draft-04/schema',
                            'properties': {
                                'b': {'type': 'integer', 'key': True},
                                'c': {'type': ['integer', 'null']},
                                'd': {'type': 'string'},
                                'e': {'type': ['string', 'null']},
                                'f': {'type': 'boolean'},
                                'g': {'type': 'null'},
                                'h': {'type': 'string'},
                                'i': {'type': 'object'},
                                'j': {'type': 'object'}},
                            'type': 'object',
                            'required': ['b']
                        })
