# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import find_packages
from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pymt5adapter',
    version='0.1.0',
    description='A drop in replacmenet for MetaTrader5 with type hinting and pythonic interfaces',
    long_description=readme,
    author='nicholishen',
    author_email='nicholishen@tutanota.com',
    url='https://github.com/kennethreitz/samplemod',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
