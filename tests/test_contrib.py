#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
from io import StringIO

from data_migrator.contrib.dutch import clean_phone, clean_zip_code
from data_migrator.contrib.read import read_map_from_csv
from data_migrator.exceptions import DefinitionException, NonUniqueDataException

class TestDutch(unittest.TestCase):
    def test_phone(self):
        '''test phone cleaner'''
        l = [
            ('00 31 6 - 20 20 20 20', '+31620202020'),
            ('06 20 20 20 20', '+31620202020'),
            ('020 -123 345 6', '+31201233456'),
            ('+440.203.020.23', '+44020302023'),
            ('+440 ada 203.020 // 23', '+44020302023'),
            ('31 (6) - 20 20 20 20', '+31620202020'),
        ]
        for i, o in l:
            self.assertEqual(o, clean_phone(i))

    def test_zip_code(self):
        '''test zip code'''
        l = [
            ('1234 AB','1234AB'),
            ('1234ba','1234BA'),
            ('1234    ba','1234BA'),
            ('1 2 3 4 A B','1 2 3 4 A B'),
            ('blabla', 'blabla')
        ]
        for i, o in l:
            self.assertEqual(o, clean_zip_code(i))


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
            ('bla', 'value', u'key,value\nhello,world\nhappy,camper\n', ',', False, DefinitionException),
            ('key', 'bla', u'key,value\nhello,world\nhappy,camper\n', ',', False, DefinitionException),
            (0, 'value', u'key,value\nhello,world\nhappy,camper\n', ',', False, DefinitionException),
            ('key', 0, u'key,value\nhello,world\nhappy,camper\n', ',', False, DefinitionException),
            ('key', 'value', u'key,value\nhello,world\nhello,camper\n', ',', False, DefinitionException),
            ('key', 'value', u'key,value\nhello,world\nhello,camper\n', ',', True, NonUniqueDataException),
        ]
        for k,v,f,d,u,exc in o:
            f = StringIO(f)
            self.assertRaises(exc, read_map_from_csv, key=k, value=v, f=f, delimiter=d, unique=u)
