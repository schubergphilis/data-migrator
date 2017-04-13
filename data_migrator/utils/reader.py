import sys
import csv

from data_migrator.exceptions import DefinitionException, DataException

def default_reader(infile='<stdin>', skip_headers=False, delimiter='\t'):
    '''default csv reader'''
    if infile == '<stdin>':
        infile = sys.stdin
    else:
        infile = open(infile)
    reader = csv.reader(infile, delimiter=delimiter)
    headers = next(reader, []) if not skip_headers else []
    return reader, headers
