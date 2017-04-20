#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator.models import Model, StringField
from data_migrator.exceptions import DataException

class TrailModel(Model):
    a = StringField(pos=0)
    b = StringField(pos=1)

    class Meta:
        table_name = "new_name"
        remark = "description"

class TestModel(unittest.TestCase):

    def test_basic(self):
        '''Model Testing'''
        class BasicModel(Model):
            pass
        self.assertEquals(BasicModel._meta.model_name, "BasicModel")

    def test_default_init(self):
        '''model default initialization'''
        o = TrailModel()
        self.assertIsNone(o.a)
        self.assertIsNone(o.b)

    def test_init(self):
        '''model initialization'''
        d = {"a":"hello", "b":"World"}
        o1 = TrailModel(a="hello", b="world")
        o2 = TrailModel(**d)
        self.assertEquals(o1.a, "hello")
        self.assertEquals(o2.a, "hello")
        self.assertEquals(o2._meta.model_name, "TrailModel")
        self.assertEquals(o2._meta.table_name, "new_name")

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
        self.assertEquals(o1.description, remark)

    def test_scan_row(self):
        '''can set object based on scan'''
        row = ['hello', 'world']
        o1 = TrailModel.objects.scan_row(row)
        self.assertEquals(o1[0].a, 'hello')

    def test_default_emit(self):
        '''default values are returned on emit'''
        o = TrailModel()
        e = o.emit()
        self.assertEquals(e['a'], '')
        self.assertEquals(e['b'], '')

    def test_init_emit(self):
        '''(default) values are returned on emit'''
        o = TrailModel(a="hello", b=None)
        e = o.emit()
        self.assertEquals(e['a'], 'hello')
        self.assertEquals(e['b'], '')

if __name__ == '__main__':
    unittest.main()
