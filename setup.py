#!/usr/bin/env python

from distutils.core import setup

with open('VERSION', 'r') as i:
    version = i.read().strip()

setup(name='PyCobalt',
      version=version,
      description='Coreference Resolution',
      author='Bernhard Bermeitinger',
      packages=[
          'pycobalt',
          'pycobalt.classifier',
          'pycobalt.constant_types',
          'pycobalt.language',
          'pycobalt.references'
      ],
)
