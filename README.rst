Data-migrator is a simple data-migration package for python lovers.


.. image:: https://img.shields.io/pypi/pyversions/data-migrator.svg
    :target: https://pypi.python.org/pypi/data-migrator

.. image:: https://circleci.com/gh/schubergphilis/data-migrator.svg?style=svg
    :target: https://circleci.com/gh/schubergphilis/data-migrator

----

.. image:: https://pyup.io/repos/github/schubergphilis/data-migrator/shield.svg
     :target: https://pyup.io/repos/github/schubergphilis/data-migrator/
     :alt: Updates

.. image:: https://readthedocs.org/projects/data-migrator/badge/?version=latest
    :target: http://data-migrator.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://api.codacy.com/project/badge/Grade/bf6030e9e7e248979607802880336611
    :target: https://www.codacy.com/app/schubergphilis/data-migrator?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=schubergphilis/data-migrator&amp;utm_campaign=Badge_Grade

.. image:: https://api.codacy.com/project/badge/Coverage/bf6030e9e7e248979607802880336611
    :target: https://www.codacy.com/app/schubergphilis/data-migrator?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=schubergphilis/data-migrator&amp;utm_campaign=Badge_Coverage

.. image:: https://badge.fury.io/py/data-migrator.svg
    :target: https://badge.fury.io/py/data-migrator


Data-migrator is a declarative DSL for table driven data transformations, set up as
an open and extensive system. Use this to create data transformations for
changing databases as a result of changing code, initial loads to datalakes
(it contains a Kinesis provider)and more.

Example
-------

Data-migrator assumes data is extracted and loaded with client access.

.. code-block:: bash

	$ mysql source_db -E 'select id,a,b from table' -B  | python my_filter.py | mysql target_db

It than offers a wide range of primitives with default settings to build complex transformations
fast, readable and extendable

.. code-block:: python

  from data_migrator import models, transform

  class Result(models.Model):
    id   = models.IntField(pos=0) # keep id
    uuid = models.UUIDField()     # generate new uuid4 field
    a    = models.StringField(pos=1, default='NO_NULL', max_length=5, nullable='NULL', replacement=lambda x:x.upper())
    b    = models.StringField(pos=2, name='my_b')

  if __name__ == "__main__":
    transform.Transformer(models=[Result]).process()

Installation
------------

Execute the following command to install *data-migrator* with ``pip``::

    pip install data-migrator

See the `Installation Instructions
<http://data-migrator.readthedocs.io/en/latest/install.html>`_ in Documentation for
more instructions on installing, upgrading, and uninstalling *data-migrator*.

The project is `maintained at GitHub <https://github.com/schubergphilis/data-migrator>`_.

Support and contribute
----------------------
Questions, comments, bug reports and especially tested patches may be
submitted directly to the `issue tracker
<https://github.com/schubergphilis/data-migrator/issues>`_.

Everyone interacting with this codebase, issue trackers,
chat rooms, and mailing lists is expected to follow the
`Code of Conduct <http://data-migrator.readthedocs.io/en/latest/code-of-conduct.html>`_.
