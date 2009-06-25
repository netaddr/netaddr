#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Set-based operations for groups of IP address and subnets.

"""
import itertools as _itertools

from netaddr.ip import IP, cidr_merge, iter_iprange

#-----------------------------------------------------------------------------
class IPSet(object):
    """
    Represents an unordered collection (set) of unique IP address and subnets.

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

    def __hash__(self):
        raise TypeError('IP sets are unhashable!')

    def __contains__(self, ip):
        """
        @param ip: An IP address or subnet.

        @return: True if IP address or subnet is a member of this IP set.
        """
        raise NotImplementedError('TODO')

    def __iter__(self):
        """
        @return: an iterator over the individual IP addresses in this IP set.
        """
        return _itertools.chain(*self._cidrs.iterkeys())

    def add(self, ip):
        """
        Adds an IP address or subnet to this IP set. Has no effect if it is
        already present.

        @param ip: An IP address or subnet.
        """
        raise NotImplementedError('TODO')

    def remove(self, ip):
        """
        Removes an IP address or subnet from this IP set. Raises a KeyError
        exception if it is not already a member.

        @param ip: An IP address or subnet.
        """
        raise NotImplementedError('TODO')

    def pop(self):
        """
        Removes and returns an arbitrary IP address or subnet from this IP
        set.

        @return: An IP address or subnet.
        """
        raise NotImplementedError('TODO')

    def discard(self, ip):
        """
        Removes an IP address or subnet from this IP set. Does nothing if it
        is not already a member.

        @param ip: An IP address or subnet.
        """
        raise NotImplementedError('TODO')

    def isdisjoint(other):
        """
        @param other: an IP set.

        @return True if this IP set has no elements (IP addresses or subnets)
            in common with other. Intersection *must* be an empty set.
        """
        raise NotImplementedError('TODO')

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

    def clear():
        """Remove all IP addresses and subnets from this IP set."""
        raise NotImplementedError('TODO')

    def __eq__(self, other):
        if hasattr(other, '_cidrs'):
            return self._cidrs == other._cidrs
        else:
            return False

    def __ne__(self, other):
        if hasattr(other, '_cidrs'):
            return self._cidrs != other._cidrs
        else:
            return False

    def __lt__(self, other):
        """
        self < other

        @param other:

        @return:
        """
        raise NotImplementedError('TODO')

    def issubset(self, other):
        """
        @param other: an IP set.

        @return: True if every IP address and subnet in this IP set
            is found within other.
        """
        raise NotImplementedError('TODO')

    __le__ = issubset

    def __gt__(self, other):
        """
        self > other

        @param other: an IP set.

        @return:
        """
        raise NotImplementedError('TODO')

    def issuperset(self, other):
        """
        @param other: an IP set.

        @return: True if every IP address and subnet in other IP set
            is found within this one.
        """
        raise NotImplementedError('TODO')

    __ge__ = issuperset

    def union(self, other):
        """
        self | other (bitwise AND)

        @param other: an IP set.

        @return: the union of this IP set and another as a new IP set
            (i.e. all IP addresses and subnets from both).
        """
        ipset = self.copy()
        ipset.update(other)
        return ipset

    __or__ = union

    def intersection(self, other):
        """
        self & other (bitwise AND)

        @param other: an IP set.

        @return: the intersection of this IP set and another as a new IP set.
            (i.e. all IP addresses and subnets from both).
        """
        raise NotImplementedError('TODO')

    __and__ = intersection

    def symmetric_difference(self, other):
        """
        self ^ other (bitwise XOR)

        @param other: an IP set.

        @return: the symmetric difference of this IP set and another as a new
            IP set (i.e. all IP addresses and subnets that are in exactly one
            of the sets).
        """
        raise NotImplementedError('TODO')

    __xor__ = symmetric_difference

    def difference(self, other):
        """
        self - other (difference)

        @param other: an IP set.

        @return: the difference between this IP set and another as a new IP
            set (i.e. all IP addresses and subnets that are in this IP set but
            not found in other.)
        """
        raise NotImplementedError('TODO')

    __sub__ = difference

    def __len__(self):
        """
        @return: the cardinality of this IP set (based on the number of
            individual IP addresses including those implicitly defined in
            subnets).
        """
        return sum([len(c) for c in self._cidrs])

    def __repr__(self):
        """@return: Python statement to create an equivalent object"""
        return 'IPSet(%r)' % sorted(self._cidrs.keys())

    __str__ = __repr__

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    s1 = IPSet(['192.0.4.0', '192.0.2.0/30', IP('192.0.3.16')])
    s2 = IPSet([IP('192.0.2.0/30'), IP('192.0.3.16'), IP('192.0.4.0')])
    print len(s1)
    print list(s1)
    print repr(s1)
    print s1 == s2
    print s1 != s2
    s3 = s1.copy()
    print s3
    print id(s1)
    print id(s3)
    #   Union
    print IPSet(['1.1.1.1', '1.1.1.2']) | IPSet(['1.1.1.3'])
    print cidr_merge(['1.1.1.1', '1.1.1.2', '1.1.1.3'])
    #   Intersection
    print IPSet(['1.1.1.1', '1.1.1.2']) & IPSet(['1.1.1.2', '1.1.1.3'])

