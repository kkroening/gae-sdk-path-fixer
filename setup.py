#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='gae-sdk-path-fixer',
    version='0.0.1',
    description='GAE SDK Path Fixer: detect AppEngine SDK and fix Python sys.path',
    author='Karl Kroening',
    author_email='karlk@kralnet.us',
    url='https://github.com/kkroening/gae-sdk-path-fixer',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'download-gae-sdk=gae_sdk_path_fixer.download_gae_sdk:main',
        ],
    },

)
