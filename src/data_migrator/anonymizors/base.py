#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class BaseAnonymizor(object):
    '''BaseType for anonymizers of the *data-migrator*.

    Instantiate the anonymizer and definition and call the instantiation at
    translation time.

    Implement the :meth:`~.__call__` method to implement your specific anonymizor.

    '''

    def __call__(self, v):
        '''output the anonymized object.

        Args:
            v: object to anonymize
        Returns:
            anonymized value
        '''
        raise NotImplementedError
