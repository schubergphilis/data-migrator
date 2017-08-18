#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import random
import string
from collections import Counter
from itertools import repeat

from data_migrator.anonymizors import SimpleStringAnonymizor
from data_migrator.anonymizors import TextAnonymizor
from data_migrator.anonymizors import ChoiceAnonymizor

from data_migrator.models import Model, StringField

class TrialModel(Model):
    a = StringField(pos=0, key=True, anonymize=TextAnonymizor)
    b = StringField(pos=1)
    gender = StringField(anonymize=ChoiceAnonymizor(["M", "F", None],
        weights=[0.3, 0.3, 0.4]))

def strp(v):
    return "".join([random.choice(string.printable) for x in v if x in string.punctuation+string.whitespace])

class TestFunctions(unittest.TestCase):

    def test_simple_string(self):
        a = SimpleStringAnonymizor()
        self.assertNotEqual(a("hello world"), "hello world")
        self.assertEqual(len(a("hello world")), len("hello world"))

    def test_text(self):
        a = "Hello world. This is a love letter!"
        b = TextAnonymizor()(a)
        self.assertNotEqual(b, a)
        self.assertEqual(len(a), len(b))
        self.assertEqual(len(strp(a)), len(strp(b)))

    def test_choices(self):
        c = ['M', 'F', None]
        w = [0.1, 0.3, 0.6]
        b = ChoiceAnonymizor(c, w)
        r = Counter([fn('-') for fn in repeat(b, 100)])
        self.assertLess(r['M'], r['F'])
        self.assertLess(r['F'], r[None])


class TestAnonymizeIntegration(unittest.TestCase):

    def test_model(self):
        t = "Hello, world!"
        a = TrialModel(a=t)
        e = a.emit()
        self.assertNotEqual(t, e['a'])
        self.assertEqual(len(t), len(e['a']))
        self.assertEqual(len(strp(t)), len(strp(e['a'])))
        self.assertIn(e['gender'], ['M', 'F', None])
