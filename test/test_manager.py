#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator.models import SimpleManager
from data_migrator.models import Model, StringField


class ManagerModel(Model):
    a = StringField(pos=0)
    b = StringField(pos=1)

    class Meta:
        drop_if_none = ['b']

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
        self.assertEqual(a.unique_values, {})

    def test_scan(self):
        a = [
            ["hello", "world"],
            ["goodbye", "cruel world"],
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

### Features to test
# 1. Validation
# 2. None test
# 3. Unique test
# 4. Fails and drops
# 5. replace
# 6. max_length scanning
