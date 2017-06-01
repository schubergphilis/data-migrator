#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator.models import SimpleManager
from data_migrator.models import Model, StringField
from data_migrator.exceptions import NonUniqueDataException, ValidationException

class ManagerModel(Model):
    a = StringField(pos=0, unique=True)
    b = StringField(pos=1, validate=lambda x:len(x)<=10)

    class Meta:
        drop_if_none = ['b']
        drop_non_unique = True
        fail_non_unique = True
        fail_not_validated = True

class TestFields(unittest.TestCase):
    def test_init(self):
        '''basic manager, default init'''
        a= SimpleManager()
        self.assertEqual(a.rows, 0)
        self.assertEqual(a.dropped, 0)

    def test_empty_prepare(self):
        '''low level prepare step, done by ModelBase'''
        a= SimpleManager()
        a._prepare(ManagerModel)
        self.assertIn('a', a.unique_values)

    def test_scan(self):
        a = [
            ["hallo", "wereld"],
            ["bon jour", "le monde"],
        ]
        l = len(ManagerModel.objects)
        ManagerModel.objects.scan_rows(a)
        l2 = len(ManagerModel.objects)
        self.assertEqual(l+2, l2)
        s = ManagerModel.objects.stats()
        self.assertEqual(s['out'], l2)

    def test_save(self):
        self.assertFalse(ManagerModel.objects.save([]))
        a = ManagerModel(a="ciao", b="mondo")
        self.assertTrue(ManagerModel.objects.save(a))
        a = ManagerModel(a="adios", b="mundo")
        self.assertTrue(ManagerModel.objects.save([a]))

    def test_drop_if_none(self):
        a = [
          ["hello", "world"],
          ["goodbye", "NULL"],
        ]
        l = len(ManagerModel.objects)
        ManagerModel.objects.scan_rows(a)
        l2 = len(ManagerModel.objects)
        self.assertEqual(l+1, l2)
        s = ManagerModel.objects.stats()
        self.assertEqual(s['out'], l2)


    def test_fail_unique(self):
        a = [
          ["foo", "bar"],
          ["foo", "bar"],
        ]
        self.assertRaises(NonUniqueDataException, ManagerModel.objects.scan_rows, a)
        ManagerModel._meta.fail_non_unique = False
        self.assertFalse(ManagerModel.objects.scan_rows(a))

    def test_fail_validation(self):
        a = [
          ["foo", "foo_and_bar_and_more"],
        ]
        self.assertRaises(ValidationException, ManagerModel.objects.scan_rows, a)
        ManagerModel._meta.fail_not_validated = False
        self.assertFalse(ManagerModel.objects.scan_rows(a))
