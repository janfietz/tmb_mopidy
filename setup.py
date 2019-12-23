#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
    'nfccardreader')))

from pirc522 import __version__  # flake8: noqa
sys.path.pop(0)

setup(
    name='nfccardreader',
    packages=find_packages(),
    include_package_data=True,
    version=__version__,
    description='Raspberry Pi Python library for to read NFC tags with RFID RC522 module.',
    long_description='Raspberry Pi Python library for SPI RFID RC522 module.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    author='janfietz',
    author_email='janfietz@gmail.com',
    license='MIT',
    install_requires=['spidev', 'RPi.GPIO', 'pi-rc522'],
)