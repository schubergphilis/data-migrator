#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from data_migrator.emitters.base import BaseEmitter
from data_migrator.emitters import MySQLEmitter, CSVEmitter
from data_migrator.models import Model, StringField

class EmitterModel(Model):
    a = StringField(pos=0)
    b = StringField(pos=1)

o1 = EmitterModel(a="hello", b="world").save()
o2 = EmitterModel(a="goodbye", b="cruel world").save()

class EmitterHeaderModel(Model):
    b = StringField(pos=1)
    a = StringField(pos=0)

    class Meta:
        prefix = ["hello", "world"]
        table_name = 'test'

class TestEmitterBase(unittest.TestCase):
    def test_base_default(self):
        '''Base Emitter defaults'''
        b = BaseEmitter(manager=EmitterModel.objects)
        self.assertEqual(b.filename(), "emittermodel.txt")

    def test_base_fileext(self):
        '''Base Emitter defaults'''
        b = BaseEmitter(manager=EmitterModel.objects, extension='.sql')
        self.assertEqual(b.filename(), "emittermodel.sql")

    def test_base_fileext_dot(self):
        '''Base Emitter defaults'''
        b = BaseEmitter(manager=EmitterModel.objects, extension='sql')
        self.assertEqual(b.filename(), "emittermodel.sql")

class MySQLEmitterBase(unittest.TestCase):
    def test_start(self):
        e = MySQLEmitter(manager=EmitterModel.objects)
        self.assertEqual(len(EmitterModel.objects), 2)
        self.assertGreater(len(e.preamble(headers=['hello'])), 0)

    def test_header(self):
        e = MySQLEmitter(manager=EmitterHeaderModel.objects)
        h = e.preamble(["first line"])
        self.assertIn("hello", h)
        self.assertIn("world", h)

    def test_emit(self):
        e = MySQLEmitter(manager=EmitterHeaderModel.objects)
        o = EmitterModel.objects.all()
        self.assertEqual(e.emit(o[0]), ['INSERT INTO `test` (`b`, `a`) VALUES ("world", "hello");'])
        self.assertEqual(e.emit(o[1]), ['INSERT INTO `test` (`b`, `a`) VALUES ("cruel world", "goodbye");'])

class CSVEmitterBase(unittest.TestCase):

    def test_header(self):
        e = CSVEmitter(manager=EmitterHeaderModel.objects)
        h = e.preamble()
        self.assertIn('b, a', h)

    def test_emit(self):
        e = CSVEmitter(manager=EmitterHeaderModel.objects)
        o = EmitterModel.objects.all()
        self.assertEqual(e.emit(o[0]), ['"world", "hello"'])
        self.assertEqual(e.emit(o[1]), ['"cruel world", "goodbye"'])

if __name__ == '__main__':
    unittest.main()
