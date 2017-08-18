#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

from data_migrator.anonymizors.base import BaseAnonymizor
from data_migrator.utils.compat import choices as _choices

class ChoiceAnonymizor(BaseAnonymizor):
    '''ChoiceAnonymizor returns some choices with optional probabilities

        >>> ChoiceAnonymizor(['M', 'F', None], weights=[0.3, 0.3, 0.4])()
        'M'

    Attributes:
        choices (list): list of choices to select from
        weights (list): optional list of weights
    '''

    def __init__(self, choices, weights=None):
        self.choices = choices
        self.weights = weights

    def __call__(self, v):
        return _choices(self.choices, self.weights)[0]


class Alpha3Anonymizor(BaseAnonymizor):
    '''Alpha3Anonymizor returns a Country code in alpha3

        >>> Alpha3Anonymizor()()
        'NLD'

    '''

    def __init__(self):
        self.choices = ['NLD', 'DEU', 'USA', 'BRA']

    def __call__(self, v):
        return random.choice(self.choices)
