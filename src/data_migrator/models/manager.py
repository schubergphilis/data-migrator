#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from data_migrator.exceptions import NonUniqueDataException
from data_migrator.exceptions import ValidationException
from data_migrator.utils import default_logger

log = default_logger()


class BaseManager(object):
    """
    BaseManager is the foundation for all managers, contains to base logic to
    maintain models: parse, keep and emit.

    Extend this class for actual managers
    """
    def __init__(self, *args, **kwargs):
        self.model_class = None  # holding the class of the Model to manager
        self.results = []
        self.unique_values = {}
        self.rows = 0
        self.dropped = 0

    def _prepare(self, cls):
        self.model_class = cls
        self.meta = cls._meta

        # define indexes for fields that are expected to be unique
        for u in self.meta.unique_fields:
            self.unique_values[u] = set()

    def transform(self, row, previous, model):
        '''defines the instantiation of objects from a row

        Override this function in your own manager. Models are ordered and
        generated records are offered in the consequtives managers too.

        Args:
            row (list): all input data for a new row
            previous (list): all generated objects from previous managers
                in chain
            model (Model): Model this manager is linked to

        Returns:
            list of all generated objects
        '''
        raise NotImplementedError

    def scan_rows(self, rows):
        '''scan many rows'''
        for row in rows:
            self.scan_row(row)

    def scan_row(self, row, previous=None):
        '''scan one row and save to list

        Args:
            row: current row to scan
            previous (list): list of list of previous objects in this scan

        Returns:
            list of saved objects
        '''
        self.rows += 1
        try:
            res = self.transform(row, previous, self.model_class)
        except ValidationException as err:
            if self.meta.fail_not_validated:
                raise ValidationException("%d, %s:%s" % (self.rows, self.meta.model_name, err))
            log.debug("%d, %s: dropped, %s", self.rows, self.meta.model_name, err)
            self.dropped += 1
            return []
        else:
            return self.save(res)

    def save(self, o):
        '''save object(s) to this list'''
        res = []
        if not isinstance(o, list):
            o = [o]
        for e in o:
            if self._save_object(e):
                res.append(e)
        return res

    def _save_object(self, o):
        v = self._check_none(o)
        if v:
            self.dropped += 1
            log.debug('%d, %s: drop None in field(s): %s', self.rows, self.meta.model_name, ",".join(v))
            return
        v = self._check_unique(o)
        if v and self.meta.fail_non_unique:
            raise NonUniqueDataException('columns %s' % ",".join(v))
        elif v and self.meta.drop_non_unique:
            self.dropped += 1
            log.debug('%d, %s: drop uniqueness violation', self.rows, self.meta.model_name)
        else:
            self.results.append(o)
            return o

    def _check_none(self, o):
        violation = []
        for f in self.meta.drop_if_none:
            if getattr(o, f) is None:
                violation.append(f)
        return violation

    def _check_unique(self, o):
        violation = []
        for k, s in self.unique_values.items():
            v = getattr(o, k)
            if v in s:
                log.debug('%s: non unique value %s=%s', self.meta.model_name, k, v)
                violation.append(k)
            s.add(v)
        return violation

    def all(self):
        '''return all results'''
        return self.results

    def __len__(self):
        '''return length of current result set'''
        return len(self.results)

    def stats(self):
        '''return current stats'''
        return {
            "out": len(self.results),
            "in": self.rows,
            "dropped": self.dropped,
        }


class SimpleManager(BaseManager):
    """
    The default manager to handle models, all standard logic and generates one
    object per row
    """
    def transform(self, row, previous, model):
        '''specific transform implementation, instantiates one object
        from a row
        '''
        res = [model().scan(row)]
        return res
