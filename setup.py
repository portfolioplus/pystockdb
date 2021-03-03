#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockdb

  Copyright 2019 Slash Gordon

  Use of this source code is governed by an MIT-style license that
  can be found in the LICENSE file.
"""
from setuptools import setup, find_packages
import re

EXCLUDE_FROM_PACKAGES = ['test', 'test.*', 'test*']
VERSION = '0.0.0'

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = (
    [
        'pytickersymbols>=1.1.8',
        'pandas==1.2.3',
        'yfinance>=0.1.52',
        'uplink>=0.9.0',
        'pony==0.7.14'
    ]
)
with open('src/pystockdb/__init__.py', 'r') as fd:
    VERSION = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

setup(
    name="pystockdb",
    version=VERSION,
    author="Slash Gordon",
    author_email="slash.gordon.dev@gmail.com",
    package_dir={'': 'src'},
    description="Simple stock db with tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/portfolioplus/pystockdb",
    install_requires=INSTALL_REQUIRES,
    packages=find_packages('src', exclude=EXCLUDE_FROM_PACKAGES),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
)
