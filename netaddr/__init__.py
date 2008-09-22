#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network address manipulation, done Pythonically
"""
__version__ = '0.5.1'

import struct as _struct

#-----------------------------------------------------------------------------
#  Constants.
#-----------------------------------------------------------------------------

#: True if platform is natively big endian, False otherwise.
BIG_ENDIAN_PLATFORM = _struct.pack('=h', 1) == _struct.pack('>h', 1)

AT_UNSPEC = 0x0     #: unspecified address type constant.
AT_INET   = 0x4     #: IPv4 address type constant.
AT_INET6  = 0x6     #: IPv6 address type constant.
AT_LINK   = 0x30    #: MAC/EUI-48 address type constant.
AT_EUI64  = 0x40    #: EUI-64 address type constant.

#: Address type to address description lookup dictionary.
AT_NAMES = {
    #   Address Type : Descriptive Name.
    AT_UNSPEC   : 'unspecified',
    AT_INET     : 'IPv4',
    AT_INET6    : 'IPv6',
    AT_LINK     : 'MAC',
    AT_EUI64    : 'EUI-64',
}

#-----------------------------------------------------------------------------
#   Custom exceptions.
#-----------------------------------------------------------------------------

class AddrFormatError(Exception):
    """
    Network address format not recognised.
    """
    pass

class AddrConversionError(Exception):
    """
    Conversion between address types or notations failed.
    """
    pass

#-----------------------------------------------------------------------------
#   Public interface and exports.
#-----------------------------------------------------------------------------

from netaddr.address import Addr, AddrRange, nrange, IP, CIDR, Wildcard, EUI

from netaddr.strategy import ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64

__all__ = [
    'Addr', 'AddrRange', 'nrange',                  # generic functionality
    'AddrFormatError', 'AddrConversionError',       # custom exceptions
    'IP', 'CIDR', 'Wildcard', 'EUI',                # general purpose classes
    'ST_IPV4', 'ST_IPV6', 'ST_EUI48', 'ST_EUI64',   # shared strategy objects
    'AT_INET', 'AT_INET6', 'AT_LINK', 'AT_EUI64',   # type constants
]
