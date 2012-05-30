#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2012, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Routines for dealing with nmap-style IPv4 address ranges.

The nmap range specification represents between 1 and 4 contiguous IP address
blocks depending on the range specified.

Each octets can be represented with hyphenated range sets according to the
following rules:

    1. * ``x-y`` - the hyphenated octet (represents values x through y)
    2. x must be less than or equal to y
    3. x and y must be values between 0 through 255

Example nmap ranges ::

    '192.0.2.1'                 #   one IP address
    '192.0.2.0-31'              #   one block with 32 IP addresses.
    '192.0.2-3.1-254'           #   two blocks with 254 IP addresses.
    '0-255.0-255.0-255.0-255'   #   the whole IPv4 address space
"""

from netaddr.core import AddrFormatError
from netaddr.ip import IPAddress

#-----------------------------------------------------------------------------
def valid_nmap_range(iprange):
    """
    :param iprange: an nmap-style IP address range.

    :return: ``True`` if IP range is valid, ``False`` otherwise.
    """
    status = True
    if not hasattr(iprange, 'split'):
        status = False
    else:
        tokens = iprange.split('.')
        if len(tokens) != 4:
            status = False
        else:
            for token in tokens:
                if '-' in token:
                    octets = token.split('-')
                    if len(octets) not in (1, 2):
                        status = False
                        break
                    try:
                        if not 0 <= int(octets[0]) <= 255:
                            status = False
                            break
                        if not 0 <= int(octets[1]) <= 255:
                            status = False
                            break
                    except ValueError:
                        status = False
                        break
                    if int(octets[0]) > int(octets[1]):
                        status = False
                        break
                else:
                    try:
                        if not 0 <= int(token) <= 255:
                            status = False
                            break
                    except ValueError:
                        status = False
                        break
    return status

#-----------------------------------------------------------------------------
def iter_nmap_range(iprange):
    """
    The nmap security tool supports a custom type of IPv4 range using multiple
    hyphenated octets. This generator provides iterators yielding IP addresses
    according to this rule set.

    :param iprange: an nmap-style IP address range.

    :return: an iterator producing IPAddress objects for each IP in the range.
    """
    if not valid_nmap_range(iprange):
        raise AddrFormatError('invalid nmap range: %s' % iprange)

    matrix = []
    tokens = iprange.split('.')

    for token in tokens:
        if '-' in token:
            octets = token.split('-', 1)
            pair = (int(octets[0]), int(octets[1]))
        else:
            pair = (int(token), int(token))
        matrix.append(pair)

    for w in range(matrix[0][0], matrix[0][1]+1):
        for x in range(matrix[1][0], matrix[1][1]+1):
            for y in range(matrix[2][0], matrix[2][1]+1):
                for z in range(matrix[3][0], matrix[3][1]+1):
                    yield IPAddress("%d.%d.%d.%d" % (w, x, y, z))
