#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
from setuptools import setup, find_packages

## See the following pages for keywords possibilities for setup keywords, etc.
# https://packaging.python.org/
# https://docs.python.org/3/distutils/apiref.html
# https://docs.python.org/3/distutils/setupscript.html

setup(name='series-poc',
      version='0.1.0',
      package_dir={'': 'src'},
      packages=find_packages(where='src'),
      description='harmonised series proof-of-concept',
      install_requires=['tornado', 'dbc-pyutils', 'dbc-data'],
      entry_points={'console_scripts': ['series-service=series_poc.service:cli']},
      test_suite='series_poc.tests',
      provides=['series_poc'],
      maintainer="ai",
      maintainer_email="ai@dbc.dk",
      zip_safe=False)
