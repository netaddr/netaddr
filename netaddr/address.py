#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network address classes (IP, EUI) and associated aggregate classes (CIDR,
Wildcard and IPRange).
"""
import math as _math
import socket as _socket
import re as _re

from netaddr import AddrFormatError, AddrConversionError, AT_UNSPEC, \
    AT_INET, AT_INET6, AT_LINK, AT_EUI64, AT_NAMES

from netaddr.strategy import ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64, \
    AddrStrategy

from netaddr.eui import OUI, IAB

from netaddr.util import num_bits

#: Address type to strategy object lookup dict.
AT_STRATEGIES = {
    AT_UNSPEC   : None,
    AT_INET     : ST_IPV4,
    AT_INET6    : ST_IPV6,
    AT_LINK     : ST_EUI48,
    AT_EUI64    : ST_EUI64,
}

#-----------------------------------------------------------------------------
class AddrTypeDescriptor(object):
    """
    A descriptor that checks addr_type property assignments for validity and
    also keeps the strategy property in sync with any changes made.
    """
    def __init__(self, addr_types):
        """
        Constructor.

        @param addr_types: a list of address types constants that are
        acceptable for assignment to the addr_type property.
        """
        self.addr_types = addr_types

    def __set__(self, instance, value):
        if value not in self.addr_types:
            raise ValueError('addr_type %r is invalid for objects of ' \
                'the %s() class!' % (value, instance.__class__.__name__))
        instance.__dict__['addr_type'] = value
        instance.__dict__['strategy'] = AT_STRATEGIES[value]

#-----------------------------------------------------------------------------
class AddrValueDescriptor(object):
    """
    A descriptor that checks assignments to the named parameter passed to the
    constructor.

    It accepts network addresses in either strings format or as unsigned
    integers. String based addresses are converted to their integer
    equivalents before assignment to the named parameter. Also ensures that
    addr_type and strategy are set correctly when parsing string based
    addresses.
    """
    def __init__(self, name):
        """
        Descriptor constructor.

        @param name: the name of attribute which will be assigned the value.
        """
        self.name = name

    def __set__(self, instance, value):
        if issubclass(value.__class__, Addr):
            if instance.strategy is None:
                instance.strategy = value.strategy
            value = int(value)
        else:
            if instance.addr_type == AT_UNSPEC:
                #   Select a strategy object for this address.
                for strategy in instance.__class__.STRATEGIES:
                    if strategy.valid_str(value):
                        instance.strategy = strategy
                        break

            #   Make sure we picked up a strategy object.
            if instance.strategy is None:
                raise AddrFormatError('%r is not a supported address ' \
                    'format!' % value)

            if isinstance(value, (str, unicode)):
                #   Calculate the integer value for this address.
                value = instance.strategy.str_to_int(value)
            elif isinstance(value, (int, long)):
                if not instance.strategy.valid_int(value):
                    raise OverflowError('value %r cannot be represented ' \
                        'in %d bit(s)!' % (value, instance.strategy.width))
            else:
                raise AddrFormatError('%r is an unsupported type!' % value)

        instance.__dict__[self.name] = value

#-----------------------------------------------------------------------------
class StrategyDescriptor(object):
    """
    A descriptor that checks strategy property assignments for validity and
    also keeps the addr_type property in sync with any changes made.
    """
    def __init__(self, strategies):
        """
        Constructor.

        @param strategies: a list of strategy objects that are acceptable for
            assignment to the strategy property.
        """
        self.strategies = strategies

    def __set__(self, instance, value):
        if value not in self.strategies:
            raise Exception('%r is not a supported strategy!' % value)
        instance.__dict__['strategy'] = value
        instance.__dict__['addr_type'] = instance.strategy.addr_type

#-----------------------------------------------------------------------------
class PrefixLenDescriptor(object):
    """
    A descriptor that checks prefixlen property assignments for validity based
    on address type. Also accepts netmasks and hostmasks which can easily be
    converted to the equivalent prefixlen integer.
    """
    def __init__(self, class_id=None):
        """
        Constructor.

        @param class_id: (optional) the name of the class that uses this
            descriptor.
        """
        self.class_id = class_id

    def __set__(self, instance, value):
        try:
            #   Basic integer subnet prefix.
            prefixlen = int(value)
        except ValueError:
            #   Convert possible subnet mask to integer subnet prefix.
            ip = IP(value)

            if instance.addr_type != ip.addr_type:
                raise ValueError('address and netmask type mismatch!')

            if ip.is_netmask():
                #   prefixlen is a netmask address.
                prefixlen = ip.netmask_bits()
            elif ip.is_hostmask():
                #   prefixlen is an ACL (hostmask) address.
                netmask = IP(ip.strategy.max_int ^ int(ip), ip.addr_type)
                prefixlen = netmask.netmask_bits()
            else:
                raise ValueError('%s is not a valid netmask/hostmask!' % ip)

        #   Validate subnet prefix.
        if not 0 <= prefixlen <= instance.strategy.width:
            raise ValueError('%d is an invalid prefix for an %s CIDR!' \
                % (prefixlen, AT_NAMES[instance.addr_type]))

        #   Make sure instance is not a subnet mask trying to set a prefix!
        if isinstance(instance, IP):
            if instance.is_netmask() and instance.addr_type == AT_INET \
               and prefixlen != 32 and instance.value != 0:
                raise ValueError('IPv4 netmasks must have a prefix of /32!')

        instance.__dict__['prefixlen'] = prefixlen

        #   Don't run this on a CIDR that is initialising itself.
        if self.class_id == 'CIDR' and 'first' in instance.__dict__:
            first = instance.__dict__['first']
            strategy = instance.__dict__['strategy']
            hostmask = (1 << (strategy.width - prefixlen)) - 1
            instance.__dict__['first'] = (first | hostmask) - hostmask
            instance.__dict__['last'] = first | hostmask

#-----------------------------------------------------------------------------
class FormatDescriptor(object):
    """
    A descriptor that checks formatter property assignments for validity.
    """
    def __init__(self, default):
        """
        Constructor.

        @param default: the default callable to use if the formatter
            property is None.
        """
        self.default = default

    def __set__(self, instance, value):
        if callable(value) and \
            value in (str, int, Addr, IP, long, unicode, hex):
            pass
        elif value is None:
            #   Use default.
            value = self.default
        else:
            raise TypeError("unsupported formatter callable: %r!" % value)

        instance.__dict__['fmt'] = value

#-----------------------------------------------------------------------------
class Addr(object):
    """
    The base class containing common functionality for all subclasses
    representing various network address types.

    It is a fully functioning class (as opposed to a virtual class) with a
    heuristic constructor that detects the type of address via the first
    argument if it is a string and sets itself up accordingly. If the first
    argument is an integer, then a constant must be provided via the second
    argument indicating the address type explicitly.

    Objects of this class behave differently dependent upon the type of address
    they represent.
    """
    STRATEGIES = (ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_UNSPEC, AT_INET, AT_INET6, AT_LINK, AT_EUI64)

    #   Descriptor registrations.
    value = AddrValueDescriptor('value')
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)

    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: the string form of a network address, or a network byte
            order integer within the supported range for the address type.

        @param addr_type: (optional) the network address type. If addr is an
            integer, this argument becomes mandatory.
        """
        self.addr_type = addr_type
        self.value = addr

    def __hash__(self):
        """@return: hash of this address suitable for dict keys, sets etc"""
        return hash((self.value, self.addr_type))

    def __int__(self):
        """@return: value of this address as an unsigned integer"""
        return self.value

    def __long__(self):
        """@return: value of this address as an unsigned integer"""
        return self.value

    def __str__(self):
        """@return: common string representation of this address"""
        return self.strategy.int_to_str(self.value)

    def __repr__(self):
        """@return: executable Python string to recreate equivalent object"""
        return "%s(%r)" % (self.__class__.__name__, str(self))

    def bits(self, word_sep=None):
        """
        @param word_sep: (optional) the separator to insert between words.
            Default: None - use default separator for address type.

        @return: human-readable binary digit string of this address"""
        return self.strategy.int_to_bits(self.value, word_sep)

    def packed(self):
        """@return: binary packed string of this address"""
        return self.strategy.int_to_packed(self.value)

    def bin(self):
        """
        @return: standard Python binary representation of this address. A back
            port of the format provided by the builtin bin() type available in
            Python 2.6.x and higher."""
        return self.strategy.int_to_bin(self.value)

    def __len__(self):
        """@return: The size (width) of this address in bits"""
        return self.strategy.width

    def __iter__(self):
        """@return: An iterator over individual words in this address"""
        return iter(self.strategy.int_to_words(self.value))

    def __getitem__(self, index):
        """
        @return: The integer value of the word referenced by index (both
            positive and negative). Raises C{IndexError} if index is out
            of bounds. Also supports Python list slices for accessing
            word groups.
        """
        if isinstance(index, (int, long)):
            #   Indexing, including negative indexing goodness.
            num_words = self.strategy.num_words
            if not (-num_words) <= index <= (num_words - 1):
                raise IndexError('index out range for address type!')
            return self.strategy.int_to_words(self.value)[index]
        elif isinstance(index, slice):
            #   Slicing baby!
            words = self.strategy.int_to_words(self.value)
            return [words[i] for i in range(*index.indices(len(words)))]
        else:
            raise TypeError('unsupported type %r!' % index)

    def __setitem__(self, index, value):
        """Sets the value of the word referenced by index in this address"""
        if isinstance(index, slice):
            #   TODO - settable slices.
            raise NotImplementedError('settable slices not yet supported!')

        if not isinstance(index, (int, long)):
            raise TypeError('index not an integer!')

        if not 0 <= index <= (self.strategy.num_words - 1):
            raise IndexError('index %d outside address type boundary!' % index)

        if not isinstance(value, (int, long)):
            raise TypeError('value not an integer!')

        if not 0 <= value <= self.strategy.max_word:
            raise IndexError('value %d outside word size maximum of %d bits!'
                % (value, self.strategy.word_size))

        words = list(self.strategy.int_to_words(self.value))
        words[index] = value
        self.value = self.strategy.words_to_int(words)

    def __hex__(self):
        """
        @return: hexadecimal string representation of this address (in network
        byte order).
        """
        return hex(self.value).rstrip('L').lower()

    def __iadd__(self, num):
        """
        Increment value of network address by specified amount. Behaves like
        an unsigned integer, rolling over to zero when it reaches the maximum
        value threshold.

        @param num: size of increment
        """
        try:
            new_value = self.value + num
            if new_value > self.strategy.max_int:
                self.value = new_value - (self.strategy.max_int + 1)
            else:
                self.value = new_value
        except TypeError:
            raise TypeError('Increment value must be an integer!')
        return self

    def __isub__(self, num):
        """
        Decrement value of network address by specified amount. Behaves like
        an unsigned integer, rolling over to maximum value when it goes below
        zero.

        @param num: size of decrement
        """
        try:
            new_value = self.value - num
            if new_value < 0:
                self.value = new_value + (self.strategy.max_int + 1)
            else:
                self.value = new_value
        except TypeError:
            raise TypeError('Decrement value must be an integer!')
        return self

    def __add__(self, other):
        """
        @param other: an integer or int-like object.

        @return: A new (potentially larger) Addr class/subclass instance.
        """
        return self.__class__(self.value + int(other), self.addr_type)

    def __sub__(self, other):
        """
        @param other: an integer or int-like object.

        @return: A new (potentially smaller) Addr class/subclass instance.
        """
        return self.__class__(self.value - int(other), self.addr_type)

    def __eq__(self, other):
        """
        @return: C{True} if this address is numerically the same as other,
            C{False} otherwise.
        """
        try:
            return (self.addr_type, self.value) == (other.addr_type,
                other.value)
        except AttributeError:
            return False

    def __ne__(self, other):
        """
        @return: C{False} if this address is numerically the same as the
            other, C{True} otherwise.
        """
        try:
            return (self.addr_type, self.value) != (other.addr_type,
                other.value)
        except AttributeError:
            return True

    def __lt__(self, other):
        """
        @return: C{True} if this address is numerically lower in value than
            other, C{False} otherwise.
        """
        try:
            return (self.addr_type, self.value) < (other.addr_type,
                other.value)
        except AttributeError:
            return False

    def __le__(self, other):
        """
        @return: C{True} if this address is numerically lower or equal in
            value to other, C{False} otherwise.
        """
        try:
            return (self.addr_type, self.value) <= (other.addr_type,
                other.value)
        except AttributeError:
            return False

    def __gt__(self, other):
        """
        @return: C{True} if this address is numerically greater in value than
            other, C{False} otherwise.
        """
        try:
            return (self.addr_type, self.value) > (other.addr_type,
                other.value)
        except AttributeError:
            return False

    def __ge__(self, other):
        """
        @return: C{True} if this address is numerically greater or equal in
            value to other, C{False} otherwise.
        """
        try:
            return (self.addr_type, self.value) >= (other.addr_type,
                other.value)
        except AttributeError:
            return False

    def __or__(self, other):
        """
        @param other: an integer or int-like object.

        @return: bitwise OR (x | y) of self.value with other.value.
        """
        return self.__class__(self.value | other.value, self.addr_type)

    def __and__(self, other):
        """
        @param other: an integer or int-like object.

        @return: bitwise AND (x & y) of self.value with other.value.
        """
        return self.__class__(self.value | other.value, self.addr_type)

    def __xor__(self, other):
        """
        @param other: an integer or int-like object.

        @return: bitwise exclusive OR (x ^ y) of self.value with other.value.
        """
        return self.__class__(self.value ^ other.value, self.addr_type)

    def __lshift__(self, numbits):
        """
        @param numbits: size of shift (in bits).

        @return: integer value of this IP address shifted left by x bits.
        """
        return self.__class__(self.value << numbits, self.addr_type)

    def __rshift__(self, numbits):
        """
        @param numbits: size of shift (in bits).

        @return: integer value of this IP address right shifted by x bits.
        """
        return self.__class__(self.value >> numbits, self.addr_type)

    def __invert__(self, other):
        """
        @param other: an integer or int-like object.

        @return: inversion (~x) of self.value.
        """
        return self.__class__(~self.value)

#-----------------------------------------------------------------------------
class EUI(Addr):
    """
    Represents an IEEE EUI (Extended Unique Identifier) indentifier.

    Input parser is flexible, supporting EUI-48 (including the many Media
    Access Control variants) and EUI-64.
    """
    STRATEGIES = (ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_UNSPEC, AT_LINK, AT_EUI64)

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)

    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: an EUI-48 (MAC) or EUI-64 address in string format or as
            an unsigned integer.

        @param addr_type: (optional) the specific EUI address type (C{AT_LINK}
            or C{AT_EUI64}).  This argument is used mainly to differentiate
            EUI48 and EUI48 identifiers that may be numerically equivalent.
        """
        #   Choose a sensible default when addr is an integer and addr_type is
        #   not specified.
        if addr_type == AT_UNSPEC:
            if 0 <= addr <= 0xffffffffffff:
                addr_type = AT_LINK
            elif 0xffffffffffff < addr <= 0xffffffffffffffff:
                addr_type = AT_EUI64

        super(EUI, self).__init__(addr, addr_type)

    def oui(self, fmt=OUI):
        """
        @param fmt: callable used on return values. Default: L{OUI} object.
            Also Supports str(), unicode(), int() and long().

        @return: The OUI (Organisationally Unique Identifier) for this EUI.
        """
        if callable(fmt) and fmt in (OUI, int, long):
            return fmt(self.value >> 24)
        elif callable(fmt) and fmt in (str, unicode, None):
            return '-'.join(["%02x" % i for i in self[0:3]]).upper()
        else:
            raise TypeError("unsupported formatter callable: %r!" % fmt)

    def ei(self):
        """@return: The EI (Extension Identifier) for this EUI"""
        if self.strategy == ST_EUI48:
            return '-'.join(["%02x" % i for i in self[3:6]]).upper()
        elif self.strategy == ST_EUI64:
            return '-'.join(["%02x" % i for i in self[3:8]]).upper()

    def isiab(self):
        """@return: True if this EUI is an IAB address, False otherwise"""
        return 0x50c2000 <= (self.value >> 12) <= 0x50c2fff

    def iab(self, fmt=IAB):
        """
        @param fmt: callable used on return values. Default: L{IAB} object.
            Also Supports str(), unicode(), int() and long().

        @return: If isiab() is True, the IAB (Individual Address Block)
            is returned, None otherwise.
        """
        if self.isiab():
            if callable(fmt) and fmt in (IAB, int, long):
                return fmt(self.value >> 12)
            elif callable(fmt) and fmt in (str, unicode, None):
                usermask = (1 << (self.strategy.width - 36)) - 1
                last_eui = self.value | usermask
                first_eui = last_eui - usermask
                iab_words = self.strategy.int_to_words(first_eui)
                return '-'.join(["%02x" % i for i in iab_words]).upper()
            else:
                raise TypeError("unsupported formatter callable: %r!" % fmt)

    def eui64(self):
        """
        @return: The value of this EUI object as a new 64-bit EUI object.
            - If this object represents an EUI-48 it is converted to EUI-64
                as per the standard.
            - If this object is already and EUI-64, it just returns a new,
                numerically equivalent object is returned instead.
        """
        if self.addr_type == AT_LINK:
            eui64_words = ["%02x" % i for i in self[0:3]] + ['ff', 'fe'] + \
                     ["%02x" % i for i in self[3:6]]

            return self.__class__('-'.join(eui64_words))
        else:
            return EUI(str(self))

    def ipv6_link_local(self):
        """
        @return: new link local IPv6 L{IP} object based on this L{EUI} using
            technique described in RFC 4291. B{Please Note:} this technique
            poses security risks in certain scenarios. Please read RFC 4941 for
            details. Reference: RFCs 4291 and 4941.
        """
        prefix = 'fe80:0000:0000:0000:'

        #   Add 2 to the first octet of this EUI address (temporarily).
        self[0] += 2

        if self.addr_type == AT_LINK:
            #   Modify MAC to make it an EUI-64.
            suffix = ["%02x" % i for i in self[0:3]] + ['ff', 'fe'] + \
                     ["%02x" % i for i in self[3:6]]
        else:
            suffix = ["%02x" % i for i in list(self)]

        suffix = ["%02x%02x" % (int(x[0], 16), int(x[1], 16)) for x in \
            zip(suffix[::2], suffix[1::2])]

        #   Subtract 2 again to return EUI to its original value.
        self[0] -= 2

        eui64 = ':'.join(suffix)
        addr = prefix + eui64 + '/64'
        return IP(addr)

    def info(self):
        """
        @return: A record dict containing IEEE registration details for this
            EUI (MAC-48) if available, None otherwise.
        """
        data = {'OUI': self.oui().registration()}
        if self.isiab():
            data['IAB'] = self.iab().registration()
        return data

#-----------------------------------------------------------------------------
class IP(Addr):
    """
    Represents B{individual} IPv4 and IPv6 addresses.

    B{Please Note:} this class is intended to provide low-level functionality
    to individual IP addresses such as octet/hextet access, integer/hex/binary
    conversions, etc. If you are coming from other libraries you may expect to
    find much higher level networking operations here. While the inclusion of
    a bitmask prefix or netmask to indicate subnet membership is permitted by
    the class constructor they are provided only as a convenience to the user.

    All higher level subnet and network operations can be found in objects of
    classes L{CIDR}, L{IPRange} and L{Wildcard}. There are handy helper methods
    here, (C{.cidr()}, C{.iprange()} and C{.wildcard()}) that return pre-initialised
    objects of those classes without you having to call them explicitly.

    Example usage ::

        >>> ip = IP('10.0.0.1')
        >>> list(ip) == [10, 0, 0, 1]
        True
        >>> ip += 1
        >>> str(ip) == '10.0.0.2'
        True

        >>> IP('10.0.0.0/28').iprange()
        IPRange('10.0.0.0', '10.0.0.15')

        >>> IP('10.0.0.64/24').cidr()
        CIDR('10.0.0.0/24')

        >>> IP('192.168.0.1/255.255.253.0').wildcard()
        Wildcard('192.168.0-1.*')

        >>> ipv6 = IP('fe80::20f:1fff:fe12:e733')
        >>> ipv6[0:4]
        [65152, 0, 0, 0]

        >>> IP('fe80::20f:1fff:fe12:e733/64').cidr()
        CIDR('fe80::/64')

    See those classes for details on the functionality they provide.
    """
    STRATEGIES = (ST_IPV4, ST_IPV6)
    ADDR_TYPES = (AT_UNSPEC, AT_INET, AT_INET6)
    TRANSLATE_STR = ''.join([chr(_) for _ in range(256)]) #FIXME: replace this

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)
    prefixlen = PrefixLenDescriptor()

    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: an IPv4 or IPv6 address string with an optional subnet
            prefix or an unsigned integer.

        @param addr_type: (optional) the IP address type (C{AT_INET} or
            C{AT_INET6}). This argument is used mainly to differentiate IPv4
            and IPv6 addresses that may be numerically equivalent.
        """
        prefixlen = None
        #   Check for prefix in address and split it out.
        try:
            if '/' in addr:
                (addr, prefixlen) = addr.split('/', 1)
        except TypeError:
            #   addr is an int - let it pass through.
            pass

        #   Choose a sensible default when addr is an integer and addr_type is
        #   not specified.
        if addr_type == AT_UNSPEC:
            if 0 <= addr <= 0xffffffff:
                addr_type = AT_INET
            elif 0xffffffff < addr <= 0xffffffffffffffffffffffffffffffff:
                addr_type = AT_INET6

        #   Call superclass constructor before processing subnet prefix to
        #   assign the strategyn object.
        super(IP, self).__init__(addr, addr_type)

        #   Set the subnet prefix.
        if prefixlen is None:
            self.__dict__['prefixlen'] = self.strategy.width
        else:
            self.prefixlen = prefixlen

    def is_netmask(self):
        """
        @return: C{True} if this addr is a mask that would return a host id,
            C{False} otherwise.
        """
        int_val = (self.value ^ self.strategy.max_int) + 1
        return (int_val & (int_val - 1) == 0)

    def netmask_bits(self): #FIXME: replace this
        """
        @return: If this address is a valid netmask, the number of non-zero
            bits are returned, otherwise it returns the width in bits for
            based on the version, 32 for IPv4 and 128 for IPv6.
        """
        if not self.is_netmask():
            return self.strategy.width

        bits = self.strategy.int_to_bits(self.value)
        mask_bits = bits.translate(IP.TRANSLATE_STR, ':.0')
        mask_length = len(mask_bits)

        if not 1 <= mask_length <= self.strategy.width:
            raise ValueError('Unexpected mask length %d for address type!' \
                % mask_length)

        return mask_length

    def reverse_dns(self):
        """@return: The reverse DNS lookup string for this IP address"""
        return self.strategy.int_to_arpa(self.value)

    def is_hostmask(self):
        """
        @return: C{True} if this address is a mask that would return a host
            id, C{False} otherwise.
        """
        int_val = self.value + 1
        return (int_val & (int_val-1) == 0)

    def hostname(self):
        """
        @return: Returns the FQDN for this IP address via a DNS query
            using gethostbyaddr() Python's socket module.
        """
        try:
            return _socket.gethostbyaddr(str(self))[0]
        except:
            return

    def cidr(self, strict=True):
        """
        @param strict: (optional) If True and non-zero bits are found to the
            right of the subnet mask/prefix a ValueError is raised. If False,
            CIDR returned has these bits automatically truncated.
            (default: True)

        @return: A L{CIDR} object based on this IP address
        """
        hostmask = (1 << (self.strategy.width - self.prefixlen)) - 1
        start = (self.value | hostmask) - hostmask
        network = self.strategy.int_to_str(start)
        return CIDR("%s/%d" % (network, self.prefixlen), strict=strict)

    def wildcard(self):
        """@return: A L{Wildcard} object based on this IP address"""
        if self.addr_type == AT_INET6:
            raise AddrConversionError('wildcards not support by IPv6!')
        return self.iprange().wildcard()

    def iprange(self):
        """@return: A L{CIDR} object based on this IP address"""
        hostmask = (1 << (self.strategy.width - self.prefixlen)) - 1
        netmask = self.strategy.max_int ^ hostmask
        first = (self.value | hostmask) - hostmask
        last = first | hostmask
        return IPRange(self.strategy.int_to_str(first),
                       self.strategy.int_to_str(last))

    def ipv4(self):
        """
        @return: A new version 4 L{IP} object numerically equivalent this
        address. If this object is already IPv4 then a copy is returned. If
        this object is IPv6 and its value is compatible with IPv4, a new IPv4
        L{IP} object is returned.

        Raises an L{AddrConversionError} is IPv6 address cannot be converted.
        """
        ip_addr = None
        if self.addr_type == AT_INET:
            ip_addr = IP(self.value, AT_INET)
            ip_addr.prefixlen = self.prefixlen
        elif self.addr_type == AT_INET6:
            words = self.strategy.int_to_words(self.value)
            #TODO:   Replace these with bit shifts.
            if words[0:6] == (0, 0, 0, 0, 0, 0):
                ip_addr = IP(self.value, AT_INET)
                ip_addr.prefixlen = self.prefixlen - 96
            #TODO:   Replace these with bit shifts.
            elif words[0:6] == (0, 0, 0, 0, 0, 0xffff):
                ip_addr = IP(self.value - 0xffff00000000, AT_INET)
                ip_addr.prefixlen = self.prefixlen - 96
            else:
                raise AddrConversionError('IPv6 address %s not suitable for' \
                    'IPv4 conversion!' % self)
        return ip_addr

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
        ip_addr = None
        if self.addr_type == AT_INET6:
            ip_addr = IP(self.value, AT_INET6)
            ip_addr.prefixlen = self.prefixlen - 96
        elif self.addr_type == AT_INET:
            ip_addr = IP(self.value, AT_INET6)
            if ipv4_compatible:
                #   IPv4-Compatible IPv6 address
                ip_addr[5] = 0
            else:
                #   IPv4-Mapped IPv6 address
                ip_addr[5] = 0xffff
            ip_addr.prefixlen = self.prefixlen + 96
        return ip_addr

    def is_unicast(self):
        """@return: C{True} if this IP is unicast, C{False} otherwise"""
        return not self.is_multicast()

    def is_loopback(self):
        """
        @return: C{True} if this IP is loopback address (not for network
            transmission), C{False} otherwise.
            References: RFC 3330 and 4291.
        """
        if self.addr_type == AT_INET:
            return self in CIDR('127/8')
        elif  self.addr_type == AT_INET6:
            return self == IP('::1')

    def is_multicast(self):
        """@return: C{True} if this IP is multicast, C{False} otherwise"""
        if self.addr_type == AT_INET:
            return self in CIDR('224/4')
        elif  self.addr_type == AT_INET6:
            return self in CIDR('ff00::/8')

    def is_private(self):
        """
        @return: C{True} if this IP is for internal/private use only
            (i.e. non-public), C{False} otherwise. Reference: RFCs 1918,
            3330, 4193, 3879 and 2365.
        """
        if self.addr_type == AT_INET:
            for cidr in (CIDR('192.168/16'), CIDR('10/8'),CIDR('172.16/12'),
                         CIDR('192.0.2.0/24'), CIDR('239.192/14')):
                if self in cidr:
                    return True
        elif self.addr_type == AT_INET6:
            #   Please Note: FEC0::/10 has been deprecated! See RFC 3879.
            return self in CIDR('fc00::/7') #   ULAs - Unique Local Addresses

        if self.is_link_local():
            return True

        return False

    def is_link_local(self):
        """
        @return: C{True} if this IP is link-local address C{False} otherwise.
            Reference: RFCs 3927 and 4291.
        """
        if self.addr_type == AT_INET:
            return self in CIDR('169.254/16')
        elif self.addr_type == AT_INET6:
            return self in CIDR('fe80::/10')

    def is_reserved(self):
        """
        @return: C{True} if this IP is in IANA reserved range, C{False}
            otherwise. Reference: RFCs 3330 and 3171.
        """
        if self.addr_type == AT_INET:
            #   Use of wildcards here much more concise than CIDR...
            for cidr in (CIDR('240/4'), CIDR('234/7'), CIDR('236/7'),
                         Wildcard('225-231.*.*.*'), Wildcard('234-238.*.*.*')):
                if self in cidr:
                    return True
        if self.addr_type == AT_INET6:
            for cidr in (CIDR('ff00::/12'),CIDR('::/8'), CIDR('0100::/8'),
                         CIDR('0200::/7'), CIDR('0400::/6'), CIDR('0800::/5'),
                         CIDR('1000::/4'), CIDR('4000::/3'), CIDR('6000::/3'),
                         CIDR('8000::/3'), CIDR('A000::/3'), CIDR('C000::/3'),
                         CIDR('E000::/4'), CIDR('F000::/5'), CIDR('F800::/6'),
                         CIDR('FE00::/9')):
                if self in cidr:
                    return True
        return False

    def is_ipv4_mapped(self):
        """
        @return: C{True} if this IP is IPv4-compatible IPv6 address, C{False}
            otherwise.
        """
        return self.addr_type == AT_INET6 and (self.value >> 32) == 0xffff

    def is_ipv4_compat(self):
        """
        @return: C{True} if this IP is IPv4-mapped IPv6 address, C{False}
            otherwise.
        """
        return self.addr_type == AT_INET6 and (self.value >> 32) == 0

    def info(self):
        """
        @return: A record dict containing IANA registration details for this
            IP address if available, None otherwise.
        """
        #   This import is placed here for efficiency. If you don't call this
        #   method, you don't take the (small), one time, import start up
        #   penalty. Also gets around a nasty module dependency issue.
        #   Two birds, one stone ...
        import netaddr.ip
        return netaddr.ip.query(self)

    def __str__(self):
        """@return: common string representation for this IP address"""
        return self.strategy.int_to_str(self.value)

    def __repr__(self):
        """@return: executable Python string to recreate equivalent object."""
        if self.prefixlen == self.strategy.width:
            return "%s('%s')" % (self.__class__.__name__, str(self))

        return "%s('%s/%d')" % (self.__class__.__name__, str(self),
            self.prefixlen)

#-----------------------------------------------------------------------------
def nrange(start, stop, step=1, fmt=None):
    """
    An xrange work alike generator that produces sequences of IP addresses
    based on start and stop addresses, in intervals of step size.

    @param start: first IP address string or L{IP} object in range.

    @param stop: last IP address string or L{IP} object in range

    @param step: (optional) size of step between address in range.
        (Default: 1)

    @param fmt: (optional) callable used on addresses returned.
        (Default: None - L{IP} objects). Supported options :-
            - C{str} - IP address in string format
            - C{int}, C{long} - IP address as an unsigned integer
            - C{hex} - IP address as a hexadecimal number
            - L{IP} class/subclass or callable that accepts C{addr_value} and
                C{addr_type} arguments.
    """
    if not isinstance(start, IP):
        if isinstance(start, (str, unicode)):
            start = IP(start)
        else:
            raise TypeError('start is not recognised address in string ' \
                'format or IP class/subclass instance!')
    else:
        #   Use start object's constructor as formatter.
        if fmt is None:
            fmt = start.__class__

    if not isinstance(stop, IP):
        if isinstance(stop, (str, unicode)):
            stop = IP(stop)
        else:
            raise TypeError('stop is not recognised address string ' \
                'or IP class/subclass instance!')

    if not isinstance(step, (int, long)):
        raise TypeError('step must be type int|long, not %s!' % type(step))

    if start.addr_type != stop.addr_type:
        raise TypeError('start and stop are not the same address type!')

    if step == 0:
        raise ValueError('step argument cannot be zero')

    negative_step = False
    addr_type = start.addr_type

    #   We don't need objects from here onwards. Basic integer values will do
    #   just fine.
    start_fmt = start.__class__
    start = int(start)
    stop = int(stop)

    if step < 0:
        negative_step = True

    index = start - step

    #   Default formatter.
    if fmt is None:
        fmt = IP

    if fmt in (int, long, hex):
        #   Yield network address integer values.
        while True:
            index += step
            if negative_step:
                if not index >= stop:
                    return
            else:
                if not index <= stop:
                    return
            yield fmt(index)
    elif fmt in (str, unicode):
        #   Yield address string values.
        while True:
            index += step
            if negative_step:
                if not index >= stop:
                    return
            else:
                if not index <= stop:
                    return
            yield str(start_fmt(index, addr_type))
    else:
        #   Yield network address objects.
        while True:
            index += step
            if negative_step:
                if not index >= stop:
                    return
            else:
                if not index <= stop:
                    return

            yield fmt(index, addr_type)

#-----------------------------------------------------------------------------
class IPRange(object):
    """
    Represents arbitrary contiguous blocks of IPv4 and IPv6 addresses using
    only a lower and upper bound IP address.

    It is the base class for more specialised block types such as L{CIDR()}
    and L{Wildcard()}. There is no requirement that the boundary IP addresses
    fall on strict bitmask boundaries.

    The sort order for sequence of mixed version L{IPRange} objects is IPv4
    followed by IPv6, based on the range's magnitude (size).
    """
    STRATEGIES = (ST_IPV4, ST_IPV6)
    ADDR_TYPES = (AT_UNSPEC, AT_INET, AT_INET6)

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)
    first = AddrValueDescriptor('first')
    last = AddrValueDescriptor('last')
    fmt = FormatDescriptor(IP)

    def __init__(self, first, last, fmt=IP):
        """
        Constructor.

        @param first: start address for this IP address range.

        @param last: stop address for this IP address range.

        @param fmt: (optional) callable used to create return values.
            Default: L{IP()} objects. See L{nrange()} documentations for
            more details on the various options.
        """
        #TODO: this can be optimised, consider accepting addr_type via the
        #TODO: constructor.
        self.addr_type = AT_UNSPEC
        self.first = first
        self.last = last
        if self.last < self.first:
            raise IndexError('start address is greater than stop address!')
        self.fmt = fmt

    def __hash__(self):
        """
        @return: The hash of this address range. Allow them to be used in sets
            and as keys in dictionaries.
        """
        return hash((self.first, self.last, self.addr_type))

    def tuple(self):
        """
        @return: A 3-element tuple (first, last, addr_type) which represent
            the basic details of this IPRange object.
        """
        return self.first, self.last, self.addr_type

    def __len__(self):
        """
        @return: The total number of network addresses in this range.
            - Use this method only for ranges that contain less than
            C{2^31} addresses or try the L{size()} method. Raises an
            C{IndexError} if size is exceeded.
        """
        size = self.size()
        if size > (2 ** 31):
            #   Use size() method in this class instead as len() will b0rk!
            raise IndexError("range contains greater than 2^31 addresses! " \
                "Use obj.size() instead.")
        return size

    def size(self):
        """
        @return: The total number of network addresses in this range.
            - Use this method in preference to L{__len__()} when size of
            ranges potentially exceeds C{2^31} addresses.
        """
        return self.last - self.first + 1

    def format(self, int_addr, fmt=None):
        """
        @param int_addr: a network address as an unsigned integer.

        @param fmt: (optional) a callable used on return values.
            Default: None. If set to None, this method uses the self.fmt
            setting instead. The argument is provided as an override option.

        @return: a network address in the format returned after passing it
            through this object's fmt property callable.
        """
        if fmt is None:
            fmt = self.fmt

        if fmt in (str, unicode):
            return self.strategy.int_to_str(int_addr)
        elif fmt in (int, long, hex):
            return fmt(int_addr)
        else:
            return fmt(int_addr, self.addr_type)

    def __getitem__(self, index):
        """
        @return: The IP address(es) in this address range referenced by
            index/slice. Slicing objects can produce large sequences so
            generator objects are returned instead of a list. Wrapping a slice
            with C{list()} or C{tuple()} may be required dependent on context
            in which it is called.
        """

        if isinstance(index, (int, long)):
            if (- self.size()) <= index < 0:
                #   negative index.
                return self.format(self.last + index + 1)
            elif 0 <= index <= (self.size() - 1):
                #   Positive index or zero index.
                return self.format(self.first + index)
            else:
                raise IndexError('index out range for address range size!')
        elif isinstance(index, slice):
            #   slices
            #FIXME: IPv6 breaks the .indices() method on the slice object
            #FIXME: spectacularly. We'll have to work out the start, stop and
            #FIXME: step ourselves :-(
            #
            #FIXME: see PySlice_GetIndicesEx function in Python SVN
            #FIXME: repository for implementation details :-
            #   http://svn.python.org/view/python/trunk/Objects/sliceobject.c
            (start, stop, step) = index.indices(self.size())

            start_addr = IP(self.first + start, self.addr_type)
            end_addr = IP(self.first + stop - step, self.addr_type)
            return nrange(start_addr, end_addr, step, fmt=self.fmt)
        else:
            raise TypeError('unsupported type %r!' % index)

    def __iter__(self):
        """
        @return: An iterator object providing access to all network addresses
            within this range.
        """
        start_addr = IP(self.first, self.addr_type)
        end_addr = IP(self.last, self.addr_type)
        return nrange(start_addr, end_addr, fmt=self.fmt)

    def __contains__(self, addr):
        """
        @param addr: and IP/IPRange class/subclass instance or IP string value
            to be compared.

        @return: C{True} if given address or range falls within this range,
            C{False} otherwise.
        """
        if isinstance(addr, (str, unicode)):
            #   string address or address range.
            c_addr = IP(addr)
            if c_addr.addr_type == self.addr_type:
                if self.first <= int(c_addr) <= self.last:
                    return True
        elif isinstance(addr, IP):
            #   Single value check.
            if self.first <= int(addr) <= self.last:
                return True
        elif issubclass(addr.__class__, IPRange):
            #   Range value check.
            if addr.first >= self.first and addr.last <= self.last:
                return True
        else:
            raise TypeError('%r is an unsupported type or class!' % addr)

        return False

    def __eq__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are the same as
            other, C{False} otherwise.
        """
        try:
            return (self.addr_type,  self.first,  self.last) == \
                   (other.addr_type, other.first, other.last)
        except AttributeError:
            return False

    def __ne__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{False} if the boundaries of this range are the same as
            other, C{True} otherwise.
        """
        try:
            return (self.addr_type,  self.first,  self.last) != \
                   (other.addr_type, other.first, other.last)
        except AttributeError:
            return True

    def __lt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are less than other,
            C{False} otherwise.
        """
        try:
            #   A sort key is essentially a CIDR prefixlen value.
            #   Required as IPRange (and subclasses other than CIDR) do not
            #   calculate it.
            s_sortkey = self.strategy.width - num_bits(self.size())
            o_sortkey = other.strategy.width - num_bits(other.size())

            return (self.addr_type,  self.first,  s_sortkey) < \
                   (other.addr_type, other.first, o_sortkey)
        except AttributeError:
            return False

    def __le__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are less or equal to
            other, C{False} otherwise.
        """
        try:
            #   A sort key is essentially a CIDR prefixlen value.
            #   Required as IPRange (and subclasses other than CIDR) do not
            #   calculate it.
            s_sortkey = self.strategy.width - num_bits(self.size())
            o_sortkey = other.strategy.width - num_bits(other.size())

            return (self.addr_type,  self.first,  s_sortkey) <= \
                   (other.addr_type, other.first, o_sortkey)
        except AttributeError:
            return False

    def __gt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are greater than
            other, C{False} otherwise.
        """
        try:
            #   A sort key is essentially a CIDR prefixlen value.
            #   Required as IPRange (and subclasses other than CIDR) do not
            #   calculate it.
            s_sortkey = self.strategy.width - num_bits(self.size())
            o_sortkey = other.strategy.width - num_bits(other.size())

            return (self.addr_type,  self.first,  s_sortkey) > \
                   (other.addr_type, other.first, o_sortkey)
        except AttributeError:
            return False

    def __ge__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are greater or equal
            to other, C{False} otherwise.
        """
        try:
            #   A sort key is essentially a CIDR prefixlen value.
            #   Required as IPRange (and subclasses other than CIDR) do not
            #   calculate it.
            s_sortkey = self.strategy.width - num_bits(self.size())
            o_sortkey = other.strategy.width - num_bits(other.size())

            return (self.addr_type,  self.first,  s_sortkey) >= \
                   (other.addr_type, other.first, o_sortkey)
        except AttributeError:
            return False

    def __iadd__(self, i):
        """
        Increments start and end addresses of this range by the current size.

        Raises IndexError if the result exceeds address range maximum.
        """
        try:
            new_first = self.first + (self.size() * i)
            new_last = self.last + (self.size() * i)
        except TypeError:
            raise TypeError('Increment value must be an integer!')

        if new_last > self.strategy.max_int:
            raise IndexError('Invalid increment is outside address boundary!')

        self.first = new_first
        self.last = new_last

        return self

    def __isub__(self, i):
        """
        Decrements start and end addresses of this range by the current size.

        Raises IndexError if the result is less than zero.
        """
        try:
            new_first = self.first - (self.size() * i)
            new_last = self.last - (self.size() * i)
        except TypeError:
            raise TypeError('Decrement value must be an integer!')

        if new_last < 0:
            raise IndexError('Invalid decrement is outside address boundary!')

        self.first = new_first
        self.last = new_last

        return self

    def iprange(self):
        """
        @return: A valid L{IPRange} object for this address range.
        """
        #TODO: this can be optimised.
        ip_range = IPRange(self.strategy.int_to_str(self.first),
                          self.strategy.int_to_str(self.last))
        if self.fmt == str:
            return str(ip_range)
        return ip_range

    def cidrs(self):
        """
        @return: A list of one or more L{CIDR} objects covering this address
            range. B{Please Note:} a list is returned even if this range maps
            to a single CIDR because arbitrary ranges may not be aligned with
            base 2 subnet sizes and will therefore return multiple CIDRs.
        """
        #   This can probably be tidied up a bit but I'm really proud of this
        #   method. It is one seriously sweet piece of code!!!
        cidr_list = []

        #   Get spanning CIDR covering both addresses.
        start = IP(self.first, self.addr_type)
        end = IP(self.last, self.addr_type)

        cidr_span = CIDR.span([start, end])

        if cidr_span.first == self.first and cidr_span.last == self.last:
            #   Spanning CIDR matches start and end exactly.
            cidr_list = [cidr_span]
        elif cidr_span.last == self.last:
            #   Spanning CIDR matches end exactly.
            ip = IP(start)
            first_int_val = int(ip)
            ip -= 1
            cidr_remainder = cidr_span - ip

            first_found = False
            for cidr in cidr_remainder:
                if cidr.first == first_int_val:
                    first_found = True
                if first_found:
                    cidr_list.append(cidr)
        elif cidr_span.first == self.first:
            #   Spanning CIDR matches start exactly.
            ip = IP(end)
            last_int_val = int(ip)
            ip += 1
            cidr_remainder = cidr_span - ip

            last_found = False
            for cidr in cidr_remainder:
                cidr_list.append(cidr)
                if cidr.last == last_int_val:
                    break
        elif cidr_span.first <= self.first and cidr_span.last >= self.last:
            #   Spanning CIDR overlaps start and end.
            ip = IP(start)
            first_int_val = int(ip)
            ip -= 1
            cidr_remainder = cidr_span - ip

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
            cidr_remainder = cidr_list.pop() - ip

            last_found = False
            for cidr in cidr_remainder:
                cidr_list.append(cidr)
                if cidr.last == last_int_val:
                    break

        #   Return address list in requested format.
        if self.fmt in (str, unicode):
            cidr_list = [self.fmt(c) for c in cidr_list]

        return cidr_list

    def wildcard(self):
        """
        @return: A L{Wildcard} object equivalent to this CIDR.
            - If CIDR was initialised with C{fmt=str}, a wildcard string
              is returned, in all other cases a L{Wildcard} object is
              returned.
            - Only supports IPv4 CIDR addresses.
        """
        t1 = self.strategy.int_to_words(self.first)
        t2 = self.strategy.int_to_words(self.last)

        if self.addr_type != AT_INET:
            raise AddrConversionError('wildcards only suitable for IPv4 ' \
                'ranges!')

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
                #   Create a hyphenated octet - only one allowed per wildcard.
                if not seen_asterisk:
                    if not seen_hyphen:
                        tokens.append('%s-%s' % (t1[i], t2[i]))
                        seen_hyphen = True
                    else:
                        raise SyntaxError('only one hyphenated octet per ' \
                            'wildcard permitted!')
                else:
                    raise SyntaxError("* chars aren't permitted before ' \
                        'hyphenated octets!")

        wildcard = '.'.join(tokens)

        if self.fmt == str:
            return wildcard

        return Wildcard(wildcard)

    def issubnet(self, other):
        """
        @return: True if other's boundary is equal to or within this range.
            False otherwise.
        """
        if isinstance(other, (str, unicode)):
            other = CIDR(other)

        if not hasattr(other, 'addr_type'):
            raise TypeError('%r is an unsupported argument type!' % other)

        if self.addr_type != other.addr_type:
            raise TypeError('Ranges must be the same address type!')

        return self.first >= other.first and self.last <= other.last

    def issupernet(self, other):
        """
        @return: True if other's boundary is equal to or contains this range.
            False otherwise.
        """
        if isinstance(other, (str, unicode)):
            other = CIDR(other)

        if not hasattr(other, 'addr_type'):
            raise TypeError('%r is an unsupported argument type!' % other)

        if self.addr_type != other.addr_type:
            raise TypeError('Ranges must be the same address type!')

        return self.first <= other.first and self.last >= other.last

    def adjacent(self, other):
        """
        @return: True if other's boundary touches the boundary of this
            address range, False otherwise.
        """
        if isinstance(other, (str, unicode)):
            other = CIDR(other)

        if not hasattr(other, 'addr_type'):
            raise TypeError('%r is an unsupported argument type!' % other)

        if self.addr_type != other.addr_type:
            raise TypeError('addresses must be of the same type!')

        if isinstance(other, IPRange):
            #   Left hand side of this address range.
            if self.first == (other.last + 1):
                return True

            #   Right hand side of this address range.
            if self.last == (other.first - 1):
                return True
        elif isinstance(other, IP):
            #   Left hand side of this address range.
            if self.first == (other.value + 1):
                return True

            #   Right hand side of this address range.
            if self.last == (other.value - 1):
                return True
        else:
            raise TypeError('unexpected error for argument: %r!')

        return False

    def overlaps(self, other):
        """
        @return: True if other's boundary crosses the boundary of this address
            range, False otherwise.
        """
        if isinstance(other, (str, unicode)):
            other = CIDR(other)

        if not hasattr(other, 'addr_type'):
            raise TypeError('%r is an unsupported argument type!' % other)

        if self.addr_type != other.addr_type:
            raise TypeError('Ranges must be the same address type!')

        #   Left hand side of this address range.
        if self.first <= other.last <= self.last:
            return True

        #   Right hand side of this address range.
        if self.first <= other.first <= self.last:
            return True

        return False

    def __str__(self):
        return "%s-%s" % (self.strategy.int_to_str(self.first),
                          self.strategy.int_to_str(self.last))

    def __repr__(self):
        """@return: executable Python string to recreate equivalent object."""
        return "%s(%r, %r)" % (self.__class__.__name__,
            self.strategy.int_to_str(self.first),
            self.strategy.int_to_str(self.last))

#-----------------------------------------------------------------------------
def cidr_to_bits(cidr):
    """
    @param cidr: a CIDR object or CIDR string value (acceptable by CIDR class
        constructor).

    @return: a tuple containing CIDR in binary string format and addr_type.
    """
    if not hasattr(cidr, 'network'):
        cidr = CIDR(cidr, strict=False)

    bits = cidr.network.bits(word_sep='')
    return (bits[0:cidr.prefixlen], cidr.addr_type)

#-----------------------------------------------------------------------------
def bits_to_cidr(bits, addr_type=AT_UNSPEC, fmt=None):
    """
    @param bits: a CIDR in binary string format.

    @param addr_type: (optional) CIDR address type (IP version).
        (Default: AT_UNSPEC - auto-select) If not specified AT_INET (IPv4) is
        assumed if length of binary string is <= /32. If binary string
        is > /32 and <= /128 AT_INET6 (IPv6) is assumed. Useful when you have
        IPv6 addresses with a prefixlen of /32 or less.

    @param fmt: (optional) callable invoked on return CIDR.
        (Default: None - CIDR object). Also accepts str() and unicode().

    @return: a CIDR object or string (determined by fmt).
    """
    if _re.match('^[01]+$', bits) is None:
        raise ValueError('%r is an invalid bit string!' % bits)

    num_bits = len(bits)
    strategy = None
    if addr_type == AT_UNSPEC:
        if 0 <= num_bits <= 32:
            strategy = ST_IPV4
        elif 33 < num_bits <= 128:
            strategy = ST_IPV6
        else:
            raise ValueError('Invalid number of bits: %s!' % bits)
    elif addr_type == AT_INET:
        strategy = ST_IPV4
    elif addr_type == AT_INET6:
        strategy = ST_IPV6
    else:
        raise ValueError('strategy auto-select failure for %r!' % bits)

    if bits == '':
        return CIDR('%s/0' % strategy.int_to_str(0))

    cidr = None
    bits = bits + '0' * (strategy.width - num_bits)
    ip = strategy.int_to_str(strategy.bits_to_int(bits))
    cidr = CIDR('%s/%d' % (ip, num_bits))

    if fmt is not None:
        return fmt(cidr)

    return cidr

#-----------------------------------------------------------------------------
class CIDR(IPRange):
    """
    Represents blocks of IPv4 and IPv6 addresses using CIDR (Classless
    Inter-Domain Routing) notation.

    CIDR is a method of categorising contiguous blocks of both IPv4 and IPv6
    addresses. It is very scalable allowing for the optimal usage of the IP
    address space. It permits the aggregation of networks via route
    summarisation (supernetting) where adjacent routes can be combined into a
    single route easily. This greatly assists in the reduction of routing
    table sizes and improves network router efficiency.

    CIDR blocks are represented by a base network address and a prefix
    indicating the size of the (variable length) subnet mask. These are
    separated by a single '/' character. Subnet sizes increase in powers of
    base 2 aligning to bit boundaries.

    It is technically invalid to have non-zero bits in a CIDR address to the
    right of the implied netmask. For user convenience this is however
    configurable and can be disabled using a constructor argument.

    The constructor accepts CIDRs expressed in one of 4 different ways :-

    A) Standard CIDR format :-

    IPv4::

        x.x.x.x/y -> 192.0.2.0/24

    where the x's represent the network address and y is the netmask
    prefix between 0 and 32.

    IPv6::

        x::/y -> fe80::/10

    where the x's represent the network address and y is the netmask
    prefix between 0 and 128.

    B) Abbreviated CIDR format (IPv4 only)::

        x       -> 192
        x/y     -> 10/8
        x.x/y   -> 192.168/16
        x.x.x/y -> 192.168.0/24

    which are equivalent to::

        x.0.0.0/y   -> 192.0.0.0/24
        x.0.0.0/y   -> 10.0.0.0/8
        x.x.0.0/y   -> 192.168.0.0/16
        x.x.x.0/y   -> 192.168.0.0/24

        - The trailing zeros are implicit.
        - Old classful IP address rules apply if y is omitted.

    C) Hybrid CIDR format (prefix replaced by netmask) :-

    IPv4::

        x.x.x.x/y.y.y.y -> 192.0.2.0/255.255.255.0

    IPv6::

        x::/y:: -> fe80::/ffc0::

    where the y's represent a valid netmask.

    D) ACL-style CIDR format (prefix is replaced by a hostmask) :-

    Akin to Cisco's ACL (Access Control List) bitmasking (reverse
    netmasks).

    IPv4::

        x.x.x.x/y.y.y.y -> 192.0.2.0/0.0.0.255

    IPv6::

        x::/y:: -> fe80::/3f:ffff:ffff:ffff:ffff:ffff:ffff:ffff

    where the y's represent a valid hostmask.

    Reference: RFCs 1338 and 4632.
    """
    STRATEGIES = (ST_IPV4, ST_IPV6)
    ADDR_TYPES = (AT_UNSPEC, AT_INET, AT_INET6)

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)
    prefixlen = PrefixLenDescriptor('CIDR')
    fmt = FormatDescriptor(IP)

    @staticmethod
    def abbrev_to_verbose(abbrev_cidr):
        """
        A static method that converts abbreviated IPv4 CIDRs to their more
        verbose equivalent.

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
        network address, C{None} if format provided was not recognised or
        supported.
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
            #   Don't support IPv6 for now...
            if ':' in abbrev_cidr:
                return None
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
                return None

            if '/' in part_addr:
                (part_addr, prefix) = part_addr.split('/', 1)

            #   Check prefix for validity.
            if prefix is not None:
                try:
                    if not 0 <= int(prefix) <= 32:
                        return None
                except ValueError:
                    return None

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
                return None

            if prefix is None:
                try:
                    prefix = classful_prefix(tokens[0])
                except ValueError:
                    return None

            return "%s%s/%s" % (start, '.'.join(tokens), prefix)

        except TypeError:
            pass
        except IndexError:
            pass

        #   Not a recognisable format.
        return None

    @staticmethod
    def span(addrs, fmt=None):
        """
        Static method that accepts a sequence of IP addresses and/or CIDRs,
        Wildcards and IPRanges returning a single CIDR that is large enough
        to span the lowest and highest IP addresses in the sequence (with
        a possible overlap on either end).

        @param addrs: a sequence of IP, CIDR, Wildcard or IPRange objects
            and/or their string representations.

        @param fmt: (optional) callable used on return values.
            (Default: None - L{CIDR} object) Also accepts str() and unicode().

        @return: a single CIDR object spanning all addresses.
        """
        if not isinstance(addrs, (list, tuple)): #  Required - DO NOT CHANGE!
            raise TypeError('expected address sequence is not iterable!')

        if not len(addrs) > 1:
            raise ValueError('sequence must contain 2 or more elements!')

        if fmt not in (None, str, unicode):
            raise ValueError('unsupported formatter %r!' % fmt)

        #   List is required.
        if not isinstance(addrs, list):
            addrs = list(addrs)

        #   Detect type of string address or address range and create the
        #   equivalent instance.
        for (i, addr) in enumerate(addrs):
            if isinstance(addr, (str, unicode)):
                try:
                    obj = IP(addr)
                    addrs[i] = obj
                    continue
                except:
                    pass
                try:
                    obj = CIDR(addr)
                    addrs[i] = obj
                    continue
                except:
                    pass
                try:
                    obj = Wildcard(addr)
                    addrs[i] = obj
                    continue
                except:
                    pass

        #   Find lowest and highest IP objects in address list.
        addrs.sort()
        lowest = addrs[0]
        highest = addrs[-1]

        if isinstance(lowest, IPRange):
            #   Create new IP as user may be returning address strings.
            lowest = IP(lowest.first, lowest.addr_type)

        if isinstance(highest, IPRange):
            #   Create new IP as user may be returning address strings.
            highest = IP(highest.last, highest.addr_type)

        if lowest.addr_type != highest.addr_type:
            raise TypeError('address types are not the same!')

        cidr = highest.cidr()

        while cidr.prefixlen > 0:
            if highest in cidr and lowest not in cidr:
                cidr.prefixlen -= 1
            else:
                break

        #   Return address in string format.
        if fmt is not None:
            return fmt(cidr)

        return cidr

    @staticmethod
    def summarize(cidrs, fmt=None):
        """
        Static method that accepts a sequence of IP addresses and/or CIDRs
        returning a summarized sequence of merged CIDRs where possible. This
        method doesn't create any CIDR that are inclusive of any addresses
        other than those found in the original sequence provided.

        @param cidrs: a list or tuple of IP and/or CIDR objects.

        @param fmt: callable used on return values.
            (Default: None - L{CIDR} objects). str() and unicode() supported.

        @return: a possibly smaller list of CIDRs covering sequence passed in.
        """
        if not hasattr(cidrs, '__iter__'):
            raise ValueError('A sequence or iterable is expected!')

        #   Start off using set as we'll remove any duplicates at the start.
        ipv4_bit_cidrs = set()
        ipv6_bit_cidrs = set()

        #   Convert CIDRs into bit strings separating IPv4 from IPv6
        #   (required).
        for cidr in cidrs:
            (bits, addr_type) = cidr_to_bits(cidr)
            if addr_type == AT_INET:
                ipv4_bit_cidrs.add(bits)
            elif addr_type == AT_INET6:
                ipv6_bit_cidrs.add(bits)
            else:
                raise ValueError('Unknown address type found!')

        #   Merge binary CIDRs into their smallest equivalents.
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

        #   Reduce and format IPv4 CIDRs.
        for bit_cidr in _reduce_bit_cidrs(list(ipv4_bit_cidrs)):
            new_cidrs.append(bits_to_cidr(bit_cidr, fmt=fmt))

        #   Reduce and format IPv6 CIDRs.
        for bit_cidr in _reduce_bit_cidrs(list(ipv6_bit_cidrs)):
            new_cidrs.append(bits_to_cidr(bit_cidr, fmt=fmt))

        return new_cidrs

    def __init__(self, cidr, fmt=IP, strict=True, expand_abbrev=True):
        """
        Constructor.

        @param cidr: a valid IPv4/IPv6 CIDR address or abbreviated IPv4
            network address.

        @param fmt: (optional) callable used on return values.
            Default: L{IP} class. See L{nrange()} documentations for
            more details on the various options.

        @param strict: (optional) If True and non-zero bits are found to the
            right of the subnet mask/prefix a ValueError is raised. If False,
            CIDR returned has these bits automatically truncated.
            (default: True)

        @param expand_abbrev: (optional) If True, enables the abbreviated CIDR
            expansion routine. If False, abbreviated CIDRs will be considered
            invalid addresses, raising an AddrFormatError exception.
            (default: True)
        """
        cidr_arg = cidr     #   Keep a copy of original argument.

        if expand_abbrev:
            #   Replace an abbreviation with a verbose CIDR.
            verbose_cidr = CIDR.abbrev_to_verbose(cidr)
            if verbose_cidr is not None:
                cidr = verbose_cidr

        if not isinstance(cidr, (str, unicode)):
            raise TypeError('%r is not a valid CIDR!' % cidr)

        #   Check for prefix in address and extract it.
        try:
            (network, mask) = cidr.split('/', 1)
        except ValueError:
            network = cidr
            mask = None

        #FIXME: Are IP objects for first and last really necessary?
        #FIXME: Should surely just be integer values.
        first = IP(network)
        self.strategy = first.strategy

        if mask is None:
            #   If no mask is specified, assume maximum CIDR prefix.
            self.__dict__['prefixlen'] = first.strategy.width
        else:
            self.prefixlen = mask

        strategy = first.strategy
        addr_type = strategy.addr_type

        hostmask = (1 << (strategy.width - self.prefixlen)) - 1

        last = IP(first.value | hostmask, addr_type)

        if strict:
            #   Strict CIDRs enabled.
            netmask = strategy.max_int ^ hostmask
            host = (first.value | netmask) - netmask
            if host != 0:
                raise ValueError('%s contains non-zero bits right of the ' \
                    '%d-bit mask! Did you mean %s instead?' \
                        % (first, self.prefixlen,
                           strategy.int_to_str(int(last) - hostmask)))
        else:
            #   Strict CIDRs disabled.
            first.value = strategy.int_to_str(int(last) - hostmask)

        super(CIDR, self).__init__(first, last, fmt)

    def __sub__(self, other):
        """
        Subtract another CIDR from this one.

        @param other: a CIDR object that is greater than or equal to C{self}.

        @return: A list of CIDR objects than remain after subtracting C{other}
            from C{self}.
        """
        cidrs = []

        if self.prefixlen == self.strategy.width:
            #   Fail fast. Nothing to do in this case.
            return cidrs

        new_prefixlen = self.prefixlen + 1
        i_lower = self.first
        i_upper = self.first + (2 ** (self.strategy.width - new_prefixlen))

        lower = CIDR('%s/%d' % (self.strategy.int_to_str(i_lower),
            new_prefixlen))
        upper = CIDR('%s/%d' % (self.strategy.int_to_str(i_upper),
            new_prefixlen))

        while other.prefixlen >= new_prefixlen:
            if other in lower:
                matched = i_lower
                unmatched = i_upper
            elif other in upper:
                matched = i_upper
                unmatched = i_lower

            cidr = CIDR('%s/%d' % (self.strategy.int_to_str(unmatched),
                new_prefixlen))

            cidrs.append(cidr)

            new_prefixlen += 1

            if new_prefixlen > self.strategy.width:
                break

            i_lower = matched
            i_upper = matched + (2 ** (self.strategy.width - new_prefixlen))

            lower = CIDR('%s/%d' % (self.strategy.int_to_str(i_lower),
                new_prefixlen))
            upper = CIDR('%s/%d' % (self.strategy.int_to_str(i_upper),
                new_prefixlen))

        cidrs.sort()

        #   Return string based CIDR address values at user's request.
        if self.fmt is str:
            return [str(cidr) for cidr in cidrs]

        return cidrs

    def __add__(self, other):
        """
        Add another CIDR to this one returning a CIDR supernet that will
        contain both in the smallest possible sized range.

        @param other: a CIDR object.

        @return: A new (potentially larger) CIDR object.
        """
        cidr = CIDR.span([self, other])
        if self.fmt is str:
            return str(cidr)
        return cidr

    @property
    def network(self):
        """@return: The network (first) address in this CIDR block."""
        return self[0]

    @property
    def broadcast(self):
        """
        B{Please Note:} although IPv6 doesn't actually recognise the concept of
        broadcast addresses per se (as in IPv4), so many other libraries do
        this that it isn't worth trying to resist the trend just for the sake
        of making a theoretical point.

        @return: The broadcast (last) address in this CIDR block.
        """
        return self[-1]

    @property
    def netmask(self):
        """@return: The subnet mask address of this CIDR block."""
        hostmask = (1 << (self.strategy.width - self.prefixlen)) - 1
        netmask = self.strategy.max_int ^ hostmask
        return self.format(netmask)

    @property
    def hostmask(self):
        """@return: The host mask address of this CIDR block."""
        hostmask = (1 << (self.strategy.width - self.prefixlen)) - 1
        return self.format(hostmask)

    def previous(self, step=1):
        """
        @param step: the number of CIDRs between this CIDR and the expected
        one. Default: 1 - the preceding CIDR.

        @return: The immediate (adjacent) predecessor of this CIDR.
        """
        cidr_copy = CIDR('%s/%d' % (self.strategy.int_to_str(self.first),
            self.prefixlen))
        cidr_copy -= step
        #   Respect formatting.
        if self.fmt in (str, unicode):
            return self.fmt(cidr_copy)
        return cidr_copy

    def next(self, step=1):
        """
        @param step: the number of CIDRs between this CIDR and the expected
        one. Default: 1 - the succeeding CIDR.

        @return: The immediate (adjacent) successor of this CIDR.
        """
        cidr_copy = CIDR('%s/%d' % (self.strategy.int_to_str(self.first),
            self.prefixlen))
        cidr_copy += step
        #   Respect formatting.
        if self.fmt in (str, unicode):
            return self.fmt(cidr_copy)
        return cidr_copy

    def iter_host_addrs(self):
        """
        @return: An iterator object providing access to all valid host IP
            addresses within the specified CIDR block.
                - with IPv4 the network and broadcast addresses are always
                excluded. Any smaller than 4 hosts yields an emtpy list.
                - with IPv6 only the unspecified address '::' is excluded from
                the yielded list.
        """
        if self.addr_type == AT_INET:
            #   IPv4
            if self.size() >= 4:
                return nrange( IP(self.first+1, self.addr_type),
                    IP(self.last-1, self.addr_type), fmt=self.fmt)
            else:
                return iter([])
        elif self.addr_type == AT_INET6:
            #   IPv6
            if self.first == 0:
                #   Don't return '::'.
                return nrange(IP(self.first+1, self.addr_type),
                    IP(self.last, self.addr_type), fmt=self.fmt)
            else:
                return iter(self)

    def supernet(self, prefixlen=0, fmt=None):
        """
        Provides a list of supernet CIDRs for the current CIDR between the size
        of the current prefix and (if specified) the end CIDR prefix.

        @param prefixlen: (optional) a CIDR prefix for the maximum supernet.
            Default: 0 - returns all possible supernets.

        @param fmt: callable used on return values.
            Default: None - L{CIDR} objects. str() and unicode() supported.

        @return: an tuple containing CIDR supernets that contain this one.
        """
        if not 0 <= prefixlen <= self.strategy.width:
            raise ValueError('prefixlen %r invalid for IP version!' \
                % prefixlen)

        #   Use a copy of self as we'll be editing it.
        cidr = self.cidrs()[0]
        cidr.fmt = fmt

        supernets = []
        while cidr.prefixlen > prefixlen:
            cidr.prefixlen -= 1
            supernets.append(cidr.cidrs()[0])

        return list(reversed(supernets))

    def subnet(self, prefixlen, count=None, fmt=None):
        """
        A generator that returns CIDR subnets based on the current network
        base address and provided CIDR prefix and count.

        @param prefixlen: a CIDR prefix.

        @param count: number of consecutive CIDRs to be returned.

        @param fmt: callable used on return values.
            Default: None - L{CIDR} objects. str() and unicode() supported.

        @return: an iterator (as lists could potentially be very large)
            containing CIDR subnets below this CIDR's base address.
        """
        if not 0 <= self.prefixlen <= self.strategy.width:
            raise ValueError('prefixlen %d out of bounds for address type!' \
                % prefixlen)

        if not self.prefixlen <= prefixlen:
            raise ValueError('prefixlen less than current CIDR prefixlen!')

        #   Calculate number of subnets to be returned.
        width = self.strategy.width
        max_count = 2 ** (width - self.prefixlen) / 2 ** (width - prefixlen)

        if count is None:
            count = max_count

        if not 1 <= count <= max_count:
            raise ValueError('count not within current CIDR boundaries!')

        base_address = self.strategy.int_to_str(self.first)

        #   Respect self.fmt value if one wasn't passed to the method.
        if fmt is None and self.fmt in (str, unicode):
            fmt = self.fmt

        if fmt is None:
            #   Create new CIDR instances for each subnet returned.
            for i in xrange(count):
                cidr = CIDR('%s/%d' % (base_address, prefixlen))
                cidr.first += cidr.size() * i
                cidr.prefixlen = prefixlen
                yield cidr
        elif fmt in (str, unicode):
            #   Keep the same CIDR and just modify it.
            for i in xrange(count):
                cidr = CIDR('%s/%d' % (base_address, prefixlen))
                cidr.first += cidr.size() * i
                cidr.prefixlen = prefixlen
                yield fmt(cidr)
        else:
            raise TypeError('unsupported fmt callable %r' % fmt)

    def cidrs(self):
        """
        @return: A list of a copy of this L{CIDR} object. This method is here
            mainly for compatibility with IPRange interface.
        """
        cidr_copy = CIDR('%s/%d' % (self.strategy.int_to_str(self.first),
            self.prefixlen))

        #   Respect formatting.
        if self.fmt in (str, unicode):
            return [self.fmt(cidr_copy)]

        return [cidr_copy]

    def __str__(self):
        return "%s/%s" % (self.strategy.int_to_str(self.first), self.prefixlen)

    def __repr__(self):
        """@return: executable Python string to recreate equivalent object."""
        return "%s('%s/%d')" % (self.__class__.__name__,
            self.strategy.int_to_str(self.first), self.prefixlen)

#-----------------------------------------------------------------------------
class Wildcard(IPRange):
    """
    Represents blocks of IPv4 addresses using a wildcard or glob style syntax.

    Individual octets can be represented using the following shortcuts :

        1. C{*} - the asterisk octet (represents values 0 through 255)
        2. C{'x-y'} - the hyphenated octet (represents values x through y)

    A few basic rules also apply :

        1. x must always be greater than y, therefore :

            - x can only be 0 through 254
            - y can only be 1 through 255

        2. only one hyphenated octet per wildcard is allowed
        3. only asterisks are permitted after a hyphenated octet

    Example wildcards ::

        '192.168.0.1'       #   a single address
        '192.168.0.0-31'    #   32 addresses
        '192.168.0.*'       #   256 addresses
        '192.168.0-1.*'     #   512 addresses
        '192.168-169.*.*'   #   131,072 addresses
        '*.*.*.*'           #   the whole IPv4 address space

    Aside
    =====
        I{Wildcard ranges are not directly equivalent to CIDR blocks as they
        can represent address ranges that do not fall on strict bit mask
        boundaries. They are very suitable in configuration files being more
        obvious and readable than their CIDR equivalents, especially for admins
        and users without much networking knowledge or experience.}

        I{All CIDR blocks can always be represented as wildcard ranges but the
        reverse is not true. Wildcards are almost but not quite as flexible
        as IPRange objects.}
    """
    STRATEGIES = (ST_IPV4,)
    ADDR_TYPES = (AT_UNSPEC, AT_INET)

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)
    fmt = FormatDescriptor(IP)

    def is_valid(wildcard):
        """
        A static method that validates wildcard address ranges.

        @param wildcard: an IPv4 wildcard address.

        @return: True if wildcard address is valid, False otherwise.
        """
        #TODO: Add support for abbreviated wildcards
        #TODO: e.g. 192.168.*.* == 192.168.*
        #TODO:      *.*.*.*     == *
        #TODO: Add strict flag to enable verbose wildcard checking.
        seen_hyphen = False
        seen_asterisk = False
        try:
            octets = wildcard.split('.')
            if len(octets) != 4:
                return False
            for o in octets:
                if '-' in o:
                    if seen_hyphen:
                        return False
                    seen_hyphen = True
                    if seen_asterisk:
                        #   Asterisks cannot precede hyphenated octets.
                        return False
                    (o1, o2) = [int(i) for i in o.split('-')]
                    if o1 >= o2:
                        return False
                    if not 0 <= o1 <= 254:
                        return False
                    if not 1 <= o2 <= 255:
                        return False
                elif o == '*':
                    seen_asterisk = True
                else:
                    if seen_hyphen is True:
                        return False
                    if seen_asterisk is True:
                        return False
                    if not 0 <= int(o) <= 255:
                        return False
        except AttributeError:
            return False
        except ValueError:
            return False
        return True

    is_valid = staticmethod(is_valid)

    def __init__(self, wildcard, fmt=IP):
        """
        Constructor.

        @param wildcard: a valid IPv4 wildcard address

        @param fmt: (optional) callable used on return values.
            Default: L{IP} objects. See L{nrange()} documentations for
            more details on the various options..
        """
        if not Wildcard.is_valid(wildcard):
            raise AddrFormatError('%r is not a recognised wildcard address!' \
                % wildcard)
        t1 = []
        t2 = []

        for octet in wildcard.split('.'):
            if '-' in octet:
                oct_tokens = octet.split('-')
                t1 += [oct_tokens[0]]
                t2 += [oct_tokens[1]]
            elif octet == '*':
                t1 += ['0']
                t2 += ['255']
            else:
                t1 += [octet]
                t2 += [octet]

        first = '.'.join(t1)
        last = '.'.join(t2)
        super(Wildcard, self).__init__(first, last, fmt=fmt)

        if self.addr_type != AT_INET:
            raise AddrFormatError('Wildcard syntax only supports IPv4!')

    def __str__(self):
        t1 = self.strategy.int_to_words(self.first)
        t2 = self.strategy.int_to_words(self.last)

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
                #   Create a hyphenated octet - only one allowed per wildcard.
                if not seen_asterisk:
                    if not seen_hyphen:
                        tokens.append('%s-%s' % (t1[i], t2[i]))
                        seen_hyphen = True
                    else:
                        raise AddrFormatError('only one hyphenated octet ' \
                            ' per wildcard allowed!')
                else:
                    raise AddrFormatError('asterisks not permitted before ' \
                        'hyphenated octets!')

        return '.'.join(tokens)

    def __repr__(self):
        """@return: executable Python string to recreate equivalent object."""
        return "%s(%r)" % (self.__class__.__name__, str(self))


#-----------------------------------------------------------------------------
class IPRangeSet(set):
    """
    B{*EXPERIMENTAL*} A customised Python set class that deals with collections
    of IPRange class and subclass instances.
    """
    def __init__(self, addrs):
        """
        Constructor.

        @param addrs: A sequence of IPRange class/subclass instances used to
            pre-populate the set. Individual CIDR objects can be added and
            removed after instantiation with the usual set methods, add() and
            remove().
        """
        for addr in addrs:
            if isinstance(addr, IP):
                self.add(addr.cidr())
            if isinstance(addr, str):
                try:
                    self.add(CIDR(addr))
                except:
                    pass
                try:
                    ip = IP(addr)
                    self.add(ip.cidr())
                except:
                    pass
                try:
                    wildcard = Wildcard(addr)
                    try:
                        self.add(wildcard.cidr())
                    except:
                        self.add(wildcard)
                except:
                    pass
            else:
                self.add(addr)

    def __contains__(self, other):
        """
        @return: True if C{other} IP or IPRange class/subclass instance
            matches any of the members in this IPRangeSet, False otherwise.
        """
        for addr in self:
            if other in addr:
                return True

    def any_match(self, other):
        """
        @param other: An IP or IPRange class/subclass instance.

        @return: The first IP or IPRange class/subclass instance object that
            matches C{other} from any of the members in this IPRangeSet, None
            otherwise.
        """
        for addr in self:
            if other in addr:
                return addr

    def all_matches(self, other):
        """
        @param other: An IP or IPRange class/subclass instance.

        @return: All IP or IPRange class/subclass instances matching C{other}
            from this IPRangeSet, an empty list otherwise.
        """
        addrs = []
        for addr in self:
            if other in addr:
                addrs.append(addr)
        return addrs

    def min_match(self, other):
        """
        @param other: An IP or IPRange class/subclass instance.

        @return: The smallest IP or IPRange class/subclass instance matching
            C{other} from this IPRangeSet, None otherwise.
        """
        addrs = self.all_matches(other)
        addrs.sort()
        return addrs[0]

    def max_match(self, other):
        """
        @param other: An IP or IPRange class/subclass instance.

        @return: The largest IP or IPRange class/subclass instance matching
        C{other} from this IPRangeSet, None otherwise.
        """
        addrs = self.all_matches(other)
        addrs.sort()
        return addrs[-1]
