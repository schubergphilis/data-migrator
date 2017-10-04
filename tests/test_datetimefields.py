#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import datetime

from data_migrator import models


class TestDateTimeFields(unittest.TestCase):

    def test_basics(self):
        f = models.DateTimeField(format="%d-%m-%Y", pos=0, name='f')
        self.assertEqual(f.scan(row=[datetime.datetime(2017, 10, 2)]), datetime.datetime(2017, 10, 2))
        self.assertEqual(f.emit(datetime.datetime(2017, 10, 2)), "02-10-2017")
        self.assertEqual(f.json_schema(), {'f': {'type': 'string', 'format': 'date-time'}})

if __name__ == '__main__':
    unittest.main()
