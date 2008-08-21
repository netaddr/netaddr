#!/usr/bin/env python

from distutils.core import setup
import netaddr

setup(
    name            = 'netaddr',
    version         = netaddr.__version__,
    description     = 'Pythonic manipulation of IPv4, IPv6, CIDR, EUI and MAC network addresses',
    download_url    = 'http://code.google.com/p/netaddr/downloads/list',
    author          = 'David P. D. Moss',
    author_email    = 'drkjam@gmail.com',
    url             = 'http://code.google.com/p/netaddr/',
    packages        = ['netaddr'],
    license         = 'BSD License',
    long_description = """a library providing Pythonic manipulation, validation and classification of
common networking address notations, including :-

* IPv4
* IPv6
* CIDR (Classless Inter-Domain Routing)
* IEEE EUI-48, EUI-64 and MAC (Media Access Control)

Each object represents an individual address or address range and behaves as you
would expect when treated like standard Python types. For example :-

If you call list() on a CIDR object, it provides an iterator yielding IP
addresses.

Calling len() returns the number of addresses found within the range.

Indexing and/or slicing returns the addresses you'd expect. int() and hex()
return the numerical value of an address in network byte order in the respective
formats.""",
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
