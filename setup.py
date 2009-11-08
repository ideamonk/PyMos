# -*- coding: utf-8 -*-
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup
setup(name='PyMos',
      description='Python Mosaic Generator',
      author='Abhishek Mishra (ideamonk), Yuvi (yuvipanda)',
      author_email='ideamonk@gmail.com, me@yuvi.in',
      version='0.6',
      packages=['pymos'],
      scripts=['bin/pymos'],
      install_requires=['argparse'],
      license = "BSD",
      # Thats how Apple was able to take OpenBSD, make Mac OS X :)
      # http://bheekly.blogspot.com/2007/08/what-is-free.html
      keywords = "mosaic imaging graphics poster"
      )
