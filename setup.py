from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup
setup(name='PyMos',
      description='Python Mosaic Generator',
      author='Abhishek Mishra (ideamonk), Yuvi (yuvipanda)',
      author_email='ideamonk@gmail.com, me@yuvi.in',
      version='0.5',
      packages=['pymos'],
      scripts=['bin/pymos'],
      install_requires=['PIL', 'argparse']
      )
