#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Utility functions for dealing with wildcard or glob-style IP address ranges.

Individual octets can be represented using the following shortcuts :

    1. C{*} - the asterisk octet (represents values 0 through 255)
    2. C{'x-y'} - the hyphenated octet (represents values x through y)

A few basic rules also apply :

    1. x must always be greater than y, therefore :

        - x can only be 0 through 254
        - y can only be 1 through 255

    2. only one hyphenated octet per IP glob is allowed
    3. only asterisks are permitted after a hyphenated octet

Example IP globs ::

    '192.0.2.1'       #   a single address
    '192.0.2.0-31'    #   32 addresses
    '192.0.2.*'       #   256 addresses
    '192.0.2-3.*'     #   512 addresses
    '192.0-1.*.*'   #   131,072 addresses
    '*.*.*.*'           #   the whole IPv4 address space

Aside
=====
    I{IP glob ranges are not directly equivalent to CIDR blocks. They can
    represent address ranges that do not fall on strict bit mask boundaries.
    They are suitable for use in configuration files, being more obvious and
    readable than their CIDR counterparts, especially for admins and end users
    with little or no networking knowledge or experience.}

    I{All CIDR addresses can always be represented as IP globs but the reverse
    is not always true.}
"""

from netaddr.core import AddrFormatError, AddrConversionError
from netaddr.ip import IP, iprange_to_cidrs

#-----------------------------------------------------------------------------
def valid_glob(ipglob):
    """
    @param ipglob: An IP address range in a glob-style format.

    @return: C{True} if IP range glob is valid, C{False} otherwise.
    """
    #TODO: Add support for abbreviated ipglobs.
    #TODO: e.g. 192.0.*.* == 192.0.*
    #TODO:      *.*.*.*     == *
    #TODO: Add strict flag to enable verbose ipglob checking.
    if not hasattr(ipglob, 'split'):
        return False

    seen_hyphen = False
    seen_asterisk = False

    octets = ipglob.split('.')

    if len(octets) != 4:
        return False

    for octet in octets:
        if '-' in octet:
            if seen_hyphen:
                return False
            seen_hyphen = True
            if seen_asterisk:
                #   Asterisks cannot precede hyphenated octets.
                return False
            (octet1, octet2) = [int(i) for i in octet.split('-')]
            if octet1 >= octet2:
                return False
            if not 0 <= octet1 <= 254:
                return False
            if not 1 <= octet2 <= 255:
                return False
        elif octet == '*':
            seen_asterisk = True
        else:
            if seen_hyphen is True:
                return False
            if seen_asterisk is True:
                return False
            if not 0 <= int(octet) <= 255:
                return False

    return True

#-----------------------------------------------------------------------------
def glob_to_iprange(ipglob):
    """
    A function that accepts a glob-style IP range and returns the component
    lower and upper bound IP address.

    @param ipglob: an IP address range in a glob-style format.

    @return: a tuple contain lower and upper bound IP objects.
    """
    if not valid_glob(ipglob):
        raise AddrFormatError('not a recognised IP glob range: %r!' % ipglob)

    start_tokens = []
    end_tokens = []

    for octet in ipglob.split('.'):
        if '-' in octet:
            tokens = octet.split('-')
            start_tokens.append(tokens[0])
            end_tokens.append(tokens[1])
        elif octet == '*':
            start_tokens.append('0')
            end_tokens.append('255')
        else:
            start_tokens.append(octet)
            end_tokens.append(octet)

    return IP('.'.join(start_tokens)), IP('.'.join(end_tokens))

#-----------------------------------------------------------------------------
def iprange_to_globs(start, end):
    """
    A function that accepts an arbitrary start and end IP address or subnet
    and returns one or more glob-style IP ranges.

    @param start: the start IP address or subnet.

    @param end: the end IP address or subnet.

    @return: a list containing one or more IP globs.
    """
    start = IP(start)
    end = IP(end)

    if start.version != 4 and end.version != 4:
        raise AddrConversionError('IP glob ranges only support IPv4!')

    def _iprange_to_glob(lb, ub):
        #   Internal function to process individual IP globs.
        t1 = [int(_) for _ in str(lb).split('.')]
        t2 = [int(_) for _ in str(ub).split('.')]

        tokens = []

        seen_hyphen = False
        seen_asterisk = False

        for i in range(4):
            if t1[i] == t2[i]:
                #   A normal octet.
                tokens.append(str(t1[i]))
            elif (t1[i] == 0) and (t2[i] == 255):
                #   An asterisk octet.
                tokens.append('*')
                seen_asterisk = True
            else:
                #   Create a hyphenated octet - only one allowed per IP glob.
                if not seen_asterisk:
                    if not seen_hyphen:
                        tokens.append('%s-%s' % (t1[i], t2[i]))
                        seen_hyphen = True
                    else:
                        raise AddrConversionError('only 1 hyphenated octet' \
                            ' per IP glob allowed!')
                else:
                    raise AddrConversionError("asterisks are not allowed' \
                        ' before hyphenated octets!")

        return '.'.join(tokens)

    globs = []

    try:
        #   IP range can be represented by a single glob.
        ipglob = _iprange_to_glob(start, end)
        globs.append(ipglob)
    except AddrConversionError:
        #   Break IP range up into CIDRs before conversion to globs.
        #
        #TODO: this is still not completely optimised but is good enough
        #TODO: for the moment.
        #
        for cidr in iprange_to_cidrs(start, end):
            ipglob = _iprange_to_glob(cidr[0], cidr[-1])
            globs.append(ipglob)

    return globs

#-----------------------------------------------------------------------------
def glob_to_cidrs(ipglob):
    """
    A function that accepts a glob-style IP range and returns a list of one or more IP CIDRs that exactly matches it.

    @param ipglob: an IP address range in a glob-style format.

    @return: a list of one or more IP objects.
    """
    return iprange_to_cidrs(*glob_to_iprange(ipglob))

#-----------------------------------------------------------------------------
def cidr_to_glob(cidr):
    """
    A function that accepts an IP subnet in a glob-style format and returns
    a list of CIDR subnets that exactly matches the specified glob.

    @param cidr: an IP object CIDR subnet.

    @return: a list of one or more IP addresses and subnets.
    """
    ip = IP(cidr)
    globs = iprange_to_globs(ip[0], ip[-1])
    if len(globs) != 1:
        #   There should only ever be a one to one mapping between a CIDR and
        #   an IP glob range.
        raise AddrConversionError('bad CIDR to IP glob conversion!')
    return globs[0]
