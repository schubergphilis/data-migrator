#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import doctest

from data_migrator import utils


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(utils.sql))
    return tests

class TestFunctions(unittest.TestCase):

    def test_argparse(self):
        in_args = ['-i', 'hello', '--outdir', 'world']
        parser = utils.configure_parser()
        args = parser.parse_args(in_args)
        self.assertEqual(args.input, 'hello')
        self.assertEqual(args.outdir, 'world')

    def test_logging(self):
        self.assertTrue(utils.configure_logging())

    def test_parser(self):
        self.assertTrue(utils.default_parser())

class TestCSV(unittest.TestCase):
    def test_unflatten(self):
        a = {'hello__world': 1, 'hallo': 2, 'hi': 3, 'hello__welt': 4}
        b = utils.unflatten(a)
        self.assertEqual(b, {'hello': {'world': 1, 'welt': 4}, 'hallo': 2, 'hi': 3})

if __name__ == '__main__':
    unittest.main()
