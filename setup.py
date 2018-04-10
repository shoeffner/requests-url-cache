# -*- coding: utf-8 -*-

from setuptools import setup

from requests_url_cache import __version__


REPOSITORY = 'https://github.com/shoeffner/requests-url-cache'

setup(
    name='requests-url-cache',
    version=__version__,
    description='A drop-in python module for requests-cache to allow fine granular url-based caching.',
    author='Sebastian Höffner',
    author_email='info@sebastian-hoeffner.de',
    url=REPOSITORY,
    download_url='{}/tarball/{}'.format(REPOSITORY, __version__),
    modules=['requests_url_cache'],
    include_package_data=True,
    install_requires=[
        'requests',
        'requests-cache'
    ],
    license='MIT',
    keywords=['requests', 'cache', 'url']
)
