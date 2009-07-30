#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""A Python library for manipulating IP and EUI network addresses."""

import sys as _sys

if _sys.version_info[0:2] < (2, 4):
    raise RuntimeError('Python 2.4.x or higher is required!')

__version__ = '0.7rc1'

from netaddr.core import AddrConversionError, AddrFormatError, \
    NotRegisteredError

from netaddr.ip import IPAddress, IPNetwork, IPRange, \
    cidr_abbrev_to_verbose, cidr_exclude, cidr_merge, spanning_cidr, \
    iter_unique_ips, iprange_to_cidrs, iter_iprange, smallest_matching_cidr, \
    largest_matching_cidr, all_matching_cidrs

from netaddr.ip.sets import IPSet

from netaddr.ip.glob import IPGlob, cidr_to_glob, glob_to_cidrs, \
    glob_to_iptuple, valid_glob, iprange_to_globs

from netaddr.eui import EUI, IAB, OUI

from netaddr.strategy.eui48 import mac_eui48, mac_unix, mac_cisco, \
    mac_bare, mac_pgsql

from netaddr.strategy.ipv6 import ipv6_compact, ipv6_full, ipv6_verbose

__all__ = [
    #   Custom exceptions.
    'AddrConversionError', 'AddrFormatError', 'NotRegisteredError',

    #   EUI related classes.
    'EUI', 'IAB', 'OUI',

    #   MAC address dialect classes.
    'mac_bare', 'mac_cisco', 'mac_eui48', 'mac_pgsql', 'mac_unix',

    #   IPv6 dialect classes.
    'ipv6_compact', 'ipv6_full', 'ipv6_verbose',

    #   IP, CIDR and IP range related classes and functions.
    'IPAddress', 'IPNetwork', 'IPRange', 'IPSet',

    'cidr_abbrev_to_verbose', 'cidr_exclude', 'cidr_merge', 'spanning_cidr',
    'iter_iprange', 'iprange_to_cidrs','iter_unique_ips',
    'smallest_matching_cidr', 'largest_matching_cidr', 'all_matching_cidrs',

    #   IP globbing routines.
    'IPGlob', 'valid_glob', 'cidr_to_glob', 'glob_to_cidrs', 'glob_to_iptuple',
    'iprange_to_globs',
]
