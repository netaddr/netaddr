#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""classes and functions for dealing with IPv4 and IPv6."""

import sys as _sys
import re as _re

from netaddr.core import AddrFormatError, AddrConversionError, num_bits
from netaddr.strategy import ipv4 as _ipv4
from netaddr.strategy import ipv6 as _ipv6

#-----------------------------------------------------------------------------
class IP(object):
    """
    Represents an individual IP address or an IP network with subnet prefix.
    The subnet prefix may either be an integer CIDR prefix, a netmask IP
    address or a hostmask IP address (Cisco style ACLs).

    Supports both IPv4 and IPv6.
    """
    def __init__(self, addr, version=None):
        """
        Constructor.

        @param addr: an IPv4 or IPv6 address with optional subnet prefix.
            May be an IP address in representation (string) format, an integer
            or another IP object (copy construction).

        @param version: the explict IP version to use when interpreting addr.
        """
        self._value = None
        self._prefixlen = None
        self._module = None

        if hasattr(addr, 'prefixlen'):
            #   Copy constructor.
            if version is not None and version != addr._module.version:
                raise ValueError('cannot switch IP versions using '
                    'copy constructor!')
            self._value = addr._value
            self._prefixlen = addr._prefixlen
            self._module = addr._module
        else:
            #   Explicit IP address version.
            if version is not None:
                if version == 4:
                    self._module = _ipv4
                elif version == 6:
                    self._module = _ipv6
                else:
                    raise ValueError('unsupported IP version %r' % version)

            if hasattr(addr, '__getitem__') and '/' in addr:
                #   IP address with CIDR prefix.
                try:
                    prefix, suffix = addr.split('/')
                except ValueError:
                    raise AddrFormatError('bad address format: %r' % addr)

                self.value = prefix
                self.prefixlen = suffix
            else:
                #   IP address (no CIDR prefix).
                self.value = addr
                self.prefixlen = self._module.width

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        if self._module is None:
            #   IP version is implicit, detect it from value.
            for module in (_ipv4, _ipv6):
                try:
                    self._value = module.str_to_int(value)
                    self._module = module
                    break
                except AddrFormatError:
                    try:
                        if 0 <= int(value) <= module.max_int:
                            self._value = int(value)
                            self._module = module
                            break
                    except ValueError:
                        pass

            if self._module is None:
                raise AddrFormatError('failed to detect IP version: %r'
                    % value)
        else:
            #   IP version is explicit.
            if hasattr(value, 'upper'):
                try:
                    self._value = self._module.str_to_int(value)
                except AddrFormatError:
                    raise AddrFormatError('base address %r is not IPv%d'
                        % (value, self._module.version))
            else:
                if 0 <= int(value) <= self._module.max_int:
                    self._value = int(value)
                else:
                    raise AddrFormatError('bad address format: %r' % value)

    value = property(_get_value, _set_value, None,
        'a positive integer representing the value of this IP address.')

    def _get_prefixlen(self):
        return self._prefixlen

    def _set_prefixlen(self, value):
        try:
            #   Integer CIDR prefix?
            if 0 <= int(value) <= self._module.width:
                self._prefixlen = int(value)
            else:
                raise AddrFormatError('CIDR prefix /%d out of range for ' \
                    'IPv%d!' % (int(value), self._module.version))
        except ValueError:
            #   Netmask or hostmask (ACL) style CIDR prefix.
            version = self._module.version
            addr = IP(value, version)

            if addr.is_netmask():
                self._prefixlen = addr.netmask_bits()
            elif addr.is_hostmask():
                #   prefixlen is an ACL (hostmask) address.
                netmask = IP(addr._module.max_int ^ int(addr), version)
                self._prefixlen = netmask.netmask_bits()
            else:
                #   Enforce this for now unless users want it changed.
                raise ValueError('CIDR prefix mask %r is invalid!' % addr)

    prefixlen = property(_get_prefixlen, _set_prefixlen, None,
        'size of the bitmask used to indentify and separate the network '
        'identifier from the host identifier in this IP address.')

    def is_unicast(self):
        """@return: C{True} if this IP is unicast, C{False} otherwise"""
        return not self.is_multicast()

    def is_multicast(self):
        """@return: C{True} if this IP is multicast, C{False} otherwise"""
        if self._module == _ipv4:
            return self in IP('224.0.0.0/4', self.version)
        elif  self._module == _ipv6:
            return self in IP('ff00::/8', self.version)

    def is_hostmask(self):
        """
        @return: C{True} if this address is a mask that would return a host
            id, C{False} otherwise.
        """
        int_val = self._value + 1
        return (int_val & (int_val - 1) == 0)

    def is_netmask(self):
        """
        @return: C{True} if this addr is a mask that would return a host id,
            C{False} otherwise.
        """
        int_val = (self._value ^ self._module.max_int) + 1
        return (int_val & (int_val - 1) == 0)

    def netmask_bits(self): #FIXME: replace this
        """
        @return: If this IP is a valid netmask, the number of non-zero
            bits are returned, otherwise it returns the width in bits for
            based on the IP address version, 32 for IPv4 and 128 for IPv6.
        """
        if not self.is_netmask():
            return self._module.width

        bits = self._module.int_to_bits(self._value)
        mask_bits = bits.translate(
            ''.join([chr(_) for _ in range(256)]), ':.0')
        mask_length = len(mask_bits)

        if not 0 <= mask_length <= self._module.width:
            raise ValueError('Unexpected mask length %d for address type!' \
                % mask_length)

        return mask_length

    def is_loopback(self):
        """
        @return: C{True} if this IP is loopback address (not for network
            transmission), C{False} otherwise.
            References: RFC 3330 and 4291.
        """
        if self.version == 4:
            return self in IP('127.0.0.0/8')
        elif  self.version == 6:
            return self == IP('::1')

    def is_private(self):
        """
        @return: C{True} if this IP is for internal/private use only
            (i.e. non-public), C{False} otherwise. Reference: RFCs 1918,
            3330, 4193, 3879 and 2365.
        """
        if self.version == 4:
            for cidr in (IP('192.168.0.0/16'), IP('10.0.0.0/8'),
                         IP('172.16.0.0/12'), IP('192.0.2.0/24'),
                         IP('239.192.0.0/14')):
                if self in cidr:
                    return True
        elif self.version == 6:
            #   Please Note: FEC0::/10 has been deprecated! See RFC 3879.
            return self in IP('fc00::/7') #   ULAs - Unique Local Addresses

        if self.is_link_local():
            return True

        return False

    def is_link_local(self):
        """
        @return: C{True} if this IP is link-local address C{False} otherwise.
            Reference: RFCs 3927 and 4291.
        """
        if self.version == 4:
            return self in IP('169.254.0.0/16')
        elif self.version == 6:
            return self in IP('fe80::/10')

    def is_reserved(self):
        """
        @return: C{True} if this IP is in IANA reserved range, C{False}
            otherwise. Reference: RFCs 3330 and 3171.
        """
        if self.version == 4:
            #   Use of ipglobs here would be much more concise than CIDRs...
            for cidr in (IP('240.0.0.0/4'), IP('234.0.0.0/7'),
                         IP('236.0.0.0/7'),
                         #  225-231.*.*.*
                         IP('225.0.0.0/8'), IP('226.0.0.0/7'),
                         IP('228.0.0.0/6'),
                         #  234-238.*.*.*
                         IP('234.0.0.0/7'), IP('236.0.0.0/7'),
                         IP('238.0.0.0/8')):
                if self in cidr:
                    return True
        if self.version == 6:
            for cidr in (IP('ff00::/12'),IP('::/8'), IP('0100::/8'),
                         IP('0200::/7'), IP('0400::/6'), IP('0800::/5'),
                         IP('1000::/4'), IP('4000::/3'), IP('6000::/3'),
                         IP('8000::/3'), IP('A000::/3'), IP('C000::/3'),
                         IP('E000::/4'), IP('F000::/5'), IP('F800::/6'),
                         IP('FE00::/9')):
                if self in cidr:
                    return True
        return False

    def is_ipv4_mapped(self):
        """
        @return: C{True} if this IP is IPv4-compatible IPv6 address, C{False}
            otherwise.
        """
        return self.version == 6 and (self._value >> 32) == 0xffff

    def is_ipv4_compat(self):
        """
        @return: C{True} if this IP is IPv4-mapped IPv6 address, C{False}
            otherwise.
        """
        return self.version == 6 and (self._value >> 32) == 0

    @property
    def ip(self):
        """
        The IP address of this IP object. This is not necessarily the same as
        the network address indicated by various CIDR prefixes or network
        masks.
        """
        return IP(self._value, self.version)

    @property
    def version(self):
        """the IP protocol version represented by this IP object."""
        return self._module.version

    @property
    def network(self):
        """The network address of this IP object."""
        return IP(self._value & int(self.netmask), self.version)

    @property
    def broadcast(self):
        """The broadcast address of this IP object"""
        return IP(self._value | self.hostmask._value, self.version)

    @property
    def first(self):
        """
        The integer value of first IP address in the CIDR block for this IP
        object.
        """
        return self._value & (self._module.max_int ^ self.hostmask._value)

    @property
    def last(self):
        """
        The integer value of last IP address in the CIDR block for this IP
        object.
        """
        hostmask = (1 << (self._module.width - self._prefixlen)) - 1
        return self._value | hostmask

    @property
    def netmask(self):
        """The subnet mask of this IP object."""
        return IP(self._module.max_int ^ self.hostmask._value, self.version)

    @property
    def hostmask(self):
        """The host mask of this IP object."""
        hostmask = (1 << (self._module.width - self._prefixlen)) - 1
        return IP(hostmask, self.version)

    @property
    def cidr(self):
        """
        The CIDR network address for this IP object. This excludes any host
        address bits that remain after applying the subnet prefix to the IP
        address of an IP object.
        """
        cidr = IP(self._value & int(self.netmask), self.version)
        cidr.prefixlen = self.prefixlen
        return cidr

    @property
    def size(self):
        """The number of IP addresses in this subnet."""
        return int(self.last - self.first + 1)

    def supernet(self, prefixlen=0):
        """
        Provides a list of supernet CIDR blocks for this IP object's subnet
        between the size of the current prefix and (if specified) and end
        prefix.

        @param prefixlen: (optional) a CIDR prefix for the maximum supernet.
            Default: 0 - returns all possible supernets.

        @return: an tuple containing IP object supernets containing this one.
        """
        if not 0 <= prefixlen <= self._module.width:
            raise ValueError('CIDR prefix /%d invalid for IPv%d!' \
                % (prefixlen, self.version))

        #   Use a copy of self as we'll be editing it.
        supernet = self.cidr

        supernets = []
        while supernet.prefixlen > prefixlen:
            supernet.prefixlen -= 1
            supernets.append(supernet.cidr)

        return list(reversed(supernets))

    def __iadd__(self, i):
        """
        Increases the value of this IP object by the current size * i.

        An IndexError is raised if result exceeds address range maximum.
        """
        new_first = int(self.network) + (self.size * i)

        if (new_first + (self.size - 1)) > self._module.max_int:
            raise IndexError('increment exceeds address boundary!')

        self._value = new_first
        return self

    def __isub__(self, i):
        """
        Decreases the value of this IP object by the current size * i.

        An IndexError is raised if result is less than zero.
        """
        new_first = int(self.network) - (self.size * i)

        if new_first < 0:
            raise IndexError('decrement is less than zero!')

        self._value = new_first
        return self

    def __getitem__(self, index):
        """
        @return: The IP address(es) in this address range referenced by
            index/slice. Slicing objects can produce large sequences so
            generator objects are returned instead of a list. Wrapping a slice
            with C{list()} or C{tuple()} may be required dependent on context
            in which it is called.
        """
        if hasattr(index, 'indices'):
            if self._module.version == 6:
                #FIXME: IPv6 breaks the .indices() method on the slice object
                #FIXME: spectacularly. We'll have to work out the start, stop
                #FIXME: and step ourselves :-(
                #FIXME: See PySlice_GetIndicesEx function in Python SVN
                #FIXME: repository for implementation details :-
                #http://svn.python.org/view/python/trunk/Objects/sliceobject.c
                raise TypeError('slices unsupported on IPv6 objects!')

            (start, stop, step) = index.indices(self.size)
            start_ip = IP(self.first + start, self.version)
            end_ip = IP(self.first + stop, self.version)
            return iter_iprange(start_ip, end_ip, step)
        else:
            try:
                index = int(index)
                if (- self.size) <= index < 0:
                    #   negative index.
                    return IP(self.last + index + 1, self.version)
                elif 0 <= index <= (self.size - 1):
                    #   Positive index or zero index.
                    return IP(self.first + index, self.version)
                else:
                    raise IndexError('index out range for address range size!')
            except ValueError:
                raise TypeError('unsupported index type %r!' % index)

    def __len__(self):
        """
        @return: The number of IP addresses in this subnet. Raises IndexError
            if size > sys.maxint (a Python limitation). Use the .size()
            property for subnets of any size.
        """
        size = self.size
        if size > _sys.maxint:
            #   Use .size() method in this class instead as len() will b0rk!
            raise IndexError("range contains greater than %d (sys.maxint)" \
                "addresses! Use the .size() method instead.")
        return size

    def __contains__(self, other):
        """
        @param other: an IP address (any format supported by IP.__init__).

        @return: C{True} if a given IP address/ranges falls within the
            boundary of this IP address/range, C{False} otherwise.
        """
        other = IP(other, self.version)
        return other.first >= self.first and other.last <= self.last

    def __iter__(self):
        """
        @return: An iterator object providing access to all network addresses
            within this range.
        """
        start_ip = IP(self.first, self.version)
        end_ip = IP(self.last+1, self.version)
        return iter_iprange(start_ip, end_ip)

    def __hash__(self):
        """
        @return: A hash value uniquely indentifying this IP object. It is
            based on the subnet of this IP object, *not* its IP address value.
        """
        return hash((self.version, self.first, self.last))

    def __eq__(self, other):
        """
        @param other: an IP address object of the same version as C{self}.

        @return: C{True} if the boundary of this IP's subnet match that
            of other, C{False} otherwise.
        """
        try:
            return (self.version,  self.first,  self.last) == \
                   (other.version, other.first, other.last)
        except AttributeError:
            return False

    def __ne__(self, other):
        """
        @param other: an IP address object of the same version as C{self}.

        @return: C{False} if the boundary of this IP's subnet match that
            of other, C{True} otherwise.
        """
        try:
            return (self.version,  self.first,  self.last) != \
                   (other.version, other.first, other.last)
        except AttributeError:
            return True

    def __lt__(self, other):
        """
        @param other: an IP address object of the same version as C{self}.

        @return: C{True} if the boundary of this IP's subnet are less than
            other, C{False} otherwise.
        """
        try:
            #   A sort key is essentially a CIDR prefixlen value.
            #   Required as IPRange (and subclasses other than CIDR) do not
            #   calculate it.
            self_sort_key = self._module.width - num_bits(self.size)
            other_sort_key = other._module.width - num_bits(other.size)
            return (self.version,  self.first,  self_sort_key) < \
                   (other.version, other.first, other_sort_key)
        except AttributeError:
            return False

    def __le__(self, other):
        """
        @param other: an IP address object of the same version as C{self}.

        @return: C{True} if the boundary of this IP's subnet are less than or
            equal to other, C{False} otherwise.
        """
        try:
            #   A sort key is essentially a CIDR prefixlen value.
            #   Required as IPRange (and subclasses other than CIDR) do not
            #   calculate it.
            self_sort_key = self._module.width - num_bits(self.size)
            other_sort_key = other._module.width - num_bits(other.size)
            return (self.version,  self.first,  self_sort_key) <= \
                   (other.version, other.first, other_sort_key)
        except AttributeError:
            return False

    def __gt__(self, other):
        """
        @param other: an IP address object of the same version as C{self}.

        @return: C{True} if the boundary of this IP's subnet are greater
            than other, C{False} otherwise.
        """
        try:
            #   A sort key is essentially a CIDR prefixlen value.
            #   Required as IPRange (and subclasses other than CIDR) do not
            #   calculate it.
            self_sort_key = self._module.width - num_bits(self.size)
            other_sort_key = other._module.width - num_bits(other.size)
            return (self.version,  self.first,  self_sort_key) > \
                   (other.version, other.first, other_sort_key)
        except AttributeError:
            return False

    def __ge__(self, other):
        """
        @param other: an IP address object of the same version as C{self}.

        @return: C{True} if the boundary of this IP's subnet are greater than
            or equal than other, C{False} otherwise.
        """
        try:
            #   A sort key is essentially a CIDR prefixlen value.
            #   Required as IPRange (and subclasses other than CIDR) do not
            #   calculate it.
            self_sort_key = self._module.width - num_bits(self.size)
            other_sort_key = other._module.width - num_bits(other.size)
            return (self.version,  self.first,  self_sort_key) >= \
                   (other.version, other.first, other_sort_key)
        except AttributeError:
            return False

    def __int__(self):
        """@return: value of this address as an unsigned integer"""
        return self._value

    def __long__(self):
        """@return: value of this address as an unsigned integer"""
        return self._value

    def __hex__(self):
        """@return: hexadecimal string representation of this IP address."""
        return hex(self._value).rstrip('L').lower()

    def __str__(self):
        """@return: IP address in representational format"""
        addr = self._module.int_to_str(self._value)
        if self.prefixlen != self._module.width:
            return "%s/%s" % (addr, self.prefixlen)
        return addr

    def __repr__(self):
        """@return: Python statement to create equivalent IP object"""
        return "IP('%s')" % self

    def bits(self, word_sep=None):
        """
        @param word_sep: (optional) the separator to insert between words.
            Default: None - use default separator for address type.

        @return: human-readable binary digit string of this address"""
        return self._module.int_to_bits(self._value, word_sep)

    def packed(self):
        """@return: binary packed string of this address"""
        return self._module.int_to_packed(self._value)

    def bin(self):
        """
        @return: standard Python binary representation of this address. A back
            port of the format provided by the builtin bin() type available in
            Python 2.6.x and higher."""
        return self._module.int_to_bin(self._value)

    def reverse_dns(self):
        """@return: The reverse DNS lookup string for this IP address"""
        return self._module.int_to_arpa(self._value)

    def ipv4(self):
        """
        @return: A new IPv4 address numerically equivalent to this one.
        An object copy is returned if this object is already IPv4. If
        this object is IPv6 and its value is compatible with IPv4, a new IPv4
        L{IP} object is returned.

        Raises an L{AddrConversionError} is IPv6 address cannot be converted.
        """
        ip = None

        if self.version == 4:
            ip = IP(self._value, 4)
            ip.prefixlen = self.prefixlen
        elif self.version == 6:
            if 0 <= self._value <= _ipv4.max_int:
                ip = IP(self._value, 4)
                ip.prefixlen = self.prefixlen - 96
            elif _ipv4.max_int <= self._value <= 0xffffffffffff:
                ip = IP(self._value - 0xffff00000000, 4)
                ip.prefixlen = self.prefixlen - 96
            else:
                raise AddrConversionError('IPv6 address %s unsuitable for ' \
                    'conversion to IPv4!' % self)
        return ip

    def ipv6(self, ipv4_compatible=False):
        """
        B{Please Note:} the IPv4-Mapped IPv6 address format is now considered
        deprecated. Reference: RFC 4291

        @param ipv4_compatible: If C{True} returns an IPv4-Mapped address
            (::ffff:x.x.x.x), an IPv4-Compatible (::x.x.x.x) address
            otherwise. Default: False (IPv4-Mapped).

        @return: A new L{IP} version 6 object that is numerically equivalent
            this address. If this object is already IPv6 then a copy of this
            object is returned. If this object is IPv4, a new version 6 L{IP}
            object is returned.
        """
        ip = None

        if self.version == 6:
            ip = IP(self._value, 6)
            ip.prefixlen = self.prefixlen
        elif self.version == 4:
            ip = IP(self._value, 6)
            if ipv4_compatible:
                #   IPv4-Compatible IPv6 address
                ip = IP(self._value, 6)
            else:
                #   IPv4-Mapped IPv6 address
                ip = IP(0xffff00000000 + self._value, 6)
            ip.prefixlen = self.prefixlen + 96

        return ip

    def previous(self, step=1):
        """
        @param step: the number of IP subnets between this IP object and the
            expected subnet. Default is 1 (the previous IP subnet).

        @return: The adjacent subnet that precedes this IP object.
        """
        ip_copy = IP('%s/%d' % (self.network, self.prefixlen), self.version)
        ip_copy -= step
        return ip_copy

    def next(self, step=1):
        """
        @param step: the number of IP subnets between this IP object and the
            expected subnet. Default is 1 (the next IP subnet).

        @return: The adjacent subnet that succeeds this IP object.
        """
        ip_copy = IP('%s/%d' % (self.network, self.prefixlen), self.version)
        ip_copy += step
        return ip_copy

    def subnet(self, prefixlen, count=None, fmt=None):
        """
        A generator divides up and returns smaller IP subnets of the current
        IP subnet based on a new smaller CIDR prefix (block size).

        @param prefixlen: a CIDR prefix indicate size of subnets to create.

        @param count: (optional) number of consecutive IP subnets to be
            returned.

        @return: an iterator (as lists could potentially be very large)
            containing IP subnets based on this IP object's subnet.
        """
        if not 0 <= self.prefixlen <= self._module.width:
            raise ValueError('CIDR prefix /%d invalid for IPv%d!' \
                % (prefixlen, self.version))

        if not self.prefixlen <= prefixlen:
            #   Don't return anything.
            raise StopIteration

        #   Calculate number of subnets to be returned.
        width = self._module.width
        max_subnets = 2 ** (width - self.prefixlen) / 2 ** (width - prefixlen)

        if count is None:
            count = max_subnets

        if not 1 <= count <= max_subnets:
            raise ValueError('count outside of current IP subnet boundary!')

        base_subnet = self._module.int_to_str(self.first)

        for i in xrange(count):
            subnet = IP('%s/%d' % (base_subnet, prefixlen), self.version)
            subnet.value += (subnet.size * i)
            subnet.prefixlen = prefixlen
            yield subnet

    def iter_hosts(self):
        """
        @return: An iterator that provides all IP addresses that can be
            assigned to hosts within the range of this IP object's subnet.
                - for IPv4, the network and broadcast addresses are always
                excluded from any yielded list. Therefore, any subnet that
                contains less than 4 IP addresses yields an empty list.
                - for IPv6, only the unspecified address '::' is excluded
                from any yielded IP addresses.
        """
        if self.version == 4:
            #   IPv4 logic.
            if self.size >= 4:
                return iter_iprange(IP(self.first+1, self.version),
                                    IP(self.last, self.version))
            else:
                return iter([])
        else:
            #   IPv6 logic.
            if self.first == 0:
                if self.size != 1:
                    #   Don't return '::'.
                    return iter_iprange(IP(self.first+1, self.version),
                                        IP(self.last+1, self.version))
                else:
                    return iter([])
            else:
                return iter(self)

    def info(self):
        """
        @return: A record dict containing IANA registration details for this
            IP address if available, None otherwise.
        """
        #   This import is placed here for efficiency. If you don't call this
        #   method, you don't take the (small), one time, import start up
        #   penalty.
        from netaddr.ip.iana import query
        return query(self)

#-----------------------------------------------------------------------------
def iter_iprange(start_ip, stop_ip, step=1):
    """
    An xrange work-alike generator for IP addresses. It produces sequences
    based on start and stop IP address values, in intervals of step size.

    @param start_ip: start IP address (any format supported by IP.__init__).

    @param stop_ip: end IP address (any format supported by IP.__init__).

    @param step: (optional) size of step between IP addresses.
        (Default: 1)

    @return: an iterator yielding one or more IP objects.
    """
    start_ip = IP(start_ip)
    stop_ip = IP(stop_ip)

    if start_ip.version != stop_ip.version:
        raise TypeError('start and stop IP versions do not match!')
    version = start_ip.version

    step = int(step)
    if step == 0:
        raise ValueError('step argument cannot be zero')

    #   We don't need objects from here, just integers.
    start = int(start_ip)
    stop = int(stop_ip)

    negative_step = False

    if step < 0:
        negative_step = True

    index = start - step
    while True:
        index += step
        if negative_step:
            if not index > stop:
                return
        else:
            if not index < stop:
                return
        yield IP(index, version)


#-----------------------------------------------------------------------------
def iter_unique_ips(*args):
    """
    @param args: A list of IP addresses and subnets passed in as arguments.

    @return: A generator that flattens out IP subnets, yielding unique
        individual IP addresses (no duplicates).
    """
    for cidr in cidr_merge(args):
        for ip in cidr:
            yield ip

#-----------------------------------------------------------------------------
def cidr_abbrev_to_verbose(abbrev_cidr):
    """
    A function that converts abbreviated IPv4 CIDRs to their more verbose
    equivalent.

    @param abbrev_cidr: an abbreviated CIDR.

    Uses the old-style classful IP address rules to decide on a default
    subnet prefix if one is not explicitly provided.

    Only supports IPv4 addresses.

    Examples ::

        10                  - 10.0.0.0/8
        10/16               - 10.0.0.0/16
        128                 - 128.0.0.0/16
        128/8               - 128.0.0.0/8
        192.168             - 192.168.0.0/16

    @return: A verbose CIDR from an abbreviated CIDR or old-style classful
    network address, The original value if it was not recognised as a
    supported abbreviation.
    """
    #   Internal function that returns a prefix value based on the old IPv4
    #   classful network scheme that has been superseded (almost) by CIDR.
    def classful_prefix(octet):
        octet = int(octet)
        if not 0 <= octet <= 255:
            raise IndexError('Invalid octet: %r!' % octet)
        if 0 <= octet <= 127:       #   Legacy class 'A' classification.
            return 8
        elif 128 <= octet <= 191:   #   Legacy class 'B' classification.
            return 16
        elif 192 <= octet <= 223:   #   Legacy class 'C' classification.
            return 24
        elif octet == 224:          #   Multicast address range.
            return 4
        elif 225 <= octet <= 239:   #   Reserved.
            return 8
        return 32                   #   Default.

    start = ''
    tokens = []
    prefix = None

    if isinstance(abbrev_cidr, (str, unicode)):
        if ':' in abbrev_cidr:
            return abbrev_cidr
    try:
        #   Single octet partial integer or string address.
        i = int(abbrev_cidr)
        tokens = [str(i), '0', '0', '0']
        return "%s%s/%s" % (start, '.'.join(tokens), classful_prefix(i))

    except ValueError:
        #   Multi octet partial string address with optional prefix.
        part_addr = abbrev_cidr
        tokens = []

        if part_addr == '':
            #   Not a recognisable format.
            return abbrev_cidr

        if '/' in part_addr:
            (part_addr, prefix) = part_addr.split('/', 1)

        #   Check prefix for validity.
        if prefix is not None:
            try:
                if not 0 <= int(prefix) <= 32:
                    return abbrev_cidr
            except ValueError:
                return abbrev_cidr

        if '.' in part_addr:
            tokens = part_addr.split('.')
        else:
            tokens = [part_addr]

        if 1 <= len(tokens) < 4:
            for i in range(4 - len(tokens)):
                tokens.append('0')
        elif len(tokens) == 4:
            if prefix is None:
                #   Non-partial addresses without a prefix.
                prefix = 32
        else:
            #   Not a recognisable format.
            return abbrev_cidr

        if prefix is None:
            try:
                prefix = classful_prefix(tokens[0])
            except ValueError:
                return abbrev_cidr

        return "%s%s/%s" % (start, '.'.join(tokens), prefix)

    except TypeError:
        pass
    except IndexError:
        pass

    #   Not a recognisable format.
    return abbrev_cidr

#-----------------------------------------------------------------------------
def cidr_merge(ip_addrs):
    """
    A function that accepts an iterable sequence of IP addresses and subnets
    returning the smallest possible list of the largest possible IP addresses
    and subnets.

    It does this by merging any adjacent subnets where possible and
    removing any addresses or subnets contained within those found in the list
    after any merges have taken place.

    @param ip_addrs: an iterable sequence of IP addresses and subnets.

    @return: a summarized list of IP objects.
    """
    if not hasattr(ip_addrs, '__iter__'):
        raise ValueError('A sequence or iterable is expected!')

    #   Start off using set as we'll remove any duplicates at the start.
    ipv4_bit_cidrs = set()
    ipv6_bit_cidrs = set()

    #   Convert IP addresses and subnets into their CIDR bit strings.
    for ip in ip_addrs:
        cidr = IP(ip)
        bits = cidr.network.bits(word_sep='')[0:cidr.prefixlen]

        if cidr.version == 4:
            ipv4_bit_cidrs.add(bits)
        else:
            ipv6_bit_cidrs.add(bits)

    #   Merge binary CIDR addresses where possible.
    def _reduce_bit_cidrs(cidrs):
        new_cidrs = []

        cidrs.sort()

        #   Multiple passes are required to obtain precise results.
        while 1:
            finished = True
            while len(cidrs) > 0:
                if len(new_cidrs) == 0:
                    new_cidrs.append(cidrs.pop(0))
                if len(cidrs) == 0:
                    break
                #   lhs and rhs are same size and adjacent.
                (new_cidr, subs) = _re.subn(r'^([01]+)0 \1[1]$',
                    r'\1', '%s %s' % (new_cidrs[-1], cidrs[0]))
                if subs:
                    #   merge lhs with rhs.
                    new_cidrs[-1] = new_cidr
                    cidrs.pop(0)
                    finished = False
                else:
                    #   lhs contains rhs.
                    (new_cidr, subs) = _re.subn(r'^([01]+) \1[10]+$',
                        r'\1', '%s %s' % (new_cidrs[-1], cidrs[0]))
                    if subs:
                        #   keep lhs, discard rhs.
                        new_cidrs[-1] = new_cidr
                        cidrs.pop(0)
                        finished = False
                    else:
                        #   no matches - accept rhs.
                        new_cidrs.append(cidrs.pop(0))
            if finished:
                break
            else:
                #   still seeing matches, reset.
                cidrs = new_cidrs
                new_cidrs = []

        return new_cidrs

    new_cidrs = []

    def _bits_to_cidr(bits, module):
        if _re.match('^[01]+$', bits) is None:
            raise ValueError('%r is an invalid bit string!' % bits)

        num_bits = len(bits)

        if bits == '':
            return IP(module.int_to_str(0), module.version)
        else:
            bits = bits + '0' * (module.width - num_bits)
            ip = module.int_to_str(module.bits_to_int(bits))
            return IP('%s/%d' % (ip, num_bits), module.version)

    #   Reduce and format lists of reduced CIDRs.
    for bits in _reduce_bit_cidrs(list(ipv4_bit_cidrs)):
            new_cidrs.append(_bits_to_cidr(bits, _ipv4))

    for bits in _reduce_bit_cidrs(list(ipv6_bit_cidrs)):
            new_cidrs.append(_bits_to_cidr(bits, _ipv6))

    return new_cidrs

#-----------------------------------------------------------------------------
def cidr_exclude(target, exclude):
    """
    Removes an exclude IP object from a target IP object.

    @param target: the target IP object.

    @param exclude: the IP object to be removed from target.

    @return: list of remaining IP objects after exclusion has been performed.
    """
    cidrs = []

    target = IP(target)
    exclude = IP(exclude)

    if exclude.last < target.first:
        #   Exclude subnet's upper bound address less than target
        #   subnet's lower bound.
        return [target.cidr]
    elif target.last < exclude.first:
        #   Exclude subnet's lower bound address greater than target
        #   subnet's upper bound.
        return [target.cidr]

    new_prefixlen = target.prefixlen + 1

    if new_prefixlen <= target._module.width:
        i_lower = target.first
        i_upper = target.first + (2 ** (target._module.width - new_prefixlen))

        lower = IP('%s/%d' % (target._module.int_to_str(i_lower),
            new_prefixlen))
        upper = IP('%s/%d' % (target._module.int_to_str(i_upper),
            new_prefixlen))

        while exclude.prefixlen >= new_prefixlen:
            if exclude in lower:
                matched = i_lower
                unmatched = i_upper
            elif exclude in upper:
                matched = i_upper
                unmatched = i_lower
            else:
                #   Exclude subnet not within target subnet.
                cidrs.append(target.cidr)
                break

            ip = IP('%s/%d' % (target._module.int_to_str(unmatched),
                new_prefixlen))

            cidrs.append(ip)

            new_prefixlen += 1

            if new_prefixlen > target._module.width:
                break

            i_lower = matched
            i_upper = matched + (2 ** (target._module.width - new_prefixlen))

            lower = IP('%s/%d' % (target._module.int_to_str(i_lower),
                new_prefixlen))
            upper = IP('%s/%d' % (target._module.int_to_str(i_upper),
                new_prefixlen))

    cidrs.sort()

    return cidrs

#-----------------------------------------------------------------------------
def spanning_cidr(ip_addrs):
    """
    Function that accepts a sequence of IP addresses and subnets returning
    a single (CIDR) subnet that is large enough to span the lower and upper
    bound IPs with a possible overlap on either end.

    @param ip_addrs: sequence of IP addresses and subnets.

    @return: a single spanning IP subnet.
    """
    sorted_ips = sorted([IP(ip) for ip in ip_addrs])

    if not len(sorted_ips) > 1:
        raise ValueError('IP sequence must contain at least 2 elements!')

    lowest_ip = sorted_ips[0]
    highest_ip = sorted_ips[-1]

    if lowest_ip.version != highest_ip.version:
        raise TypeError('IP sequence cannot contain both IPv4 and IPv6!')

    ip = highest_ip.cidr

    while ip.prefixlen > 0:
        if highest_ip in ip and lowest_ip not in ip:
            ip.prefixlen -= 1
        else:
            break

    return ip.cidr

#-----------------------------------------------------------------------------
def iprange_to_cidrs(start, end):
    """
    A function that accepts an arbitrary start and end IP address or subnet
    and returns a list of CIDR subnets that fit exactly between the boundaries
    of the two with no overlap.

    @param start: the start IP address or subnet.

    @param end: the end IP address or subnet.

    @return: a list of one or more IP addresses and subnets.
    """
    cidr_list = []

    start = IP(start)
    end = IP(end)

    iprange = [start.first, end.last]

    #   Get spanning CIDR covering both addresses.
    cidr_span = spanning_cidr([start, end])

    if cidr_span.first == iprange[0] and cidr_span.last == iprange[-1]:
        #   Spanning CIDR matches start and end exactly.
        cidr_list = [cidr_span]
    elif cidr_span.last == iprange[-1]:
        #   Spanning CIDR matches end exactly.
        ip = IP(start)
        first_int_val = int(ip)
        ip -= 1
        cidr_remainder = cidr_exclude(cidr_span, ip)

        first_found = False
        for cidr in cidr_remainder:
            if cidr.first == first_int_val:
                first_found = True
            if first_found:
                cidr_list.append(cidr)
    elif cidr_span.first == iprange[0]:
        #   Spanning CIDR matches start exactly.
        ip = IP(end)
        last_int_val = int(ip)
        ip += 1
        cidr_remainder = cidr_exclude(cidr_span, ip)

        last_found = False
        for cidr in cidr_remainder:
            cidr_list.append(cidr)
            if cidr.last == last_int_val:
                break
    elif cidr_span.first <= iprange[0] and cidr_span.last >= iprange[-1]:
        #   Spanning CIDR overlaps start and end.
        ip = IP(start)
        first_int_val = int(ip)
        ip -= 1
        cidr_remainder = cidr_exclude(cidr_span, ip)

        #   Fix start.
        first_found = False
        for cidr in cidr_remainder:
            if cidr.first == first_int_val:
                first_found = True
            if first_found:
                cidr_list.append(cidr)

        #   Fix end.
        ip = IP(end)
        last_int_val = int(ip)
        ip += 1
        cidr_remainder = cidr_exclude(cidr_list.pop(), ip)

        last_found = False
        for cidr in cidr_remainder:
            cidr_list.append(cidr)
            if cidr.last == last_int_val:
                break

    return cidr_list

#-----------------------------------------------------------------------------
def within_iprange(ip, start, end):
    """
    A function that accepts two arbitrary IP addresses that form a boundary
    IP range and a target IP object. It checks to see if the IP object falls
    within the boundary of start and end addresses.

    @param ip: an IP object to be tested against IP range.

    @param start: the start IP address or subnet.

    @param end: the end IP address or subnet.

    @return: True if ip falls with the bounds of iprange, False otherwise.
    """
    ip = IP(ip)
    start = IP(start)
    end = IP(end)

    if start.last > end.first:
        raise ValueError('bad IP range, start IP is greater than end IP!')

    if start.first <= ip.value <= end.last:
        return True

    return False

#-----------------------------------------------------------------------------
def cidr_gaps(cidrs, supernet=None):
    """
    A function that accepts a list of CIDR subnets and IP addresses detecting
    and returning the gaps between each one.

    @param cidrs: A sequence CIDR subnets or IP addresses.

    @param supernet: An optional supernet CIDR. If it contains all IPs and
        CIDRs in cidrs suquence, it will return any gaps on either side as
        well.

    @return: A list of cidrs that fill the gaps between each CIDR subnet
        and or IP address.
    """
    raise NotImplementedError('TODO')
