#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import csv
import logging

from data_migrator import __version__
from data_migrator.exceptions import DataException, ValidationException
from data_migrator.utils import configure_logging
from data_migrator.utils import configure_parser
from data_migrator.emitters import MySQLEmitter


class Transformer(object):
    '''Main transformation engine

    Use this class as your main entry to build your Transformer

        >>> if __name__ == "__main__":
        >>>    t = transform.Transformer(models=[Model])
        >>>    t.process()

    '''
    def __init__(self, models=None, reader=None, dataset=None,
                 argparser=None, outdir=None,
                 emitter=MySQLEmitter):
        '''
        Args:
            models (list): list of all models to be processed in this
                transformer
            reader: reference to and external reader if not default
            dataset: a tablib dataset to read from
            argparse: reference to another argument parser if not
                default_parser
            outdir: output directory for results, otherwise scan from argparser
            emitter: emitter to be used for this transformation

        Note that the order of models is relevant for the generation
        '''

        self.outdir = outdir
        self.models = models or []
        self.emitter = emitter
        self.dataset = dataset
        self.print_rows = 0
        self.argparser = argparser
        self.reader = reader
        self.max_pos = max([x._meta.max_pos for x in models])

    def process(self):
        '''Main processing loop'''
        self.log = configure_logging()
        self.parser = self.argparser or configure_parser()
        self._specific_args()
        self._interpret_cmdline()
        self.log.info("data_migrator pipeline starting")
        self.log.debug("version: %s", __version__)
        self._get_header()
        self._open_input()
        self._read_input()
        self._write_output()
        self.log.info("data_migrator pipeline done")

    def _specific_args(self):
        pass

    def _interpret_cmdline(self):
        self.args = self.parser.parse_args(sys.argv[1:])
        self.outdir = self.outdir or self.args.outdir
        if self.args.debug:
            self.log.setLevel(logging.DEBUG)
            self.print_rows = self.args.rows
        if self.args.quiet:
            self.log.setLevel(logging.CRITICAL)
        if self.dataset:
            self.log.debug("reading from dataset")
            self.reader = self.dataset
        elif self.reader:
            self.log.debug("reading from external reader")
            self.reader = self.reader(self.args)
        elif self.args.input == '<stdin>':
            self.log.debug("reading from <stdin>")
            self.reader = csv.reader(sys.stdin, delimiter='\t')
        else:
            self.log.debug("reading from file: %s", self.args.input)
            self.reader = csv.reader(open(self.args.input), delimiter='\t')


    def _get_header(self):
        try:
            self.in_headers = self.reader.headers
        except AttributeError:
            self.in_headers = next(self.reader, [])

    def _open_input(self):
        if len(self.in_headers) <= self.max_pos:
            raise DataException(
                'Data in has %d columns, too little for max position %d',
                len(self.in_headers), self.max_pos
            )
        self.log.debug("input has %d columns", len(self.in_headers))

    def _read_input(self):
        self.rows = 0
        self.log.info(
            "models: %s", ", ".join([x._meta.model_name for x in self.models])
        )
        for x in self.models:
            if x.objects.unique_values:
                self.log.info(
                    "%s: unique columns [%s]",
                    x._meta.model_name,
                    ",".join([x for x in x.objects.unique_values])
                )
        if self.print_rows:
            self.log.debug("printing first %d rows of input", self.print_rows)
        for row in self.reader:
            if self.print_rows > 0:
                self.log.debug("%d: %s", self.print_rows, row)
                self.print_rows -= 1
            self.rows += 1
            res = []
            for o in self.models:
                try:
                    scanned = o.objects.scan_row(row=row, previous=res)
                    res.append(scanned)
                except DataException:
                    if o._meta.fail_on_data_exception:
                        self.critical("Error in data[%d]: %s", self.rows, row)
                        sys.exit(1)
                    self.log.warning("Error in data[%d]: %s", self.rows, row)
                except:  #pylint: disable=W0702
                    self.log.critical("Uncaught exception in data: %s", row)
                    sys.exit(1)
        self.log.debug("headers of input: %s", ",".join(self.in_headers))

    def _write_output(self):
        for m in self.models:
            _emitter = (
                getattr(m._meta, 'emitter', self.emitter) or
                self.emitter
            )(manager=m.objects)
            f, file_name = self._filehandle(_emitter)
            self.log.debug(
                '%s: stats %s', m._meta.model_name, ", ".join(
                    ["%s=%d" % (k, v) for k, v in m.objects.stats().items()]
                )
            )
            for l in _emitter.preamble(headers=self.in_headers):
                f.write(l + '\n')
            lineno = 0
            for l in m.objects.all():
                try:
                    _out = _emitter.emit(l)
                    for x in _out:
                        f.write(x+'\n')
                except AssertionError as err:
                    raise ValidationException("object: %d, %s" % (lineno, err))
                lineno += 1
            for l in _emitter.postamble():
                f.write(l + '\n')
            if f != sys.stdout:
                self.log.info("Closing file %s", file_name)
                f.close()
            self.log.info(
                "%s: %d records emitted",
                m._meta.model_name, len(m.objects)
            )

    def _filehandle(self, e):
        if self.outdir:
            _filename = e.filename()
            _filename = os.path.normpath(self.outdir + "/" + _filename)
            self.log.debug('%s: opening %r', e.meta.model_name, _filename)
            f = open(_filename, "w")
        else:
            self.log.debug('%s: writing to stdout', e._meta.model_name)
            f = sys.stdout
        return f, _filename
