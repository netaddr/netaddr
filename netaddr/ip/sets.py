#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""Set based operations for IP addresses and subnets."""
import sys as _sys
import itertools as _itertools

from netaddr.ip import IPNetwork, IPAddress, cidr_merge, cidr_exclude, \
    iter_iprange, iprange_to_cidrs

from intset import IntSet as _IntSet

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
        cidrs = cidr_merge(self._cidrs)
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
        return self._cidrs.popitem()

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

        #TODO:   !!! implement IPv6 support !!!
        lhs = _IntSet(*[(c.first, c.last) for c in self._cidrs])
        rhs = _IntSet(*[(c.first, c.last) for c in other._cidrs])

        return lhs.issubset(rhs)

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

        #TODO:   !!! implement IPv6 support !!!
        lhs = _IntSet(*[(c.first, c.last) for c in self._cidrs])
        rhs = _IntSet(*[(c.first, c.last) for c in other._cidrs])

        return lhs.issuperset(rhs)

    __ge__ = issuperset

    def union(self, other):
        """
        @param other: an IP set.

        @return: the union of this IP set and another as a new IP set
            (combines IP addresses and subnets from both sets).
        """
#COMPARE:        ipset = self.copy()
#COMPARE:        ipset.update(other)
#COMPARE:        ipset.compact()
#COMPARE:        return ipset
        #TODO:   !!! implement IPv6 support !!!
        lhs = _IntSet(*[(c.first, c.last) for c in self._cidrs])
        rhs = _IntSet(*[(c.first, c.last) for c in other._cidrs])

        sdiff = lhs | rhs

        cidr_list = []
        for start, end in list(sdiff._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start), IPAddress(end-1))
            cidr_list.extend(cidrs)

        return IPSet(sorted(cidr_list))

    __or__ = union

    def intersection(self, other):
        """
        @param other: an IP set.

        @return: the intersection of this IP set and another as a new IP set.
            (IP addresses and subnets common to both sets).
        """
        #TODO:   !!! implement IPv6 support !!!
        lhs = _IntSet(*[(c.first, c.last) for c in self._cidrs])
        rhs = _IntSet(*[(c.first, c.last) for c in other._cidrs])

        sdiff = lhs & rhs

        cidr_list = []
        for start, end in list(sdiff._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start), IPAddress(end-1))
            cidr_list.extend(cidrs)

        return IPSet(sorted(cidr_list))

    __and__ = intersection

    def symmetric_difference(self, other):
        """
        @param other: an IP set.

        @return: the symmetric difference of this IP set and another as a new
            IP set (all IP addresses and subnets that are in exactly one
            of the sets).
        """
        #TODO:   !!! implement IPv6 support !!!
        lhs = _IntSet(*[(c.first, c.last) for c in self._cidrs])
        rhs = _IntSet(*[(c.first, c.last) for c in other._cidrs])

        sdiff = lhs ^ rhs

        cidr_list = []
        for start, end in list(sdiff._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start), IPAddress(end-1))
            cidr_list.extend(cidrs)

        return IPSet(sorted(cidr_list))

    __xor__ = symmetric_difference

    def difference(self, other):
        """
        @param other: an IP set.

        @return: the difference between this IP set and another as a new IP
            set (all IP addresses and subnets that are in this IP set but
            not found in the other.)
        """
        #TODO:   !!! implement IPv6 support !!!
        lhs = _IntSet(*[(c.first, c.last) for c in self._cidrs])
        rhs = _IntSet(*[(c.first, c.last) for c in other._cidrs])

        sdiff = lhs - rhs

        cidr_list = []
        for start, end in list(sdiff._ranges):
            cidrs = iprange_to_cidrs(IPAddress(start), IPAddress(end-1))
            cidr_list.extend(cidrs)

        return IPSet(sorted(cidr_list))

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

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    import pprint
    print IPNetwork('0.0.0.0/0').size
    print IPSet(['0.0.0.0/0']).size
#    s1 = IPSet(['192.0.4.0', '192.0.2.0/30', IPAddress('192.0.3.16')])
#
#    print len(s1)
#    pprint.pprint(list(s1))
#    print repr(s1)
#
#    s2 = IPSet([
#        IPNetwork('192.0.2.0/30'),
#        IPAddress('192.0.3.16'),
#        IPAddress('192.0.4.0')])
#
#    print s1 == s2
#    print s1 != s2
#    s3 = s1.copy()
#    print s3
#    print id(s1)
#    print id(s3)
#    #   Union
#    s4 = IPSet(['1.1.1.1', '1.1.1.2']) | IPSet(['1.1.1.3'])
#    pprint.pprint(list(s4))
#
#    print cidr_merge(['1.1.1.1', '1.1.1.2', '1.1.1.3'])
#    #   Intersection
#    print IPSet(['1.1.1.1', '1.1.1.2']) & IPSet(['1.1.1.2', '1.1.1.3'])
#
#    print IPSet(['192.0.2.0', '192.0.2.0/32'])

#    s1 = IPSet()
#
#    print s1
#    for ip in IPNetwork('192.0.2.0/28'):
#        s1.add(ip)
#        print s1, len(s1)
#
#    print '-' * 79
#
#    s2 = IPSet(['192.0.2.0/28'])
#
#    print s2
#    for ip in IPNetwork('192.0.2.0/28'):
#        s2.remove(ip)
#        print s2, len(s2)
#
#    print '-' * 79
#
#    removals = [
#        '192.0.1.0/22',
#        '192.0.7.0/24',
#        '192.0.9.0/24',
#        '192.0.11.0/24',
#        '192.0.13.0/24',
#        '192.0.15.0/24',
#    ]
#
#    s3 = IPSet(['192.168.0.0/23'])
#
#    print 'start:', s3
#    cidr = IPNetwork('192.168.0.0/23')
#    print '%-20s %-17s -> %-17s' % (cidr, cidr[0], cidr[-1])
#
#    print '---'
#    print 'to be removed :-'
#    print
#    for cidr in removals:
#        cidr = IPNetwork(cidr)
#        print '%-20s %-17s -> %-17s' % (cidr, cidr[0], cidr[-1])
#        s3.remove(cidr)
#
#    print '---'
#    print 'results:', s3
#    print '---'
#    for cidr in s3.iter_cidrs():
#        print '%-20s %-17s -> %-17s' % (cidr, cidr[0], cidr[-1])
#    print '---'
#
#    print IPSet(['192.0.2.0/24']) | IPSet(['192.0.3.0/24'])

#    s1 = IPSet(['192.168.0.0/24', '192.168.2.0/24', '192.168.4.0/24'])
#    print s1
#    addr = '192.168.0.0/23'
#    print 'remove: ', addr
#    s1.remove(addr)
#    print s1
#    print IPSet(['1.1.1.0/24']) ^ IPSet(['1.1.1.16/28'])
#    print IPSet(['1.1.1.0/21', '1.1.2.0/24', '1.1.3.0/24']) ^ \
#          IPSet(['1.1.2.0/24', '1.1.4.0/24'])


    ipv4_addr_space = IPSet(['0.0.0.0/0'])

    private = IPSet([
        '192.168.0.0/16',
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.0.2.0/24',
        '239.192.0.0/14'])

    reserved = IPSet([
        '240.0.0.0/4',
        '234.0.0.0/7',
        '236.0.0.0/7',
        '225.0.0.0/8',
        '226.0.0.0/7',
        '228.0.0.0/6',
        '234.0.0.0/7',
        '236.0.0.0/7',
        '238.0.0.0/8'])

    unavailable = reserved | private

    print 'LHS:', ipv4_addr_space
    print 'RHS:', unavailable
    result = ipv4_addr_space ^ unavailable
    print 'Result:', result
    for  cidr in result.iter_cidrs():
        print cidr, cidr[0], cidr[-1]
#        try:
#            ipv4_info = cidr.info['IPv4'][0]
#            info = ipv4_info['prefix'], ipv4_info['status']
#        except KeyError:
#            info = 'n/a'
#        print '%-20s %-17s %-17s' % (cidr, cidr[0], cidr[-1]), info

