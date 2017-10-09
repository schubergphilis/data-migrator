#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import doctest
from io import StringIO

from data_migrator.contrib.read import read_map_from_csv
from data_migrator.exceptions import DefinitionException, NonUniqueDataException
from data_migrator.contrib import dutch

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(dutch))
    return tests

class TestRead(unittest.TestCase):
    def test_reader(self):
        f = StringIO(u'key,value\nhello,world\nhappy,camper\n')
        a = read_map_from_csv(key='key', value='value', f=f, delimiter=',')
        self.assertIn('hello', a)

    def test_reader_as_list(self):
        f = StringIO(u'key,value\nhello,world\nhello,camper\nfoo,bar\n')
        a = read_map_from_csv(key='key', value='value', f=f, delimiter=',', as_list=True)
        self.assertEqual(a['hello'], ['world', 'camper'])

    def test_reader_no_header(self):
        f = StringIO(u'hello,world\nhappy,camper\n')
        a = read_map_from_csv(key=0, value=1, header=False, f=f, delimiter=',')
        self.assertIn('hello', a)

    def test_reader_no_header_default(self):
        f = StringIO(u'hello,world\nhappy,camper\n')
        a = read_map_from_csv(header=False, f=f, delimiter=',')
        self.assertIn('hello', a)

    def test_reader_no_header_reverse(self):
        f = StringIO(u'hello,world\nhappy,camper\n')
        a = read_map_from_csv(key=1, value=0, header=False, f=f, delimiter=',')
        self.assertIn('world', a)

    def test_reader_fail(self):
        o = [
            (0, 'bla', 'value', u'key,value\nhello,world\nhappy,camper\n', ',', None, False, False, False, DefinitionException),
            (1, 'key', 'bla', u'key,value\nhello,world\nhappy,camper\n', ',', None, False, False, False, DefinitionException),
            (2, 0, 'value', u'key,value\nhello,world\nhappy,camper\n', ',', None, False, False, False, DefinitionException),
            (3, 'key', 0, u'key,value\nhello,world\nhappy,camper\n', ',', None, False, False, False, DefinitionException),
            (4, 'key', 'value', u'key,value\nhello,world\nhello,camper\n', ',', 1, False, False, False, None),
            (5, 'key', 'value', u'key,value\nhello,world\nhello,camper\n', ',', None, True, False, False, NonUniqueDataException),
            (6, 'key', 'value', u'key;value\nhello;world\nhello;camper\n', ';', 1, False, False, False, None),
            (7, 'key', 'value', u'key;value\nhello;world\nhello;camper\n', ';', 1, False, False, True, None),
            (8, 'key', 'value', u'key;value\nhallo;world\nhello;camper\n', ';', 2, False, False, True, None),
        ]
        for row, key, value, data, delim,size,u,first,as_list, exc in o:
            f = StringIO(data)
            if exc:
                with self.assertRaises(exc) as err:
                    read_map_from_csv(key=key, value=value, f=f, delimiter=delim, unique=u, first=first)
                    self.assertEqual(exc, err, "%d failed" % row)
            else:
                self.assertEqual(len(read_map_from_csv(key=key, value=value, f=f, delimiter=delim, unique=u, first=first, as_list=as_list)), size, "%d failed" % row)
