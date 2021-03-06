#!/usr/bin/env python3

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Read version info from yyyymmdd/version.py
version_vars = {}
with open("yyyymmdd/version.py") as fp:
    exec(fp.read(), version_vars)
version_string = version_vars['__version_string__']

setup(
    name='yyyymmdd',
    version=version_string,

    description='Convenient Date and DateRange classes.',
    long_description=long_description,
    url='https://github.com/shx2/yyyymmdd',
    author='shx2',
    author_email='shx222@gmail.com',
    license='MIT',

    packages=find_packages(exclude=['tests*']),
    platforms = ["POSIX", "Windows"],
    install_requires=[],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
    ],
    keywords='date datetime range',
)
