#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import six

from data_migrator import models

class DefaultModel(models.Model):
    a = models.HiddenField(pos=0)
    b = models.IntField(pos=1)
    c = models.NullIntField(pos=2)
    d = models.StringField(pos=3)
    e = models.NullStringField(pos=4)
    f = models.BooleanField(pos=5)
    g = models.NullField(pos=6)
    h = models.UUIDField(pos=7)
    i = models.JSONField(pos=8)
    j = models.MappingField(pos=8, data_map={"M":"Male", "F": "Female"})

class TestModel(unittest.TestCase):

    def test_basic(self):
        '''Model Testing'''
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
        '''Model Testing'''
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
