from data_migrator.utils import get_version

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='data-migrator',
    version=get_version(),
    description='Django-esc data migration and transformation package',
    long_description=long_description,
    license='MIT',
    author='Ilja Heitlager',
    author_email='iheitlager@schubergphilis.com',
    packages=['data_migrator','test','data_migrator.utils','data_migrator.models','data_migrator.emitters','data_migrator.contrib'],
)
