#!/usr/bin/env python

from distutils.core import setup

setup(
    name            = 'netaddr',
    version         = '0.4',
    description     = 'network address manipulation, done Pythonically',
    download_url    = 'http://code.google.com/p/netaddr/downloads/list',
    author          = 'David P. D. Moss',
    author_email    = 'drkjam@gmail.com',
    url             = 'http://code.google.com/p/netaddr/',
    packages        = ['netaddr'],
    license         = 'BSD License',
    long_description = """
a library supporting Pythonic manipulation of several common network
address notations and standards including :-

- IP version 4
- IP version 6
- CIDR (Classless Inter-Domain Routing)
- IEEE EUI-48 and EUI-64
- MAC (Media Access Control)
""",
    platforms = 'OS Independent',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Education :: Testing',
        'Topic :: Home Automation',
        'Topic :: Internet',
        'Topic :: Internet :: Log Analysis',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Firewalls',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Operating System',
        'Topic :: System :: Shells',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
