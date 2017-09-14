#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse

_PARSER = None


def default_parser():
    return _PARSER


def configure_parser(args=None, description=None):
    global _PARSER
    if not _PARSER:
        description = description or 'Basic Transformer parser'
        _PARSER = argparse.ArgumentParser(description=description)

    _PARSER.add_argument('-o', '--outdir', default='results',
            help='output directory')
    _PARSER.add_argument('-i', '--input', default='<stdin>',
            help='input file')
    _PARSER.add_argument('--debug', action='store_true',
            help='enter debug mode')
    _PARSER.add_argument('-q', '--quiet', action='store_true',
            help='quiet mode, no output')
    _PARSER.add_argument('-p', '--rows', default=0, type=int,
            help='input rows to print')
    return _PARSER
