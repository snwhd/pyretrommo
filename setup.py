#!/usr/bin/env python3
from setuptools import (
    find_packages,
    setup,
)


setup(
    name='pyretrommo',
    version='0.0.1',
    author='snwhd',
    url='https://github.com/snwhd/pyretrommo',
    packages=find_packages(),
    install_requires=[
        'requests==2.26.0',
        'beautifulsoup4==4.10.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
    ],
)
