#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name='data-migrator',
    version="0.6.1",
    description='declarative data migration and transformation package',
    long_description=long_description,
    license='MIT',
    author='Ilja Heitlager',
    author_email='iheitlager@schubergphilis.com',
    maintainer='Ilja Heitlager',
    maintainer_email='iheitlager@schubergphilis.com',
    keywords=["datamigration", "development-tools"],
    url='https://github.com/schubergphilis/data-migrator',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    test_suite="tests",
    platforms=["any"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Database",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English"
    ],
    install_requires=[
        'six',
        'boto',
    ],
    zip_safe=True,
)
