#!/usr/bin/python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator import utils

class TestFunctions(unittest.TestCase):

    def test_sql_escape(self):
        '''sql_escape tester'''
        v = [
            (None, "NULL"),
            ("hello", '"hello"'),
            ('["hello"]', '"[""hello""]"'),
            ('{"hello":"world"}', '"{""hello"":""world""}"'),
            (0, "0"),
            ("0", '"0"'),
            ('0', '"0"'),
        ]

        for i,o in v:
            self.assertEqual(utils.sql_escape(i), o)

    def test_argparse(self):
        '''argparse tester'''
        in_args = ['-i', 'hello', '--outdir', 'world']
        args = utils.configure_parser(in_args)
        self.assertEquals(args.input, 'hello')
        self.assertEquals(args.outdir, 'world')


if __name__ == '__main__':
    unittest.main()
