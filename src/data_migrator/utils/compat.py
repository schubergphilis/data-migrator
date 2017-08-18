#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""helper functions for py2 -> p3 compat"""

import random
import bisect as _bisect
from functools import reduce


def isstr(s):
    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)


def choices(population, weights=None, cum_weights=None, k=1):
    """Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.

    This is a clone of Python 3 random.choices. Took our own accumulate
    function for the cum_weights

    see https://github.com/python/cpython/blob/master/Lib/random.py
    """
    if cum_weights is None:
        if weights is None:
            _int = int
            total = len(population)
            return [population[_int(random.random() * total)] for i in range(k)]
        cum_weights = reduce(lambda c, x: c + [c[-1] + x],weights, [0])[1:]
    elif weights is not None:
        raise TypeError('Cannot specify both weights and cumulative weights')
    if len(cum_weights) != len(population):
        raise ValueError('The number of weights does not match the population')
    bisect = _bisect.bisect
    total = cum_weights[-1]
    return [population[bisect(cum_weights, random.random() * total)] for i in range(k)]
