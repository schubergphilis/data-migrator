#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator.contrib.dutch import clean_phone, clean_zip_code

class TestDutch(unittest.TestCase):
    def test_phone(self):
        '''test phone cleaner'''
        l = [
            ('00 31 6 - 20 20 20 20','+31620202020'),
            ('06 20 20 20 20','+31620202020'),
            ('020 -123 345 6','+31201233456'),
            ('+440.203.020.23','+44020302023'),
            ('+440 ada 203.020 // 23','+44020302023'),
        ]
        for i, o in l:
            self.assertEquals(o, clean_phone(i))

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
            self.assertEquals(o, clean_zip_code(i))
