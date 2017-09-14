#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import csv
import logging
import boto3
import time

from data_migrator import __version__
from data_migrator.exceptions import DataException, ValidationException
from data_migrator.exceptions import DefinitionException
from data_migrator.utils import configure_logging
from data_migrator.utils import configure_parser
from data_migrator.emitters import JSONEmitter


class KinesisTransformer(object):
    '''Main transformation engine for Kinesis Pipelines

    Use this class as your main entry to build your Transformer

        >>> if __name__ == "__main__":
        >>>    t = KinesisTransformer(models=[Model])
        >>>    t.process()

    '''
    def __init__(self, models=None, reader=None, argparser=None,
                 outdir=None,
                 stream_name=None, profile_name=None,
                 emitter=JSONEmitter):
        '''
        Args:
            models (list): list of all models to be processed in this
                transformer
            reader: reference to and external reader if not default
            argparse: reference to another argument parser if not
                default_parser
            outdir: output directory for results, otherwise scan from argparser
            stream_name: Kinesis name to send the stream to
            profile_name: AWS profile
            emitter: emitter to be used for this transformation

        Note that the order of models is relevant for the generation
        '''

        self.models = models or []
        self.emitter = emitter
        self.stream_name = stream_name
        self.profile_name = profile_name
        self.print_rows = 0
        self.argparser = argparser
        self.reader = reader
        self.outdir = outdir
        self.trial_run = False
        self.max_pos = max([x._meta.max_pos for x in models])

    def process(self):
        '''Main processing loop'''
        self.log = configure_logging()
        self.parser = self.argparser or configure_parser()
        self._specific_args()
        self._interpret_cmdline()
        self.log.info("data_migrator pipeline starting")
        self.log.debug("version: %s", __version__)
        self._open_input()
        self._read_input()
        self._write_output()
        self.log.info("data_migrator pipeline done")

    def _specific_args(self):
        self.parser.add_argument('-t', '--trial', action='store_true',
            help='trial run only, no actual upload to Kinesis')
        self.parser.add_argument('--stream',
            help='name of the stream')
        self.parser.add_argument('--profile',
            help='name of the profile')

    def _interpret_cmdline(self):
        self.args = self.parser.parse_args(sys.argv[1:])
        if self.args.debug:
            self.log.setLevel(logging.DEBUG)
            self.print_rows = self.args.rows
        if self.args.trial:
            self.trial_run = True
        if self.args.quiet:
            self.log.setLevel(logging.CRITICAL)

        self.outdir = self.outdir or self.args.outdir

        if self.args.stream:
            self.stream_name = self.args.stream
        if self.args.profile:
            self.profile_name = self.args.profile

        if self.reader:
            self.log.debug("reading from external reader")
            self.reader = self.reader(self.args)
        elif self.args.input == '<stdin>':
            self.log.debug("reading from <stdin>")
            self.reader = csv.reader(sys.stdin, delimiter='\t')
        else:
            self.log.debug("reading from file: %s", self.args.input)
            self.reader = csv.reader(open(self.args.input), delimiter='\t')

        if not self.stream_name:
            raise DefinitionException("Please set the stream_name")
        if not self.profile_name:
            raise DefinitionException("Please set the profile_name")
        self.log.debug("Default profile and stream: %s - %s", self.profile_name, self.stream_name)



    def _open_input(self):
        self.in_headers = next(self.reader, [])
        if len(self.in_headers) <= self.max_pos:
            raise DataException(
                'Data in has %d columns, too little for max position %d',
                len(self.in_headers), self.max_pos
            )
        self.log.debug("csv has %d columns", len(self.in_headers))

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
                self.log.debug("%d: %s", self.print_rows, ",".join(row))
                self.print_rows -= 1
            self.rows += 1
            res = []
            for o in self.models:
                res.append(o.objects.scan_row(row=row, previous=res))
        self.log.debug("headers of input: %s", ",".join(self.in_headers))

    def _write_output(self):
        for m in self.models:
            _emitter = (
                getattr(m._meta, 'emitter', self.emitter) or
                self.emitter
            )(manager=m.objects)

            f, file_name = self._filehandle(_emitter)
            stream_name = self._stream_client(_emitter)

            self.log.debug(
                '%s: stats %s', m._meta.model_name, ", ".join(
                    ["%s=%d" % (k, v) for k, v in m.objects.stats().items()]
                )
            )
            lineno = 0
            batch = []
            for l in m.objects.all():
                try:
                    _out = _emitter.emit(l)
                    for x in _out:
                        if f:
                            f.write(x + '\n')
                        batch += [{
                            'Data': str.encode(x),
                            'PartitionKey': 'string',
                        }]
                except AssertionError as err:
                    raise ValidationException("object: %d, %s" % (lineno, err))
                lineno += 1
                if lineno % 500 == 0:
                    self.log.debug("Sending batch: %d to %s", lineno, stream_name)
                    self._put_records(batch, stream_name)
                    batch = []
            if batch:
                    self.log.debug("Sending batch: %d to %s", lineno, stream_name)
                    self._put_records(batch, stream_name)
            if f:
                self.log.info("Closing file %s", file_name)
                f.close()
            self.log.info(
                "%s: %d records emitted",
                m._meta.model_name, len(m.objects)
            )

    def _put_records(self, batch, stream):
        if self.trial_run:
            self.log.info("TRIAL: put_records: %d to %s", len(batch), stream)
            return

        success = False
        retry = 10
        while not success and retry > 0:
            retry -= 1
            response = self.client.put_records(Records=batch, StreamName=stream)
            if response['FailedRecordCount'] != 0:
                batch = batch[len(batch)-response['FailedRecordCount']:]
                self.log.warning("Failed records %d, waiting and resending: %d", response['FailedRecordCount'], len(batch))
                ## We hit a upload limit so wait a while
                time.sleep(1)
            else:
                success = True
        if not retry:
            self.log.error("Too many retries, stopping")
            sys.exit(1)

    def _stream_client(self, e):
        session = boto3.Session(profile_name=self.profile_name)
        self.client = session.client('kinesis')
        return self.stream_name

    def _filehandle(self, e):
        f = None
        if self.outdir:
            _filename = e.filename()
            _filename = os.path.normpath(self.outdir + "/" + _filename)
            self.log.debug('%s: opening %r', e.meta.model_name, _filename)
            f = open(_filename, "w")
        return f, _filename
