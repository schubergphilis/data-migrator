#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator.models import SimpleManager
from data_migrator.models import Model, StringField
from data_migrator.exceptions import NonUniqueDataException

class ManagerModel(Model):
    a = StringField(pos=0, unique=True)
    b = StringField(pos=1)

    class Meta:
        drop_if_none = ['b']
        fail_non_unique = True

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


    def test_fail_non_unique(self):
        a = [
            ["foo", "bar"],
            ["foo", "bar"],
        ]
        self.assertRaises(NonUniqueDataException, ManagerModel.objects.scan_rows, a)

### Features to test
# 1. Validation
# 2. [Done] None test
# 3. [Done] Unique test
# 4. Fails and drops
# 5. [done] replace
# 6. [done] max_length scanning
