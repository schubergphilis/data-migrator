#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Emitters are used to export models to output format.

This module contains all classes for emitters: base and actuals. Currently
the system has two emitters: :class:`~.CSVEmitter` and :class:`~.MySQLEmitter`
implemented, of which the last is the default emitter. An emitter provides the
export format for the scanned and cleaned datasets. It also provides preambles
and postambles in the output files, for example to clean the target table
before loading it.

The following classes are defined in this module:

* :class:`~.BaseEmitter`
* :class:`~.MySQLEmitter`
* :class:`~.CSVEmitter`

The basic structure for emitting is a combination between
:class:`~.BaseManager` and :class:`~.BaseEmitter`:

.. code-block:: python

  e = Emitter(manager=Model.objects)
  print e.preamble(header=[..my header lines to add..])
  for l in Model.objects.all():
    print e.emit(l)  # emit is returning a list of strings!

.. note::

    At this moment *data-migrator* does not an actively take part in schema
    migrations of any sort. It is purely about cleaning, anonymizing and
    transforming data (yet!).
"""


from .mysql import MySQLEmitter # noqa
from .csv import CSVEmitter # noqa
from .singer import SingerEmitter # noqa
