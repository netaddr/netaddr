#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network address manipulation, done Pythonically
"""
from address import Addr, IP, EUI, AddrRange, CIDR, Wildcard, nrange

from strategy import BIG_ENDIAN_PLATFORM, AT_LINK, AT_EUI64, AT_INET, \
    AT_INET6, AT_UNSPEC, ST_EUI48, ST_EUI64, ST_IPV4, ST_IPV6
