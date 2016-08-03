#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='ref-resolver',
      version='1.0.2',
      description='A lightweight python json schema ref resolver and inliner.',
      author='Purush Swaminathan',
      author_email='purukaushik@asu.edu',
      license='MPL 2.0',
      url='https://github.com/purukaushik/ref-resolver',
      download_url='https://github.com/purukaushik/ref-resolver.git',
      packages=find_packages(),
      install_requires=['simplejson', 'jsonpath_rw']
     )
