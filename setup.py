#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stock-selector',
    version='0.1.0',
    description='Stock selection tool using fundamental and technical analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/stock-selector',
    author='Your Name',
    author_email='your.email@example.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    packages=find_packages(exclude=['tests', 'docs', 'examples']),
    install_requires=[
        'yfinance>=0.2.0',
        'pandas>=1.3.0',
        'numpy>=1.16.5',
        'requests>=2.31.0',
        'ta>=0.10.0',
        'scikit-learn>=1.0.0',
        'textblob>=0.17.0',
        'vaderSentiment>=3.3.2',
        'beautifulsoup4>=4.11.1',
        'lxml>=4.9.0',
        'python-dateutil>=2.8.0',
        'pytz>=2022.5',
    ],
    python_requires='>=3.9',
)
