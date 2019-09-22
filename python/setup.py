# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Djoro regulation server',
    'author': 'Ivan Frain / Lior Perez',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'ifn@thermlabs.com',
    'version': '0.1',
    'install_requires': [
        'nose',
        'pymongo >= 2.4.1',
        'flask-restful >= 0.2.12',
        'goose-extractor >= 1.0.12',
        'BeautifulSoup',
        'html2text'
    ],
    'packages': [
        'djoro_regulation_server',
        'djoro_regulation_server.controllers'],
  #  'scripts': ['bin/djoro_regulation_server.py'],
    'name': 'djoro_regulation_server'
}

setup(**config)
