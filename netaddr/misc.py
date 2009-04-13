#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Miscellaneous functions and classes. Do not rely on anything in here as it is
liable to change, move or be deleted with each release.
"""
import pprint

from netaddr import CIDR, IPGlob

#-----------------------------------------------------------------------------
def ipv4_cidr_prefixes():
    """
    Returns a recordset (list of dicts) of host/network breakdown for IPv4
    using all of the various CIDR prefixes.
    """
    table = []
    prefix = 32
    while prefix >= 0:
        cidr = CIDR('0.0.0.0/%d' % prefix)
        table.append(dict(prefix=str(cidr), hosts=cidr.size(),
            networks=2 ** cidr.prefixlen))
        prefix -= 1
    return table

#-----------------------------------------------------------------------------
def ipv6_cidr_prefixes():
    """
    Returns a recordset (list of dicts) of host/network breakdown for IPv6
    using all of the various CIDR prefixes.
    """
    table = []
    prefix = 128
    while prefix >= 0:
        cidr = CIDR('::/%d' % prefix)
        table.append(dict(prefix=str(cidr), hosts=cidr.size(),
            networks=2 ** cidr.prefixlen))
        prefix -= 1
    return table

#-----------------------------------------------------------------------------
def print_ipv4_cidr_prefixes():
    """
    Prints a table to stdout of host/network breakdown for IPv4 using CIDR
    notation.
    """
    print '%-10s %-15s %-15s' % ('Prefix', 'Hosts', 'Networks')
    print '-'*10, '-'*15, '-'*15
    for record in ipv4_cidr_prefixes():
        print '%(prefix)-10s %(hosts)15s %(networks)15s' % record

#-----------------------------------------------------------------------------
def print_ipv6_cidr_prefixes():
    """
    Prints a table to stdout of host/network breakdown for IPv6 using CIDR
    notation.
    """
    print '%-10s %-40s %-40s' % ('Prefix', 'Hosts', 'Networks')
    print '-'*10, '-'*40, '-'*40
    for record in ipv6_cidr_prefixes():
        print '%(prefix)-10s %(hosts)40s %(networks)40s' % record

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    import pprint
    #pprint.pprint(ipv4_cidr_prefixes())
    print_ipv4_cidr_prefixes()
    #pprint.pprint(ipv6_cidr_prefixes())
    print_ipv6_cidr_prefixes()

