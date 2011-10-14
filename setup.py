#!/usr/bin/env python
# -*- coding: utf-8 -*-

from platform import python_version
from setuptools import setup, find_packages

major, minor, micro = python_version().split('.')

if major != '2' or minor not in ['6', '7']:
    raise Exception('unsupported version of python')

requires = [
    'python >= 2.6',
]

setup(
    name='cortex-client',
    description='cortex command line client',
    author='Laurent Eschenauer',
    author_email='laurent.eschenauer@gmail.com',
    url='https://github.com/guardis/cortex-client',
    license='',
    packages=find_packages(),
    scripts=[
        'cortex-client'
    ],
    include_package_data=True,
    # Here's the list of usable classifiers:
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: POSIX',
        'Topic :: Content Management',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
    ],
    install_requires=requires,
)
