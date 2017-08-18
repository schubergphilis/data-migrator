#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Anonymizers are used to anonymize data while outputting.

This module contains all classes for anonymizers:

* :class:`data_migrator.anonymizors.base.BaseAnonymizer`
* :class:`~.SimpleStringAnonymizor`
* :class:`~.TextAnonymizor`
* :class:`~.ChoiceAnonymizor`

"""


from .strings import SimpleStringAnonymizor # noqa
from .strings import TextAnonymizor # noqa
from .lists import ChoiceAnonymizor # noqa
