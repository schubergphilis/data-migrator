import unittest

from data_migrator.contrib.dutch import clean_phone

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
