from setuptools import find_packages
from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pymt5adapter',
    version='0.1.0',
    description='A drop in replacement/wrapper for the MetaTrader5 package with type hinting and pythonic interfaces',
    long_description=readme,
    author='nicholishen',
    author_email='nicholishen@tutanota.com',
    url='https://github.com/nicholishen/pymt5adapter',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
