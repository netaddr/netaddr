=====================
netaddr documentation
=====================

A Python library and a :doc:`reference/cli` for representing and manipulating layer 3 (IP) and layer 2 (MAC)
network addresses.

netaddr provides support for:

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

netaddr's documentation uses the `Diátaxis approach to technical documentation
authoring <https://diataxis.fr/>`_ and is organized like so:

* :doc:`tutorials` take you on a step-by-step journey through some of the netaddr's features.
  Start here if you're new to netaddr.
* :doc:`how-to` are recipes and provide steps to address common problems and use-cases.
* :doc:`reference` contains technical description of various parts of netaddr machinery
  (including the :doc:`api`).

.. toctree::
    :maxdepth: 1
    :hidden:
    :caption: User documentation

    tutorials
    how-to
    reference

.. toctree::
    :maxdepth: 1
    :hidden:
    :caption: Developer documentation

    dev-how-to/index

.. toctree::
    :maxdepth: 1
    :hidden:
    :caption: Misc

    changes
    copyright
    license
    authors
    contributors

.. toctree::
    :maxdepth: 1
    :hidden:
    :caption: Project links

    Source code repository <https://github.com/netaddr/netaddr/>
    PyPI page <https://pypi.org/project/netaddr/>

------------------
Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`

