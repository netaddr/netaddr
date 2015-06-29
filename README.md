netaddr
=======

A Python library for representing and manipulating network addresses.

Provides support for:

Layer 3 addresses

- IPv4 and IPv6 addresses, subnets, masks, prefixes
- iterating, slicing, sorting, summarizing and classifying IP networks
- dealing with various ranges formats (CIDR, arbitrary ranges and globs, nmap)
- set based operations (unions, intersections etc) over IP addresses and subnets
- parsing a large variety of different formats and notations
- looking up IANA IP block information
- generating DNS reverse lookups
- supernetting and subnetting

Layer 2 addresses

- representation and manipulation MAC addresses and EUI-64 identifiers
- looking up IEEE organisational information (OUI, IAB)
- generating derived IPv6 addresses

Changes
-------

For details on the latest updates and changes, see :doc:`changes`

License
-------

This software is released under the liberal BSD license.

See the :doc:`license` and :doc:`copyright` for full text.

Dependencies
------------

- Python 2.5.x through 3.5.x
- IPython (for netaddr interactive shell)

Installation
------------

See :doc:`installation` for details.

Documentation
-------------

This library has comprehensive docstrings and a full set of project
documentation (including tutorials):

- http://pythonhosted.org/netaddr/
- http://readthedocs.org/docs/netaddr/en/latest/

Tests
-----

netaddr requires py.test (http://pytest.org/).

To run the test suite, clone the repository and run:

    python setup.py test

If any of the tests fail, *please* help the project's user base by filing
bug reports on the netaddr issue tracker:

- http://github.com/drkjam/netaddr/issues

Finally...
----------

Share and enjoy!
