import sys
import os
import logging

from data_migrator.exceptions import DataException, ValidationException
from data_migrator.utils import configure_logging
from data_migrator.utils import configure_parser, default_reader
from data_migrator.utils import get_version
from data_migrator.emitters import MySQLEmitter

class Transformer(object):
    '''Main transformation engine'''
    def __init__(self, models=[], reader=None, argparser=None, outdir=None, emitter=MySQLEmitter):
        self.outdir = outdir
        self.models = models
        self.emitter = emitter
        self.print_rows=0
        self.argparser = argparser
        self.reader = reader
        self.max_pos = max([x._meta.max_pos for x in models])

    def process(self):
        self.log = configure_logging()
        self.args = self.argparser or configure_parser()
        self._interpret_cmdline()
        self.log.info("data_migrator pipeline starting")
        self.log.info("version: %s", get_version())
        self._open_input()
        self._read_input()
        self._write_output()
        self.log.info("data_migrator pipeline done")

    def _interpret_cmdline(self):
        self.outdir = self.outdir or self.args.outdir
        if self.args.debug:
            self.log.setLevel(logging.DEBUG)
            self.print_rows = self.args.rows
        if self.args.quiet:
            self.log.setLevel(logging.CRITICAL)

    def _open_input(self):
        if self.reader:
            self.reader, self.in_headers = self.reader(self.args)
        else:
            self.log.debug("reading from %s", self.args.input)
            self.reader, self.in_headers = default_reader(infile=self.args.input)
        if len(self.in_headers) <= self.max_pos:
            raise DataException('Data in has %d columns, too little for max position %d', len(self.in_headers), self.max_pos)
        self.log.debug("csv has %d columns", len(self.in_headers))

    def _read_input(self):
        self.rows = 0
        self.log.info("models: %s" % ", ".join([x._meta.model_name for x in self.models]))
        for x in self.models:
            if x.objects.unique_values:
                self.log.info("%s: unique columns [%s]", x._meta.model_name, ",".join([x for x in x.objects.unique_values]))
        if self.print_rows:
            self.log.debug("printing first %d rows of input", self.print_rows)
        for row in self.reader:
            if self.print_rows > 0:
                self.log.debug("%d: %s" % (self.print_rows, ",".join(row)))
                self.print_rows -= 1
            self.rows += 1
            res = []
            for o in self.models:
                res.append(o.objects.scan_row(row=row, previous=res))
        self.log.debug("headers of input: %s" % ",".join(self.in_headers))

    def _write_output(self):
        for m in self.models:
            _emitter = (getattr(m._meta, 'emitter', self.emitter) or self.emitter)(manager=m.objects)
            f = self._filehandle(_emitter)
            self.log.debug('%s: stats %s' % (m._meta.model_name, ", ".join(["%s=%d" % (k,v) for k,v in m.objects.stats().items()])))
            for l in _emitter.preamble(headers=self.in_headers):
                f.write(l + '\n')
            lineno=0
            for l in m.objects.all():
                try:
                    _out = _emitter.emit(l)
                    for x in _out:
                        f.write(x+'\n')
                except AssertionError as err:
                    raise ValidationException("object: %d, %s" % (lineno, err))
                lineno += 1
            if f != sys.stdout:
                f.close()
            self.log.info("%s: %d records emitted", m._meta.model_name, len(m.objects))

    def _filehandle(self, e):
        if self.outdir:
            _filename = e.filename()
            _filename = os.path.normpath(self.outdir + "/" + _filename)
            self.log.debug('%s: opening %r' % (e.meta.model_name, _filename))
            f = open(_filename, "w")
        else:
            self.log.debug('%s: writing to stdout' % (m._meta.model_name))
            f = sys.stdout
        return f
