from setuptools import find_packages
from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pymt5adapter',
    version='0.4.1',
    description='A drop in replacement wrapper for the MetaTrader5 package',
    long_description_content_type='text/markdown',
    long_description=readme,
    author='nicholishen',
    author_email='nicholishen@tutanota.com',
    url='https://github.com/nicholishen/pymt5adapter',
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['MetaTrader5==5.0.33', 'ujson'],
    python_requires='>=3.6',
)
