#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network address manipulation, done Pythonically
"""
import sys as _sys
if _sys.version_info[0:2] < (2, 4):
    raise RuntimeError('Python 2.4.x or higher is required!')

__version__ = '0.6.2'

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
    An Exception indicating that a network address format is not recognised.
    """
    pass

class AddrConversionError(Exception):
    """
    An Exception indicating a failure to convert between address types or
    notations.
    """
    pass

#-----------------------------------------------------------------------------
#   Submodule imports.
#-----------------------------------------------------------------------------

from netaddr.address import nrange, IP, IPRange, IPRangeSet, CIDR, \
    Wildcard, EUI

from netaddr.eui import OUI, IAB, NotRegisteredError

import netaddr.ip

from netaddr.strategy import ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64

#-----------------------------------------------------------------------------
#   Public interface.
#-----------------------------------------------------------------------------
__all__ = [
     # type constants
    'AT_UNSPEC', 'AT_INET', 'AT_INET6', 'AT_LINK', 'AT_EUI64',

    # module specific exceptions
    'AddrFormatError', 'AddrConversionError', 'NotRegisteredError',

    # shared strategy objects
    'ST_IPV4', 'ST_IPV6', 'ST_EUI48', 'ST_EUI64',

    # main interface classes
    'CIDR', 'IP', 'IPRange', 'IPRangeSet', 'Wildcard',
    'EUI', 'OUI', 'IAB',

    #   functions
    'nrange',
]
