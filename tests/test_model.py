#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator.models import Model, StringField, NullField, UUIDField
from data_migrator.exceptions import DataException

class TrailModel(Model):
    a = StringField(pos=0)
    b = StringField(pos=1)
    empty = NullField()
    uuid = UUIDField()

    class Meta:
        table_name = "new_name"
        remark = "description"

class TestModel(unittest.TestCase):

    def test_basic(self):
        '''Model Testing'''
        class BasicModel(Model):
            pass
        self.assertEqual(BasicModel._meta.model_name, "BasicModel")

    def test_default_init(self):
        '''model default initialization'''
        o = TrailModel()
        self.assertEqual(o.a, '')
        self.assertEqual(o.b, '')
        self.assertIsNone(o.empty)
        self.assertIsNotNone(o.uuid)
        self.assertNotEqual(o.uuid, '')
        self.assertEqual(str(o), 'TrailModel object')

    def test_init(self):
        '''model initialization'''
        d = {"a":"hello", "b":"World"}
        o1 = TrailModel(a="hello", b="world", empty="somevalue", uuid='bla')
        o2 = TrailModel(**d)
        self.assertEqual(o1.a, "hello")
        self.assertEqual(o1.empty, None)
        self.assertNotEqual(o1.uuid, 'bla')
        self.assertIsNotNone(o1.uuid)
        self.assertEqual(o2.a, "hello")
        self.assertEqual(o2._meta.model_name, "TrailModel")
        self.assertEqual(o2._meta.table_name, "new_name")

    def test_fail_extra_fields(self):
        '''don't except extra fields'''
        d = {"a":"hello", "b":"World", "c":"fail"}
        self.assertRaises(DataException, TrailModel, a="hello", b="world", c="fail")
        self.assertRaises(DataException, TrailModel, **d)

    def test_remark(self):
        '''can set an addtional remark on this object'''
        remark = "additional remark"
        d = {"a":"hello", "b":"World", "description":remark}
        o1 = TrailModel(**d)
        self.assertEqual(o1.description, remark)

    def test_scan_row(self):
        '''can set object based on scan'''
        row = ['hello', 'world']
        o1 = TrailModel.objects.scan_row(row)
        self.assertEqual(o1[0].a, 'hello')

    def test_default_emit(self):
        '''default values are returned on emit'''
        o = TrailModel()
        e = o.emit()
        self.assertEqual(e['a'], '')
        self.assertEqual(e['b'], '')

    def test_init_emit(self):
        '''(default) values are returned on emit'''
        o = TrailModel(a="hello", b=None)
        e = o.emit()
        self.assertEqual(e['a'], 'hello')
        self.assertEqual(e['b'], '')

if __name__ == '__main__':
    unittest.main()
