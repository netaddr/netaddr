=============
API Reference
=============

.. toctree::
    :maxdepth: 2

------------------
IP Class Hierarchy
------------------

Here the class hierarchy for IP related classes ::

                                +--------+    +-------------+
                                | BaseIP |    | IPListMixin |
     +---------+                +--------+    +-------------+   +---------+
     | ipv4(M) |                     |          |        |      | ipv6(M) |
     +---------+                     |          |        |      +---------+
          |         +----------------+----------------+  |           |
       (HAS A)      |                |          |     |  |        (HAS A)
          |         |                |          |     |  |           |
          +-----+----------------+-----------------+  |  |           |
                |   |   +--------|-------+---------|--------+--------+
                |   |   |        |   |   |      |  |  |  |  |
                |   |   |        |   |   |      |  |  |  |  |
                v   v   v        v   v   v      |  |  |  |  |
              +-----------+    +-----------+    |  |  |  |  |
              | IPAddress |    | IPNetwork |<---+  |  |  |  |
              +-----------+    +-----------+       |  |  |  |
                    |                |             |  |  |  |
                 (HAS A)          (HAS A)          |  |  |  |
                    |                |             v  v  v  v
                    +-------+--------+           +------------+
                            |                    |  IPRange   |
                            |                    +------------+
                            v                          |
                        +-------+                      |
                        | IPSet |                      v
                        +-------+                  +--------+
                                                   | IPGlob |
                                                   +--------+


---------
Constants
---------

The following constants are used by the various *flags* arguments on netaddr class constructors.

.. data:: P
          INET_PTON

   Use inet_pton() semantics instead of inet_aton() when parsing IPv4.

.. data:: Z
          ZEROFILL

   Remove any preceding zeros from IPv4 address octets before parsing.

.. data:: N
          NOHOST

   Remove any host bits found to the right of an applied CIDR prefix

-----------------
Custom Exceptions
-----------------
.. autoexception:: netaddr.AddrConversionError
.. autoexception:: netaddr.AddrFormatError
.. autoexception:: netaddr.NotRegisteredError

------------
IP addresses
------------

An IP address is a virtual address used to identify the source and destination of (layer 3) packets being transferred between hosts in a switched network. This library fully supports both IPv4 and the new IPv6 standards.

The `IPAddress` class is used to identify individual IP addresses.

.. autoclass:: netaddr.IPAddress
    :members:
    :special-members:

^^^^^^^^^^^^^^^^^^^^^^^^
IPv6 formatting dialects
^^^^^^^^^^^^^^^^^^^^^^^^

The following dialect classes can be used with the IPAddress.format method.

.. autoclass:: netaddr.ipv6_compact
    :members:

.. autoclass:: netaddr.ipv6_full
    :members:

.. autoclass:: netaddr.ipv6_verbose
    :members:

-----------------------
IP networks and subnets
-----------------------

The `IPNetwork` class is used to represent a group of IP addresses that comprise a network/subnet/VLAN containing hosts.

Nowadays, IP networks are usually specified using the CIDR format with a prefix indicating the size of the netmask. In the real world, there are a number of ways to express a "network"" and so the flexibility of the `IPNetwork` class constructor reflects this.

.. autoclass:: netaddr.IPNetwork
    :members:
    :special-members:

---------------------------
Arbitrary IP address ranges
---------------------------

netaddr was designed to accomodate the many different ways in which groups of IP addresses and IP networks are specified, not only in router configurations but also less standard but more human-readable forms found in, for instance, configuration files.

Here are the options currently available.

^^^^^^^^^^^^^^
bounded ranges
^^^^^^^^^^^^^^

A bounded range is a group of IP addresses specified using a start and end address forming a contiguous block. No bit boundaries are assumed but the end address must be numerically greater than or equal to the start address.

.. autoclass:: netaddr.IPRange
    :members:
    :special-members:

^^^^^^^^^^^^^^
IP glob ranges
^^^^^^^^^^^^^^

A very useful way to represent IP network in configuration files and on the command line for those who do not speak CIDR.

The `IPGlob` class is used to represent individual glob ranges.

.. autoclass:: netaddr.IPGlob
    :members:
    :special-members:

^^^^^^^^^^^^^^^^^^
globbing functions
^^^^^^^^^^^^^^^^^^

It is also very useful to be able to convert between glob ranges and CIDR and IP ranges. The following function enable these various conversions.

.. autofunction:: netaddr.cidr_to_glob
.. autofunction:: netaddr.glob_to_cidrs
.. autofunction:: netaddr.glob_to_iprange
.. autofunction:: netaddr.glob_to_iptuple
.. autofunction:: netaddr.iprange_to_globs

^^^^^^^^^^^^^^^
``nmap`` ranges
^^^^^^^^^^^^^^^

``nmap`` is a well known network security tool. It has a particularly flexible way of specifying IP address groupings.

Functions are provided that allow the verification and enumeration of IP address specified in this format.

.. autofunction:: netaddr.valid_nmap_range
.. autofunction:: netaddr.iter_nmap_range

-------
IP sets
-------

When dealing with large numbers of IP addresses and ranges it is often useful to manipulate them as sets so you can calculate intersections, unions and differences between various groups of them.

The `IPSet` class was built specifically for this purpose.

.. autoclass:: netaddr.IPSet
    :members:
    :special-members:

---------------------------
IP functions and generators
---------------------------

The following are a set of useful helper functions related to the various format supported in this library.

.. autofunction:: netaddr.all_matching_cidrs
.. autofunction:: netaddr.cidr_abbrev_to_verbose
.. autofunction:: netaddr.cidr_exclude
.. autofunction:: netaddr.cidr_merge
.. autofunction:: netaddr.iprange_to_cidrs
.. autofunction:: netaddr.iter_iprange
.. autofunction:: netaddr.iter_unique_ips
.. autofunction:: netaddr.largest_matching_cidr
.. autofunction:: netaddr.smallest_matching_cidr
.. autofunction:: netaddr.spanning_cidr

---------------------------------------
MAC addresses and the IEEE EUI standard
---------------------------------------

A MAC address is the 48-bit hardware address associated with a particular physical interface on a networked host. They are found in all networked devices and serve to identify (layer 2) frames in the networking stack.

The `EUI` class is used to represents MACs (as well as their larger and less common 64-bit cousins).

.. autoclass:: netaddr.EUI
    :members:
    :special-members:

.. autoclass:: netaddr.OUI
    :members:
    :special-members:

.. autoclass:: netaddr.IAB
    :members:
    :special-members:

^^^^^^^^^^^^^^^^^^^^^^^
MAC formatting dialects
^^^^^^^^^^^^^^^^^^^^^^^

The following dialects are used to specify the formatting of MAC addresses.

.. autoclass:: netaddr.mac_bare
    :members:

.. autoclass:: netaddr.mac_cisco
    :members:

.. autoclass:: netaddr.mac_eui48
    :members:

.. autoclass:: netaddr.mac_pgsql
    :members:

.. autoclass:: netaddr.mac_unix
    :members:

--------------------
Validation functions
--------------------
.. autofunction:: netaddr.valid_ipv4
.. autofunction:: netaddr.valid_ipv6
.. autofunction:: netaddr.valid_glob
.. autofunction:: netaddr.valid_mac

------------
A bit of fun
------------

Who said networking was all about being serious? It's always good to lighten up and have a bit of fun.

Let's face it, no networking library worth its salt would be complete without support for RFC 1924 - http://www.ietf.org/rfc/rfc1924 ``:-)``

.. autofunction:: netaddr.base85_to_ipv6
.. autofunction:: netaddr.ipv6_to_base85
