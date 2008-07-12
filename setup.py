#!/usr/bin/env python

from distutils.core import setup

setup(
    name            = 'netaddr',
    version         = '0.3',
    description     = 'network address manipulation, done Pythonically',
    download_url    = 'http://code.google.com/p/netaddr/downloads/list',
    author          = 'David P. D. Moss',
    author_email    = 'drkjam@gmail.com',
    url             = 'http://code.google.com/p/netaddr/',
    packages        = ['netaddr'],
    classifiers = [
        'Development Status :: 3 - Beta',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Network Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Networking',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
)
