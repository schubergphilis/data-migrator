from data_migrator.utils import get_version, get_development_status

from setuptools import setup, find_packages

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name='data-migrator',
    version=get_version(),
    description='Django-esc data migration and transformation package',
    long_description=long_description,
    license='MIT',
    author='Ilja Heitlager',
    author_email='iheitlager@schubergphilis.com',
    maintainer='Ilja Heitlager',
    maintainer_email='iheitlager@schubergphilis.com',
    keywords = "datamigration development-tools",
    url='https://github.com/schubergphilis/data-migrator',
    packages=find_packages(exclude=['test_*']),
    classifiers = [
        get_development_status(),
        "Environment :: Console",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Database",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English"
    ]
)
