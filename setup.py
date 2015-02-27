#!/usr/bin/env python

from distutils.core import setup

import djbraintree

setup(name='Django Braintree',
      version='0.0.1',
      description='Django + Braintree',
      author='Benjamin Rosnick',
      author_email='benrxv@gmail.com',
      url='https://github.com/benrxv/django-braintree',
      packages=['djbraintree',],
     )
