netaddr
=======

A Python library for representing and manipulating network addresses.

It supports the ability to work and interact with the following:

- IPv4 and IPv6 addresses and subnets
- MAC addresses, OUI and IAB identifiers, IEEE EUI-64 identifiers
- arbitrary (non-aligned) IP address ranges and IP address sets
- various non-CIDR IP range formats such as nmap and glob-style formats

There are routines that allow :

- generating, sorting and summarizing IP addresses and networks
- performing easy conversions between address notations and formats
- detecting, parsing and formatting network address representations
- performing set-based operations on groups of IP addresses and subnets
- working with arbitrary IP address ranges and formats
- accessing OUI and IAB organisational information published by IEEE
- accessing IP address and block information published by IANA

Changes
-------

For details on the latest updates and changes, see :doc:`changes`

License
-------

This software is released under the liberal BSD license.

See the :doc:`license` and :doc:`copyright` for full text.

Dependencies
------------

Python 2.4 or higher.

Python 3.x support available from netaddr version 0.7.5 onwards.

Required IPython for the interactive netaddr shell.

Installation
------------

See :doc:`installation` for details.

Documentation
-------------

The code contains docstrings throughout and a full set of project
documentation along with tutorials can be found here :-

http://pythonhosted.org/netaddr/
http://readthedocs.org/docs/netaddr/en/latest/

Running The Tests
-----------------

netaddr uses py.test (http://pytest.org/) for its test suite.

To run the unit tests, clone the repository and run the following in the
root directory :-

    python setup.py test

If any of the tests fail, *please* help the project's user base by filing
bug reports on the netaddr Issue Tracker, here :-

	http://github.com/drkjam/netaddr/issues

Efforts have been made to ensure this code works equally well on both big and 
little endian architectures. However, the project does not own or have access
to any big endian hardware (e.g. SPARC or PowerPC) for continual regression 
testing. If you happen to work on big endian architectures with Python and wish
to use netaddr *PLEASE* ensure you run the unit tests before you using it in a 
production setting just to make sure everything is functioning as expected.

And finally...
--------------

Share and enjoy!
