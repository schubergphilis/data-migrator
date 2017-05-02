#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator.models import Model, StringField, NullField, UUIDField
from data_migrator.exceptions import DataException

class TrialModel(Model):
    a = StringField(pos=0, key=True)
    b = StringField(pos=1)
    empty = NullField()
    uuid = UUIDField(required=True)

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
        o = TrialModel()
        self.assertEqual(o.a, '')
        self.assertEqual(o.b, '')
        self.assertIsNone(o.empty)
        self.assertIsNone(o._meta.strict)
        self.assertIsNotNone(o.uuid)
        self.assertNotEqual(o.uuid, '')
        self.assertEqual(str(o), 'TrialModel object')

    def test_init(self):
        '''model initialization'''
        d = {"a": "hello", "b": "World"}
        o1 = TrialModel(a="hello", b="world", empty="somevalue", uuid='bla')
        o2 = TrialModel(**d)
        self.assertEqual(o1.a, "hello")
        self.assertEqual(o1.empty, None)
        self.assertNotEqual(o1.uuid, 'bla')
        self.assertIsNotNone(o1.uuid)
        self.assertEqual(o2.a, "hello")
        self.assertEqual(o2._meta.model_name, "TrialModel")
        self.assertEqual(o2._meta.table_name, "new_name")

    def test_fail_extra_fields(self):
        '''don't except extra fields'''
        d = {"a":"hello", "b":"World", "c":"fail"}
        self.assertTrue(TrialModel(**d))
        t, TrialModel._meta.strict = TrialModel._meta.strict, True
        self.assertRaises(DataException, TrialModel, a="hello", b="world", c="fail")
        self.assertRaises(DataException, TrialModel, **d)
        TrialModel._meta.strict = t

    def test_remark(self):
        '''can set an addtional remark on this object'''
        remark = "additional remark"
        d = {"a": "hello", "b": "World", "description": remark}
        o1 = TrialModel(**d)
        self.assertEqual(o1.description, remark)

    def test_scan_row(self):
        '''can set object based on scan'''
        row = ['hello', 'world']
        o1 = TrialModel.objects.scan_row(row)
        self.assertEqual(o1[0].a, 'hello')

    def test_set(self):
        '''set values in a chain'''
        row = ['hello', 'world']
        o1 = TrialModel().scan(row).update(a='hallo')
        self.assertEqual(o1.a, 'hallo')

    def test_set_fail(self):
        '''set values in a chain'''
        row = ['hello', 'world']
        o1 = TrialModel().scan(row).update(a='hallo')
        t, TrialModel._meta.strict = TrialModel._meta.strict, True
        self.assertRaises(DataException, o1.update, d='hallo')
        TrialModel._meta.strict = t

    def test_default_emit(self):
        '''default values are returned on emit'''
        o = TrialModel()
        e = o.emit()
        self.assertEqual(e['a'], '')
        self.assertEqual(e['b'], '')

    def test_init_emit(self):
        '''(default) values are returned on emit'''
        o = TrialModel(a="hello", b=None)
        e = o.emit()
        self.assertEqual(e['a'], 'hello')
        self.assertEqual(e['b'], '')

    def test_json_schema(self):
        d = {"a": "hello", "b": "World", "c": "fail"}
        m = TrialModel(**d)
        self.assertTrue(m)
        t, TrialModel._meta.strict = TrialModel._meta.strict, True
        # print(TrialModel.json_schema())
        # print(m.json_schema())
        TrialModel._meta.strict = t

if __name__ == '__main__':
    unittest.main()
