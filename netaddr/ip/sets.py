#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""Set based operations for IP addresses and subnets."""

import sys as _sys
import itertools as _itertools

from netaddr.ip.intset import IntSet as _IntSet

from netaddr.ip import IPNetwork, IPAddress, cidr_merge, cidr_exclude, \
    iprange_to_cidrs

#-----------------------------------------------------------------------------
def partition_ips(iterable):
    """
    Takes a sequence of IP addresses and networks splitting them into two
    separate sequences by IP version.

    @param iterable: a sequence or iterator contain IP addresses and networks.

    @return: a two element tuple (ipv4_list, ipv6_list).
    """
    #   Start off using set as we'll remove any duplicates at the start.
    if not hasattr(iterable, '__iter__'):
        raise ValueError('A sequence or iterator is expected!')

    ipv4 = []
    ipv6 = []

    for ip in iterable:
        if not hasattr(ip, 'version'):
            raise TypeError('IPAddress or IPNetwork expected!')

        if ip.version == 4:
            ipv4.append(ip)
        else:
            ipv6.append(ip)

    return ipv4, ipv6

#-----------------------------------------------------------------------------
class IPSet(object):
    """
    Represents an unordered collection (set) of unique IP addresses and
    subnets.
    """
    def __init__(self, iterable=None):
        """
        Constructor.

        @param iterable: (optional) an iterable containing IP addresses and
            subnets.
        """
        self._cidrs = {}
        if iterable is not None:
            for ip in cidr_merge(iterable):
                self._cidrs[ip] = True

    def compact(self):
        """
        Compact internal list of L{IPNetwork} objects using a CIDR merge.
        """
        cidrs = cidr_merge(list(self._cidrs))
        self._cidrs = dict(zip(cidrs, [True] * len(cidrs)))

    def __hash__(self):
        """
        B{Please Note}: IPSet objects are not hashable and cannot be used as
        dictionary keys or as members of other sets. Raises C{TypeError} if
        this method is called.
        """
        raise TypeError('IP sets are unhashable!')

    def __contains__(self, ip):
        """
        @param ip: An IP address or subnet.

        @return: C{True} if IP address or subnet is a member of this IP set.
        """
        ip = IPNetwork(ip)
        for cidr in self._cidrs:
            if ip in cidr:
                return True
        return False

    def __iter__(self):
        """
        @return: an iterator over the IP addresses within this IP set.
        """
        return _itertools.chain(*sorted(self._cidrs))

    def iter_cidrs(self):
        """
        @return: an iterator over individual IP subnets within this IP set.
        """
        return sorted(self._cidrs)

    def add(self, ip):
        """
        Adds an IP address or subnet to this IP set. Has no effect if it is
        already present.

        Note that where possible the IP address or subnet is merged with other
        members of the set to form more concise CIDR blocks.

        @param ip: An IP address or subnet.
        """
        self._cidrs[IPNetwork(ip)] = True
        self.compact()

    def remove(self, ip):
        """
        Removes an IP address or subnet from this IP set. Does nothing if it
        is not already a member.

        Note that this method behaves more like discard() found in regular
        Python sets because it doesn't raise KeyError exceptions if the
        IP address or subnet is question does not exist. It doesn't make sense
        to fully emulate that behaviour here as IP sets contain groups of
        individual IP addresses as individual set members using IPNetwork
        objects.

        @param ip: An IP address or subnet.
        """
        ip = IPNetwork(ip)

        #   This add() is required for address blocks provided that are larger
        #   than blocks found within the set but have overlaps. e.g. :-
        #
        #   >>> IPSet(['192.0.2.0/24']).remove('192.0.2.0/23')
        #   IPSet([])
        #
        self.add(ip)

        remainder = None
        matching_cidr = None

        #   Search for a matching CIDR and exclude IP from it.
        for cidr in self._cidrs:
            if ip in cidr:
                remainder = cidr_exclude(cidr, ip)
                matching_cidr = cidr
                break

        #   Replace matching CIDR with remaining CIDR elements.
        if remainder is not None:
            del self._cidrs[matching_cidr]
            for cidr in remainder:
                self._cidrs[cidr] = True
            self.compact()

    def pop(self):
        """
        Removes and returns an arbitrary IP address or subnet from this IP
        set.

        @return: An IP address or subnet.
        """
        return self._cidrs.popitem()[0]

    def isdisjoint(self, other):
        """
        @param other: an IP set.

        @return: C{True} if this IP set has no elements (IP addresses
            or subnets) in common with other. Intersection *must* be an
            empty set.
        """
        result = self.intersection(other)
        if result == IPSet():
            return True
        return False

    def copy(self):
        """@return: a shallow copy of this IP set."""
        obj_copy = self.__class__()
        obj_copy._cidrs.update(self._cidrs)
        return obj_copy

    def update(self, iterable):
        """
        Update the contents of this IP set with the union of itself and
        other IP set.

        @param iterable: an iterable containing IP addresses and subnets.
        """
        if not hasattr(iterable, '__iter__'):
            raise TypeError('an iterable was expected!')

        if hasattr(iterable, '_cidrs'):
            #   Another IP set.
            for ip in cidr_merge(self._cidrs.keys() + iterable._cidrs.keys()):
                self._cidrs[ip] = True
        else:
            #   An iterable contain IP addresses or subnets.
            for ip in cidr_merge(self._cidrs.keys() + list(iterable)):
                self._cidrs[ip] = True

        self.compact()

    def clear(self):
        """Remove all IP addresses and subnets from this IP set."""
        self._cidrs = {}

    def __eq__(self, other):
        """
        @param other: an IP set

        @return: C{True} if this IP set is equivalent to the C{other} IP set,
            C{False} otherwise.
        """
        try:
            return self._cidrs == other._cidrs
        except AttributeError:
            return NotImplemented

    def __ne__(self, other):
        """
        @param other: an IP set

        @return: C{False} if this IP set is equivalent to the C{other} IP set,
            C{True} otherwise.
        """
        try:
            return self._cidrs != other._cidrs
        except AttributeError:
            return NotImplemented

    def __lt__(self, other):
        """
        @param other: an IP set

        @return: C{True} if this IP set is less than the C{other} IP set,
            C{False} otherwise.
        """
        if not hasattr(other, '_cidrs'):
            return NotImplemented

        return len(self) < len(other) and self.issubset(other)

    def issubset(self, other):
        """
        @param other: an IP set.

        @return: C{True} if every IP address and subnet in this IP set
            is found within C{other}.
        """
        if not hasattr(other, '_cidrs'):
            return NotImplemented

        l_ipv4, l_ipv6 = partition_ips(self._cidrs)
        r_ipv4, r_ipv6 = partition_ips(other._cidrs)

        l_ipv4_iset = _IntSet(*[(c.first, c.last) for c in l_ipv4])
        r_ipv4_iset = _IntSet(*[(c.first, c.last) for c in r_ipv4])

        l_ipv6_iset = _IntSet(*[(c.first, c.last) for c in l_ipv6])
        r_ipv6_iset = _IntSet(*[(c.first, c.last) for c in r_ipv6])

        ipv4 = l_ipv4_iset.issubset(r_ipv4_iset)
        ipv6 = l_ipv6_iset.issubset(r_ipv6_iset)

        return ipv4 and ipv6

    __le__ = issubset

    def __gt__(self, other):
        """
        @param other: an IP set.

        @return: C{True} if this IP set is greater than the C{other} IP set,
            C{False} otherwise.
        """
        if not hasattr(other, '_cidrs'):
            return NotImplemented

        return len(self) > len(other) and self.issuperset(other)

    def issuperset(self, other):
        """
        @param other: an IP set.

        @return: C{True} if every IP address and subnet in other IP set
            is found within this one.
        """
        if not hasattr(other, '_cidrs'):
            return NotImplemented

        l_ipv4, l_ipv6 = partition_ips(self._cidrs)
        r_ipv4, r_ipv6 = partition_ips(other._cidrs)

        l_ipv4_iset = _IntSet(*[(c.first, c.last) for c in l_ipv4])
        r_ipv4_iset = _IntSet(*[(c.first, c.last) for c in r_ipv4])

        l_ipv6_iset = _IntSet(*[(c.first, c.last) for c in l_ipv6])
        r_ipv6_iset = _IntSet(*[(c.first, c.last) for c in r_ipv6])

        ipv4 = l_ipv4_iset.issuperset(r_ipv4_iset)
        ipv6 = l_ipv6_iset.issuperset(r_ipv6_iset)

        return ipv4 and ipv6

    __ge__ = issuperset

    def union(self, other):
        """
        @param other: an IP set.

        @return: the union of this IP set and another as a new IP set
            (combines IP addresses and subnets from both sets).
        """
        ip_set = self.copy()
        ip_set.update(other)
        ip_set.compact()
        return ip_set

    __or__ = union

    def intersection(self, other):
        """
        @param other: an IP set.

        @return: the intersection of this IP set and another as a new IP set.
            (IP addresses and subnets common to both sets).
        """
        cidr_list = []

        #   Separate IPv4 from IPv6.
        l_ipv4, l_ipv6 = partition_ips(self._cidrs)
        r_ipv4, r_ipv6 = partition_ips(other._cidrs)

        #   Process IPv4.
        l_ipv4_iset = _IntSet(*[(c.first, c.last) for c in l_ipv4])
        r_ipv4_iset = _IntSet(*[(c.first, c.last) for c in r_ipv4])

        ipv4_result = l_ipv4_iset & r_ipv4_iset

        for start, end in list(ipv4_result._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start, 4), IPAddress(end-1, 4))
            cidr_list.extend(cidrs)

        #   Process IPv6.
        l_ipv6_iset = _IntSet(*[(c.first, c.last) for c in l_ipv6])
        r_ipv6_iset = _IntSet(*[(c.first, c.last) for c in r_ipv6])

        ipv6_result = l_ipv6_iset & r_ipv6_iset

        for start, end in list(ipv6_result._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start, 6), IPAddress(end-1, 6))
            cidr_list.extend(cidrs)

        return IPSet(cidr_list)

    __and__ = intersection

    def symmetric_difference(self, other):
        """
        @param other: an IP set.

        @return: the symmetric difference of this IP set and another as a new
            IP set (all IP addresses and subnets that are in exactly one
            of the sets).
        """
        cidr_list = []

        #   Separate IPv4 from IPv6.
        l_ipv4, l_ipv6 = partition_ips(self._cidrs)
        r_ipv4, r_ipv6 = partition_ips(other._cidrs)

        #   Process IPv4.
        l_ipv4_iset = _IntSet(*[(c.first, c.last) for c in l_ipv4])
        r_ipv4_iset = _IntSet(*[(c.first, c.last) for c in r_ipv4])

        ipv4_result = l_ipv4_iset ^ r_ipv4_iset

        for start, end in list(ipv4_result._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start, 4), IPAddress(end-1, 4))
            cidr_list.extend(cidrs)

        #   Process IPv6.
        l_ipv6_iset = _IntSet(*[(c.first, c.last) for c in l_ipv6])
        r_ipv6_iset = _IntSet(*[(c.first, c.last) for c in r_ipv6])

        ipv6_result = l_ipv6_iset ^ r_ipv6_iset

        for start, end in list(ipv6_result._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start, 6), IPAddress(end-1, 6))
            cidr_list.extend(cidrs)

        return IPSet(cidr_list)

    __xor__ = symmetric_difference

    def difference(self, other):
        """
        @param other: an IP set.

        @return: the difference between this IP set and another as a new IP
            set (all IP addresses and subnets that are in this IP set but
            not found in the other.)
        """
        cidr_list = []

        #   Separate IPv4 from IPv6.
        l_ipv4, l_ipv6 = partition_ips(self._cidrs)
        r_ipv4, r_ipv6 = partition_ips(other._cidrs)

        #   Process IPv4.
        l_ipv4_iset = _IntSet(*[(c.first, c.last) for c in l_ipv4])
        r_ipv4_iset = _IntSet(*[(c.first, c.last) for c in r_ipv4])

        ipv4_result = l_ipv4_iset - r_ipv4_iset

        for start, end in list(ipv4_result._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start, 4), IPAddress(end-1, 4))
            cidr_list.extend(cidrs)

        #   Process IPv6.
        l_ipv6_iset = _IntSet(*[(c.first, c.last) for c in l_ipv6])
        r_ipv6_iset = _IntSet(*[(c.first, c.last) for c in r_ipv6])

        ipv6_result = l_ipv6_iset - r_ipv6_iset

        for start, end in list(ipv6_result._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start, 6), IPAddress(end-1, 6))
            cidr_list.extend(cidrs)

        return IPSet(cidr_list)

    __sub__ = difference

    def __len__(self):
        """
        @return: the cardinality of this IP set (i.e. sum of individual IP
            addresses). Raises C{IndexError} if size > sys.maxint (a Python
            limitation). Use the .size property for subnets of any size.
        """
        size = self.size
        if size > _sys.maxint:
            raise IndexError("range contains greater than %d (sys.maxint) " \
                "IP addresses! Use the .size property instead." % _sys.maxint)
        return size

    @property
    def size(self):
        """
        The cardinality of this IP set (based on the number of individual IP
        addresses including those implicitly defined in subnets).
        """
        return sum([cidr.size for cidr in self._cidrs])

    def __repr__(self):
        """@return: Python statement to create an equivalent object"""
        return 'IPSet(%r)' % [str(c) for c in sorted(self._cidrs)]

    __str__ = __repr__
