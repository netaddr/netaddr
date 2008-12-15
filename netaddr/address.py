#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network address classes (IP, EUI) and associated aggregate classes (CIDR,
Wilcard, etc).
"""
import math as _math
import socket as _socket

from netaddr import AddrFormatError, AddrConversionError, AT_UNSPEC, \
    AT_INET, AT_INET6, AT_LINK, AT_EUI64, AT_NAMES

from netaddr.strategy import ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64, \
    AddrStrategy

#: Address type to strategy object lookup dict.
AT_STRATEGIES = {
    AT_UNSPEC   : None,
    AT_INET     : ST_IPV4,
    AT_INET6    : ST_IPV6,
    AT_LINK     : ST_EUI48,
    AT_EUI64    : ST_EUI64,
}

#: Topic based dictionary Lookup for information provided by this module.
EXT_LOOKUP = {
    'IPv4' : {},
    'IPv6' : {},
    'multicast' : {},
    'OUI' : {},
}

#-----------------------------------------------------------------------------
def mac_info(mac_addr):
    """
    Returns informational data specific to this IP address.
    """
    info = {}

    #TODO: Check object type of mac_addr.

    #TODO: See if shelve object is available, default to parsing whole file
    #TODO: if not.

    #TODO: Multiple records.

    try:
        info['OUI'] = EXT_LOOKUP['OUI'][mac_addr.oui()]
    except KeyError:
        info['OUI'] = None

    #TODO include IAB data lookups.

    return info

#-----------------------------------------------------------------------------
def ip_info(ip_addr):
    """
    Returns informational data specific to this IP address.
    """
    info = {}

    if ip_addr.addr_type == AT_INET:
        for cidr, record in EXT_LOOKUP['IPv4'].items():
            if ip_addr in cidr:
                info.setdefault('IPv4', [])
                info['IPv4'].append(record)

        if ip_addr.is_multicast():
            for iprange, record in EXT_LOOKUP['multicast'].items():
                if ip_addr in iprange:
                    info.setdefault('Multicast', [])
                    info['Multicast'].append(record)

    elif ip_addr.addr_type == AT_INET6:
        for cidr, record in EXT_LOOKUP['IPv6'].items():
            if ip_addr in cidr:
                info.setdefault('IPv6', [])
                info['IPv6'].append(record)

    return info

#-----------------------------------------------------------------------------
#   Descriptor protocol classes.
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
    constructor. It accepts network addresses in either string format or as
    network byte order integers. String based addresses are converted to their
    integer equivalents before assignment to the named parameter. Also ensures
    that addr_type and strategy are set correctly when parsing string based
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
                raise TypeError('%r is an unsupported type!' % value)

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
    on address type. Also accepts subnet masks which can easily be converted
    to the equivalent prefixlen integer.
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
            if not ip.is_netmask():
                raise ValueError('%s is not a valid netmask!' % ip)
            prefixlen = ip.netmask_bits()

        #   Validate subnet prefix.
        if not 0 <= prefixlen <= instance.strategy.width:
            raise ValueError('%d is an invalid prefix for an %s CIDR!' \
                % (prefixlen, AT_NAMES[instance.addr_type]))

        #   Make sure instance is not a subnet mask trying to set a prefix!
        if isinstance(instance, IP):
            if instance.is_netmask() and instance.addr_type == AT_INET \
               and prefixlen != 32:
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
class KlassDescriptor(object):
    """
    A descriptor that checks klass (data flavour) property assignments for
    validity.
    """
    def __init__(self, default_klass):
        """
        Constructor.

        @param default_klass: the default class to use if klass property is
            set to None.
        """
        self.default_klass = default_klass

    def __set__(self, instance, value):
        if isinstance(value, type):
            if value in (str, int, long, unicode):
                pass
            elif issubclass(value, Addr):
                pass
            else:
                raise TypeError("%r is an unsupported klass type!" % value)
        elif value is hex:
            #   hex() is a BIF, not a type, so do a separate check for it.
            pass
        elif value is None:
            #   Use default class in None is specified.
            value = self.default_klass
        else:
            raise ValueError("%r is not a supported type, BIF or class!" \
                % value)

        instance.__dict__['klass'] = value

#-----------------------------------------------------------------------------
#   Address classes.
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
        """
        @return: The hash of this address. Allows it to be used in sets and
            as a key in dictionaries.
        """
        return hash((self.value, self.addr_type))

    def __int__(self):
        """
        @return: The value of this address as an network byte order integer.
        """
        return self.value

    def __long__(self):
        """
        @return: The value of this address as an network byte order integer.
        """
        return self.value

    def __str__(self):
        """
        @return: The common string representation for this address type.
        """
        return self.strategy.int_to_str(self.value)

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s(%r)" % (self.__class__.__name__, str(self))

    def bits(self):
        """
        @return: A human-readable binary digit string for this address type.
        """
        return self.strategy.int_to_bits(self.value)

    def __len__(self):
        """
        @return: The size of this address (in bits).
        """
        return self.strategy.width

    def __iter__(self):
        """
        @return: An iterator over individual words in this address.
        """
        return iter(self.strategy.int_to_words(self.value))

    def __getitem__(self, index):
        """
        @return: The integer value of the word indicated by index. Raises an
            C{IndexError} if index is wrong size for address type. Full
            slicing is also supported.
        """
        if isinstance(index, (int, long)):
            #   Indexing, including negative indexing goodness.
            word_count = self.strategy.word_count
            if not (-word_count) <= index <= (word_count - 1):
                raise IndexError('index out range for address type!')
            return self.strategy.int_to_words(self.value)[index]
        elif isinstance(index, slice):
            #   Slicing baby!
            words = self.strategy.int_to_words(self.value)
            return [words[i] for i in range(*index.indices(len(words)))]
        else:
            raise TypeError('unsupported type %r!' % index)

    def __setitem__(self, index, value):
        """
        Sets the value of the word of this address indicated by index.
        """
        if isinstance(index, slice):
            #   TODO - settable slices.
            raise NotImplementedError('settable slices not yet supported!')

        if not isinstance(index, (int, long)):
            raise TypeError('index not an integer!')

        if not 0 <= index <= (self.strategy.word_count - 1):
            raise IndexError('index %d outside address type boundary!' % index)

        if not isinstance(value, (int, long)):
            raise TypeError('value not an integer!')

        if not 0 <= value <= (2 ** self.strategy.word_size - 1):
            raise IndexError('value %d outside word size maximum of %d bits!'
                % (value, self.strategy.word_size))

        words = list(self.strategy.int_to_words(self.value))
        words[index] = value
        self.value = self.strategy.words_to_int(words)

    def __hex__(self):
        """
        @return: The value of this address as a network byte order hexadecimal
        number.
        """
        return hex(self.value).rstrip('L').lower()

    def __iadd__(self, i):
        """
        Increments network address by specified value.

        If the result exceeds address type maximum, it rolls around the
        minimum boundary.
        """
        try:
            new_value = self.value + i
            if new_value > self.strategy.max_int:
                self.value = new_value - (self.strategy.max_int + 1)
            else:
                self.value = new_value
        except TypeError:
            raise TypeError('Increment value must be an integer!')
        return self

    def __isub__(self, i):
        """
        Decrements network address by specified value.

        If the result exceeds address type minimum, it rolls around the
        maximum boundary.
        """
        try:
            new_value = self.value - i
            if new_value < self.strategy.min_int:
                self.value = new_value + (self.strategy.max_int + 1)
            else:
                self.value = new_value
        except TypeError:
            raise TypeError('Decrement value must be an integer!')
        return self

    def __eq__(self, other):
        """
        @return: C{True} if this network address instance has the same
            numerical value as another, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.value) == (other.addr_type, other.value):
                return True
        except AttributeError:
            pass

        return False

    def __ne__(self, other):
        """
        @return: C{True} if this network address instance does not have the
            same numerical value as another, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.value) != (other.addr_type, other.value):
                return True
        except AttributeError:
            pass

        return False

    def __lt__(self, other):
        """
        @return: C{True} if this network address instance has a lower
            numerical value than another, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.value) < (other.addr_type, other.value):
                return True
        except AttributeError:
            pass

        return False

    def __le__(self, other):
        """
        @return: C{True} if this network address instance has a lower or
            equivalent numerical value than another, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.value) <= (other.addr_type, other.value):
                return True
        except AttributeError:
            pass

        return False

    def __gt__(self, other):
        """
        @return: C{True} if this network address instance has a higher
            numerical value than another, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.value) > (other.addr_type, other.value):
                return True
        except AttributeError:
            pass

        return False

    def __ge__(self, other):
        """
        @return: C{True} if this network address instance has a higher or
            equivalent numerical value than another, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.value) >= (other.addr_type, other.value):
                return True
        except AttributeError:
            pass

        return False

#-----------------------------------------------------------------------------
class EUI(Addr):
    """
    EUI objects represent IEEE Extended Unique Identifiers. Input parsing is
    flexible, supporting EUI-48, EUI-64 and all MAC (Media Access Control)
    address flavours.
    """
    STRATEGIES = (ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_UNSPEC, AT_LINK, AT_EUI64)

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)

    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: an EUI/MAC address string or a network byte order
            integer.

        @param addr_type: (optional) the specific EUI address type (C{AT_LINK}
        or C{AT_EUI64}). If addr is an integer, this argument is mandatory.
        """
        super(EUI, self).__init__(addr, addr_type)

    def oui(self):
        """
        @return: The OUI (Organisationally Unique Identifier) for this EUI.
        """
        return '-'.join(["%02x" % i for i in self[0:3]]).upper()

    def ei(self):
        """
        @return: The EI (Extension Identifier) for this EUI.
        """
        if self.strategy == ST_EUI48:
            return '-'.join(["%02x" % i for i in self[3:6]]).upper()
        elif self.strategy == ST_EUI64:
            return '-'.join(["%02x" % i for i in self[3:8]]).upper()

    def eui64(self):
        """
        @return: The value of this EUI object as a new 64-bit EUI object.
            - If this object represents an EUI-48 it is converted to EUI-64 as
            per the standard.
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
        @return: An IPv6 L{IP} object initialised using the value of this
            L{EUI}.
                - B{See RFC 4921 for details}.
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
        addr = prefix + eui64
        return IP(addr)

    def info(self):
        """
        @return: A record dict containing IEEE registration details for this
            EUI (MAC-48) if available, None otherwise.
        """
        #   This import is placed here for efficiency. If you don't call this
        #   method, you don't take the import lag. Also gets around a nasty
        #   module dependency issue. Two birds, one stone ...
        info = mac_info(self)
#        del info['OUI']['id']  # Internal ID is not required externally.
        return info

#-----------------------------------------------------------------------------
class IP(Addr):
    """
    A class whose objects represent Internet Protocol network addresses. Both
    IPv4 and IPv6 are fully supported and also permit the inclusion of bitmask
    prefix or subnet mask address indicating the size/extent of the subnet,
    for example ::

        IPv4

        192.168.0.1/24
        192.168.0.1/255.255.255.0

        IPv6

        fe80::20f:1fff:fe12:e733/64
    """
    STRATEGIES = (ST_IPV4, ST_IPV6)
    ADDR_TYPES = (AT_UNSPEC, AT_INET, AT_INET6)
    TRANSLATE_STR = ''.join([chr(i) for i in range(256)])
    del i

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)
    prefixlen = PrefixLenDescriptor()

    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: an IPv4 or IPv6 address string with an optional subnet
        prefix or a network byte order integer.

        @param addr_type: (optional) the IP address type (C{AT_INET} or
        C{AT_INET6}). If L{addr} is an integer, this argument is mandatory.
        """
        prefixlen = None
        #   Check for prefix in address and split it out.
        try:
            if '/' in addr:
                (addr, prefixlen) = addr.split('/', 1)
        except TypeError:
            #   addr is an int - let it pass through.
            pass

        #   Call superclass constructor before processing subnet prefix to
        #   assign the strategyn object.
        super(IP, self).__init__(addr, addr_type)

        #   Set the subnet prefix.
        if prefixlen is None:
            self.prefixlen = self.strategy.width
        else:
            self.prefixlen = prefixlen

    def is_netmask(self):
        """
        @return: C{True} if this addr is a mask that would return a host id,
        C{False} otherwise.
        """
        #   There is probably a better way to do this.
        #   Change at will, just don't break the unit tests :-)
        bits = self.strategy.int_to_bits(self.value).replace('.', '')

        if bits[0] != '1':
            #   Fail fast, if possible.
            return False

        #   Trim our search a bit.
        bits = bits.lstrip('1')

        seen_zero = False
        for i in bits:
            if i == '0' and seen_zero is False:
                seen_zero = True
            elif i == '1' and seen_zero is True:
                return False

        return True

    def netmask_bits(self):
        """
        @return: If this address is a valid netmask, the number of non-zero
        bits are returned, otherwise it returns the width (in bits) for the
        given address type (IPv4: 32, IPv6: 128).
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
        """
        @return: The reverse DNS lookup string for this IP address.
        """
        return self.strategy.int_to_arpa(self.value)

    def is_hostmask(self):
        """
        @return: C{True} if this address is a mask that would return a host
        id, C{False} otherwise.
        """
        #   There is probably a better way to do this.
        #   Change at will, just don't break the unit tests :-)
        bits = self.strategy.int_to_bits(self.value).replace('.', '')

        if bits[0] != '0':
            #   Fail fast, if possible.
            return False

        #   Trim our search a bit.
        bits = bits.lstrip('0')

        seen_one = False
        for i in bits:
            if i == '1' and seen_one is False:
                seen_one = True
            elif i == '0' and seen_one is True:
                return False

        return True

    def hostname(self):
        """
        @return: Returns the FQDN for this IP address via a DNS query
            using gethostbyaddr() Python's socket module.
        """
        try:
            return _socket.gethostbyaddr(str(self))[0]
        except:
            return

    def cidr(self):
        """
        @return: A valid L{CIDR} object for this IP address.
        """
        hostmask = (1 << (self.strategy.width - self.prefixlen)) - 1
        start = (self.value | hostmask) - hostmask
        network = self.strategy.int_to_str(start)
        return CIDR("%s/%d" % (network, self.prefixlen))

    def ipv4(self):
        """
        @return: A new L{IP} object numerically equivalent this address.
            - If its address type is IPv4.
            - If object's address type is IPv6 and its value is mappable to
            IPv4, a new IPv4 L{IP} object is returned instead.
            - Raises an L{AddrConversionError} if IPv6 address is not mappable
            to IPv4.
        """
        ip_addr = None
        if self.addr_type == AT_INET:
            ip_addr = IP(self.value, AT_INET)
        elif self.addr_type == AT_INET6:
            words = self.strategy.int_to_words(self.value)
            if words[0:6] == (0,0,0,0,0,0):
                ip_addr = IP(self.value, AT_INET)
            elif words[0:6] == (0,0,0,0,0,65535):
                ip_addr = IP(self.value - 0xffff00000000, AT_INET)
            else:
                raise AddrConversionError('IPv6 address %s too large for ' \
                    'conversion to IPv4!' % self)
        return ip_addr

    def ipv6(self):
        """
        @return: A new L{IP} object numerically equivalent this address.
            - If object's address type is IPv6.
            - If object's address type is IPv4 a new IPv6 L{IP} object, as a
            IPv4 mapped address is returned instead. Uses the preferred IPv4
            embedded in IPv6 form - C{::ffff:x.x.x.x} ('mapped' address) over
            the (now deprecated) form - C{::x.x.x.x} ('compatible' address).
            B{See RFC 4921 for details}.
        """
        ip_addr = None
        if self.addr_type == AT_INET6:
            ip_addr = IP(self.value, AT_INET6)
        elif self.addr_type == AT_INET:
            ip_addr = IP(self.value, AT_INET6)
            ip_addr[5] = 0xffff
        return ip_addr

    def is_unicast(self):
        """
        @return: C{True} if this address is unicast, C{False} otherwise.
        """
        if self.is_multicast():
            return False
        return True

    def is_multicast(self):
        """
        @return: C{True} if this address is multicast, C{False} otherwise.
        """
        if self.addr_type == AT_INET:
            if 0 <= self.value <= (2 ** 32 - 1):
                return True
        elif  self.addr_type == AT_INET6:
            if 0 <= self.value <= (2 ** 128 - 1):
                return True
        return False

    def info(self):
        """
        @return: A record dict containing IANA registration details for this
            IP address if available, None otherwise.
        """
        #   This import is placed here for efficiency. If you don't call this
        #   method, you don't take the import lag. Also gets around a nasty
        #   module dependency issue. Two birds, one stone ...
        return ip_info(self)

    def __str__(self):
        """
        @return: The common string representation for this IP address.
        """
        return self.strategy.int_to_str(self.value)

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        if self.prefixlen == self.strategy.width:
            return "netaddr.address.%s('%s')" % (self.__class__.__name__,
                str(self))

        return "netaddr.address.%s('%s/%d')" % (self.__class__.__name__,
            str(self), self.prefixlen)

#-----------------------------------------------------------------------------
#   Address aggregate classes.
#-----------------------------------------------------------------------------

def nrange(start, stop, step=1, klass=None):
    """
    A generator producing sequences of network addresses based on start and
    stop values, in intervals of step.

    @param start: first network address as string or instance of L{Addr}
        (sub)class.

    @param stop: last network address as string or instance of L{Addr}
        (sub)class.

    @param step: (optional) size of step between addresses in range.
        Default is 1.

    @param klass: (optional) the class used to create objects returned.
    Default: L{Addr} class.

        - C{str} returns string representation of network address
        - C{int}, C{long} and C{hex} return expected values
        - L{Addr} (sub)class or duck type* return objects of that class. If
        you use your own duck class, make sure you handle both arguments
        C{(addr_value, addr_type)} passed to the constructor.
    """
    if not issubclass(start.__class__, Addr):
        if isinstance(start, (str, unicode)):
            start = Addr(start)
        else:
            raise TypeError('start is not recognised address in string ' \
                'format or an that is a (sub)class of Addr!')
    else:
        #   Make klass the same class as start object.
        if klass is None:
            klass = start.__class__

    if not issubclass(stop.__class__, Addr):
        if isinstance(stop, (str, unicode)):
            stop = Addr(stop)
        else:
            raise TypeError('stop is not recognised address in string ' \
                'format or an that is a (sub)class of Addr!')

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
    start_klass = start.__class__
    start = int(start)
    stop = int(stop)

    if step < 0:
        negative_step = True

    index = start - step

    #   Set default klass value.
    if klass is None:
        klass = Addr

    if klass in (int, long, hex):
        #   Yield network address integer values.
        while True:
            index += step
            if negative_step:
                if not index >= stop:
                    return
            else:
                if not index <= stop:
                    return
            yield klass(index)
    elif klass in (str, unicode):
        #   Yield address string values.
        while True:
            index += step
            if negative_step:
                if not index >= stop:
                    return
            else:
                if not index <= stop:
                    return
            yield str(start_klass(index, addr_type))
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

            yield klass(index, addr_type)

#-----------------------------------------------------------------------------
class AddrRange(object):
    """
    A block of contiguous network addresses bounded by an arbitrary start and
    stop address. There is no requirement that they fall on strict bit mask
    boundaries, unlike L{CIDR} addresses.

    This is the only network address aggregate supporting all network address
    types. Most AddrRange subclasses usually only support a subset of address
    types.

    A sequence of address ranges sort first by address type then by magnitude.
    So for a list containing ranges of all currently supported address types,
    IPv4 ranges come first, then IPv6, EUI-48 and lastly EUI-64.
    """
    STRATEGIES = (ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_UNSPEC, AT_INET, AT_INET6, AT_LINK, AT_EUI64)

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)
    first = AddrValueDescriptor('first')
    last = AddrValueDescriptor('last')
    klass = KlassDescriptor(Addr)

    def __init__(self, first, last, klass=Addr):
        """
        Constructor.

        @param first: start address for this network address range.

        @param last: stop address for this network address range.

        @param klass: (optional) class used to create each object returned.
            Default: L{Addr()} objects. See L{nrange()} documentations for
            additional details on options.
        """
        self.addr_type = AT_UNSPEC
        self.first = first
        self.last = last
        if self.last < self.first:
            raise IndexError('start address is greater than stop address!')
        self.klass = klass

    def __hash__(self):
        """
        @return: The hash of this address range. Allow them to be used in sets
            and as keys in dictionaries.
        """
        return hash((self.first, self.last, self.addr_type))

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
            raise IndexError("range contains more than 2^31 addresses! " \
                "Use size() method instead.")
        return size

    def size(self):
        """
        @return: The total number of network addresses in this range.
            - Use this method in preference to L{__len__()} when size of
            ranges exceeds C{2^31} addresses.
        """
        return self.last - self.first + 1

    def data_flavour(self, int_addr):
        """
        @param int_addr: an network address as a network byte order integer.

        @return: a network address in whatever 'flavour' is required based on
        the value of the klass property.
        """
        if self.klass in (str, unicode):
            return self.strategy.int_to_str(int_addr)
        elif self.klass in (int, long, hex):
            return self.klass(int_addr)
        else:
            return self.klass(int_addr, self.addr_type)

    def __getitem__(self, index):
        """
        @return: The network address(es) in this address range indicated by
            index/slice. Slicing objects can produce large sequences so
            generator objects are returned instead to the usual sequences.
            Wrapping a raw slice with C{list()} or C{tuple()} may be required
            dependent on context.
        """

        if isinstance(index, (int, long)):
            if (- self.size()) <= index < 0:
                #   negative index.
                return self.data_flavour(self.last + index + 1)
            elif 0 <= index <= (self.size() - 1):
                #   Positive index or zero index.
                return self.data_flavour(self.first + index)
            else:
                raise IndexError('index out range for address range size!')
        elif isinstance(index, slice):
            #   slices
            #FIXME: IPv6 breaks the .indices() method on the slice object
            #   spectacularly. We'll have to work out the start, stop and
            #   step ourselves :-(
            #
            #   see PySlice_GetIndicesEx function in Python SVN repository for
            #   implementation details :-
            #   http://svn.python.org/view/python/trunk/Objects/sliceobject.c
            (start, stop, step) = index.indices(self.size())

            start_addr = Addr(self.first + start, self.addr_type)
            end_addr = Addr(self.first + stop - step, self.addr_type)
            return nrange(start_addr, end_addr, step, klass=self.klass)
        else:
            raise TypeError('unsupported type %r!' % index)

    def __iter__(self):
        """
        @return: An iterator object providing access to all network addresses
            within this range.
        """
        start_addr = Addr(self.first, self.addr_type)
        end_addr = Addr(self.last, self.addr_type)
        return nrange(start_addr, end_addr, klass=self.klass)

    def __contains__(self, addr):
        """
        @param addr: object of Addr/AddrRange (sub)class or a network address
            string to be compared.

        @return: C{True} if given address or range falls within this range,
            C{False} otherwise.
        """
        if isinstance(addr, (str, unicode)):
            #   string address or address range.
            c_addr = Addr(addr)
            if c_addr.addr_type == self.addr_type:
                if self.first <= int(c_addr) <= self.last:
                    return True
        elif issubclass(addr.__class__, Addr):
            #   Single value check.
            if self.first <= int(addr) <= self.last:
                return True
        elif issubclass(addr.__class__, AddrRange):
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
            if (self.addr_type, self.first, self.last) == \
               (other.addr_type, other.first, other.last):
                return True
        except AttributeError:
            pass

        return False

    def __ne__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are not the same as
            other, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.first, self.last) != \
               (other.addr_type, other.first, other.last):
                return True
        except AttributeError:
            pass

        return False

    def __lt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are less than other,
            C{False} otherwise.
        """
        try:
            if (self.addr_type, self.first, self.last) < \
               (other.addr_type, other.first, other.last):
                return True
        except AttributeError:
            pass

        return False

    def __le__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are less or equal to
            other, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.first, self.last) <= \
               (other.addr_type, other.first, other.last):
                return True
        except AttributeError:
            pass

        return False

    def __gt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are greater than
            other, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.first, self.last) > \
               (other.addr_type, other.first, other.last):
                return True
        except AttributeError:
            pass

        return False

    def __ge__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are greater or equal
            to other, C{False} otherwise.
        """
        try:
            if (self.addr_type, self.first, self.last) >= \
               (other.addr_type, other.first, other.last):
                return True
        except AttributeError:
            pass

        return False

    def __iadd__(self, i):
        """
        Increments start and end addresses of this range by the current size.

        If the result exceeds address type range for the address type an
        IndexError is raised.
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

        If the result less than zero an IndexError is raised.
        """
        try:
            new_first = self.first - (self.size() * i)
            new_last = self.last - (self.size() * i)
        except TypeError:
            raise TypeError('Decrement value must be an integer!')

        if new_last < self.strategy.min_int:
            raise IndexError('Invalid decrement is outside address boundary!')

        self.first = new_first
        self.last = new_last

        return self

    def __str__(self):
        return "%s;%s" % (self.strategy.int_to_str(self.first),
                          self.strategy.int_to_str(self.last))

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s(%r, %r)" % (self.__class__.__name__,
            self.strategy.int_to_str(self.first),
            self.strategy.int_to_str(self.last))

#-----------------------------------------------------------------------------
class IPRange(AddrRange):
    """
    A block of contiguous IP addresses bounded by an arbitrary start and stop
    address. There is no requirement that they fall on strict bit mask
    boundaries, unlike L{CIDR} addresses.

    A sequence of IPRange objects sort by IPv4 first, followed by IPv6.
        """
    STRATEGIES = (ST_IPV4, ST_IPV6)
    ADDR_TYPES = (AT_UNSPEC, AT_INET, AT_INET6)

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)
    first = AddrValueDescriptor('first')
    last = AddrValueDescriptor('last')
    klass = KlassDescriptor(IP)

    def __init__(self, first, last, klass=IP):
        """
        Constructor.

        @param first: start address for this IP address range.

        @param last: stop address for this IP address range.

        @param klass: (optional) class used to create each object returned.
            Default: L{IP()} objects. See L{nrange()} documentations for
            additional details on options.
        """
        super(IPRange, self).__init__(first, last, klass)

    def iprange(self):
        """
        @return: A valid L{IPRange} object for this address range.
        """
        iprange = IPRange(self.strategy.int_to_str(self.first),
                          self.strategy.int_to_str(self.last))
        if self.klass == str:
            return str(iprange)
        return cidr

    def cidr(self):
        """
        @return: A valid L{CIDR} object for this address range. If conversion
            fails an L{AddrConversionError} is raised as not all wildcards
            ranges are valid CIDR ranges.
        """
        raise RuntimeError('TODO')

    def wildcard(self):
        """
        @return: A L{Wildcard} object equivalent to this CIDR.
            - If CIDR was initialised with C{klass=str} a wildcard string is
            returned, in all other cases a L{Wildcard} object is returned.
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

        if self.klass == str:
            return wildcard

        return Wildcard(wildcard)

    def issubnet(self, other):
        """
        @return: True if other's boundary is equal to or within this range.
            False otherwise.
        """
        if not isinstance(other, IPRange):
            raise TypeError('Invalid type!')

        if self.addr_type != other.addr_type:
            raise TypeError('Ranges must be the same address type!')

        if self.first >= other.first and self.last <= other.last:
            return True

        return False

    def issupernet(self, other):
        """
        @return: True if other's boundary is equal to or contains this range.
            False otherwise.
        """
        if not isinstance(other, IPRange):
            raise TypeError('Invalid type!')

        if self.addr_type != other.addr_type:
            raise TypeError('Ranges must be the same address type!')

        if self.first <= other.first and self.last >= other.last:
            return True

        return False

    def adjacent(self, other):
        """
        @return: True if other's boundary touches the boundary of this
            address range, False otherwise.
        """
        if not isinstance(other, IPRange):
            raise TypeError('Invalid type!')

        if self.addr_type != other.addr_type:
            raise TypeError('Ranges must be the same address type!')

        #   Left hand side of this address range.
        if self.first == (other.last + 1):
            return True

        #   Right hand side of this address range.
        if self.last == (other.first - 1):
            return True

        return False

    def overlaps(self, other):
        """
        @return: True if other's boundary crosses the boundary of this address
            range, False otherwise.
        """
        if not isinstance(other, IPRange):
            raise TypeError('Invalid type!')

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
        return "('%s', '%s')" % (self.strategy.int_to_str(self.first),
                                 self.strategy.int_to_str(self.last))

#-----------------------------------------------------------------------------
class CIDR(IPRange):
    """
    A block of contiguous IPv4 or IPv6 network addresses defined by a base
    network address and a bitmask prefix or subnet mask address indicating the
    size/extent of the subnet.

    By default, this class does not allow any non-zero bits to be set right
    of the bitmask when it is applied to the supplied base address. Doing so
    raises an L{AddrFormatError} exception. However, it is now configurable
    and will allow a less strict base address if you ask for one. Be aware
    though that the bitmask will be applied to the base address and and
    trailing non-zero bits removed losing the original address. It will *not*
    be preserved!

    Contrast this behaviour with the L{IP} class which is less strict and has
    a cidr() method for returning CIDR objects without any loss of
    information.

    Examples of supported formats :-

        1. CIDR address format - C{<address>/<mask_length>}::

            192.168.0.0/16
            fe80::/64

        2. Address and subnet mask combo ::

            192.168.0.0/255.255.0.0 == 192.168.0.0/16
            fe80::/ffff:ffff:ffff:ffff::  == fe80::/64

        3. Partial or abbreviated formats (IPv4 only). Prefixes may be omitted
           and in this case older class-based default prefixes apply ::

            10          ==  10.0.0.0/8
            10.0        ==  10.0.0.0/8
            10/8        ==  10.0.0.0/8

            128         ==  128.0.0.0/16
            128.0       ==  128.0.0.0/16
            128/16      ==  128.0.0.0/16

            192         ==  10.0.0.0/24
            192.168.0   ==  192.168.0.0/24
            192.168/16  ==  192.168.0.0/16
    """
    STRATEGIES = (ST_IPV4, ST_IPV6)
    ADDR_TYPES = (AT_UNSPEC, AT_INET, AT_INET6)

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)
    prefixlen = PrefixLenDescriptor('CIDR')
    klass = KlassDescriptor(IP)

    def abbrev_to_verbose(abbrev_cidr):
        """
        A statis method that converts abbreviated CIDR addresses into their
        verbose form.

        @param abbrev_cidr: an abbreviated CIDR network address.

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
            prefix = 32     #   Host address default.
            if not 0 <= octet <= 255:
                raise IndexError('Invalid octet: %r!' % octet)
            if 0 <= octet <= 127:
                #   Class A
                prefix = 8
            elif 128 <= octet <= 191:
                #   Class B
                prefix = 16
            elif 192 <= octet <= 223:
                #   Class C
                prefix = 24
            elif octet == 224:
                #   Class D (multicast)
                prefix = 4
            elif 225 <= octet <= 239:
                prefix = 8
            return prefix

        start = ''
        tokens = []
        prefix = None

    #FIXME:    #   Check for IPv4 mapped IPv6 addresses.
        if isinstance(abbrev_cidr, (str, unicode)):
        ################
            #   Don't support IPv6 for now...
            if ':' in abbrev_cidr:
                return None
        ################
    #FIXME:        if abbrev_cidr.startswith('::ffff:'):
    #FIXME:            abbrev_cidr = abbrev_cidr.replace('::ffff:', '')
    #FIXME:            start = '::ffff:'
    #FIXME:            if '/' not in abbrev_cidr:
    #FIXME:                prefix = 128
    #FIXME:        elif abbrev_cidr.startswith('::'):
    #FIXME:            abbrev_cidr = abbrev_cidr.replace('::', '')
    #FIXME:            start = '::'
    #FIXME:            if '/' not in abbrev_cidr:
    #FIXME:                prefix = 128
        ################

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

            if 1 <= len(tokens) <= 4:
                for i in range(4 - len(tokens)):
                    tokens.append('0')
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

    def supernet(addrs):
        """
        Accepts a sequence of IP addresses and/or CIDRs, Wildcards and
        IPRanges returning a single CIDR that is large enough to span the
        lowest and highest addresses in the sequence.
        """
        if not isinstance(addrs, (list, tuple)):
            raise TypeError('argument must be a sequence type (list/tuple)!')

        if not len(addrs) > 0:
            raise TypeError('sequence must contain 1 or more elements!')

        #   Detect type of string address or address range and create the
        #   equivalent instance.
        for i, addr in enumerate(addrs):
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

        addr_type = addrs[0].addr_type
        strategy = AT_STRATEGIES[addr_type]

        ip1 = IP(strategy.max_int, addr_type)
        ip2 = IP(strategy.min_int, addr_type)

        #   Discover the lowest and highest address range boundaries.
        for addr in addrs:
            if isinstance(addr, (CIDR, Wildcard)):
                if addr.addr_type != addr_type:
                    raise TypeError('Sequence cannot contain multiple ' \
                        'address types!')
                if addr.first < ip1.value:
                    ip1.value = addr.first
                if addr.last > ip2.value:
                    ip2.value = addr.last
            elif isinstance(addr, IP):
                if addr.addr_type != addr_type:
                    raise TypeError('Sequence cannot contain multiple ' \
                        'address types!')
                if addr.value < ip1.value:
                    ip1.value = addr.value
                if addr.value > ip2.value:
                    ip2.value = addr.value
            else:
                raise TypeError('element %r is not a supported type!' % addr)

        #   Compute CIDR to span the extent of the list provided.
        cidr = ip1.cidr()
        while cidr.prefixlen > 0:
            if ip2 in cidr:
                break
            cidr.prefixlen -= 1

        return cidr

    abbrev_to_verbose = staticmethod(abbrev_to_verbose)
    supernet = staticmethod(supernet)

    def __init__(self, cidr, klass=IP, strict_bitmask=True):
        """
        Constructor.

        @param cidr: a valid IPv4/IPv6 CIDR address or abbreviated IPv4
            network address.

        @param klass: (optional) type, BIF or class used to create each
            object returned. Default: L{IP} class. See L{nrange()}
            documentations for additional details on options.

        @param strict_bitmask: (optional) performs a test to ensure
            there are no non-zero bits to the right of the subnet mask or
            prefix when it is applied to the base address. (default: True)
        """
        cidr_arg = cidr     #   Keep a copy of original argument.

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
            raise AddrFormatError('%r is not a recognised CIDR!' % cidr_arg)

        first = IP(network)
        self.strategy = first.strategy
        self.prefixlen = mask

        strategy = first.strategy
        addr_type = strategy.addr_type

        hostmask = (1 << (strategy.width - self.prefixlen)) - 1
        netmask = strategy.max_int ^ hostmask

        last = IP(first.value | hostmask, addr_type)

        if strict_bitmask:
            #   Enable on strict CIDR checking.
            host = (first.value | netmask) - netmask
            if host != 0:
                raise ValueError('%s contains non-zero bits right of the ' \
                    '%d-bit mask! Did you mean %s instead?' \
                        % (first, self.prefixlen,
                           strategy.int_to_str(int(last) - hostmask)))
        else:
            #   Loose CIDR checking.
            first.value = strategy.int_to_str(int(last) - hostmask)

        super(CIDR, self).__init__(first, last, klass)

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
        if self.klass is str:
            return [str(cidr) for cidr in cidrs]

        return cidrs

    def __add__(self, other):
        """
        Add another CIDR to this one returning a 'supernet' that will contain
        both addresses.

        @param other: a CIDR object.

        @return: A new (potentially larger) CIDR object.
        """
        cidr = CIDR.supernet([self, other])
        if self.klass is str:
            return str(cidr)
        return cidr

    def netmask(self):
        """
        @return: The subnet mask address of this CIDR range.
        """
        hostmask = (1 << (self.strategy.width - self.prefixlen)) - 1
        netmask = self.strategy.max_int ^ hostmask
        return self.data_flavour(netmask)

    def hostmask(self):
        """
        @return: The host mask address of this CIDR range.
        """
        hostmask = (1 << (self.strategy.width - self.prefixlen)) - 1
        return self.data_flavour(hostmask)

    def __str__(self):
        return "%s/%s" % (self.strategy.int_to_str(self.first), self.prefixlen)

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s('%s/%d')" % (self.__class__.__name__,
            self.strategy.int_to_str(self.first), self.prefixlen)

#-----------------------------------------------------------------------------
class Wildcard(IPRange):
    """
    A block of contiguous IPv4 network addresses defined using a wildcard
    style syntax.

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
        I{Wildcard ranges are not directly equivalent to CIDR ranges as they
        can represent address ranges that do not fall on strict bit mask
        boundaries.}

        I{All CIDR ranges can always be represented as wildcard ranges but the
        reverse isn't true in every case.}
    """
    STRATEGIES = (ST_IPV4,)
    ADDR_TYPES = (AT_UNSPEC, AT_INET)

    #   Descriptor registrations.
    strategy = StrategyDescriptor(STRATEGIES)
    addr_type = AddrTypeDescriptor(ADDR_TYPES)
    klass = KlassDescriptor(IP)

    def is_valid(wildcard):
        """
        A static method that validates wildcard address ranges.

        @param wildcard: an IPv4 wildcard address.

        @return: True if wildcard address is valid, False otherwise.
        """
        #TODO: Add support for partial wildcards
        #TODO: e.g. 192.168.*.* == 192.168.*
        #TODO:      *.*.*.*     == *
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

    def __init__(self, wildcard, klass=IP):
        """
        Constructor.

        @param wildcard: a valid IPv4 wildcard address

        @param klass: (optional) class used to create each return object.
            Default: L{IP} objects. See L{nrange()} documentations for
            additional details on options.
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
        super(Wildcard, self).__init__(first, last, klass=klass)

        if self.addr_type != AT_INET:
            raise AddrFormatError('Wildcard syntax only supports IPv4!')

    def __add__(self, other):
        """
        Add another Wildcard, CIDR or IP to this Wildcard object.

        @param other: a Wildcard, CIDR or IP object that is either adjacent to
            or intersects with this address.

        @return: A new (most likely larger) Wildcard object. Raises an
            Exception if other is not adjacent or intersects with this
            Wildcard object.
        """
        raise NotImplementedError('TODO')

    def __sub__(self, other):
        """
        Subtract a Wildcard, CIDR or IP from this Wildcard object.

        @param other: a Wildcard, CIDR or IP object.

        @return: A list of either one or two Wildcard objects remaining after
        subtracting C{other} from C{self}.
        """
        raise NotImplementedError('TODO')

    def cidr(self):
        """
        @return: A valid L{CIDR} object for this wildcard. If conversion fails
            an L{AddrConversionError} is raised as not all wildcards ranges are
            valid CIDR ranges.
        """
        #FIXME: This method should be removed and replace with a more generic
        #FIXME: version defined in superclass IPRange().
        size = self.size()

        if size & (size - 1) != 0:
            raise AddrConversionError('%s cannot be represented with CIDR' \
                % str(self))

        (mantissa, exponent) = _math.frexp(size)

        #   The check below is only valid up to around 2^53 after which
        #   rounding on +1 or -1 starts to bite and would cause this logic to
        #   fail. Fine for our purposes here as we only envisage supporting
        #   values up to 2^32 (IPv4), for now at least.
        if mantissa != 0.5:
            raise AddrConversionError('%s cannot be represented with CIDR' \
                % str(self))

        prefix = 32 - int(exponent - 1)
        network = self.strategy.int_to_str(self.first)
        try:
            cidr = CIDR("%s/%d" % (network, prefix))
        except:
            raise AddrConversionError('%s cannot be represented with CIDR' \
                % str(self))

        if self.klass == str:
            return str(cidr)

        return cidr

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
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s(%r)" % (self.__class__.__name__, str(self))


#-----------------------------------------------------------------------------
class IPRangeSet(set):
    """
    A customised Python set class that deals with IP addresses and CIDRs. Any
    object passed in that is not a CIDR will be converted into one.

    """
    def __init__(self, cidrs):
        """
        Constructor.

        @param cidrs: A list of CIDR objects used to pre-populate the set.
            Individual CIDR object can be added and removed after
            instantiation with the usual set methods, add() and remove().

        """
        for cidr in cidrs:
            if isinstance(cidr, IP):
                self.add(cidr.cidr())
            if isinstance(cidr, str):
                try:
                    self.add(CIDR(cidr))
                except:
                    pass
                try:
                    ip = IP(cidr)
                    self.add(ip.cidr())
                except:
                    pass
                try:
                    wildcard = Wildcard(cidr)
                    try:
                        self.add(wildcard.cidr())
                    except:
                        self.add(wildcard)
                except:
                    pass
            else:
                self.add(cidr)

    def __contains__(self, other):
        """
        @return: True if C{other} CIDR object matches any of the members in
            this CIDRSet, False otherwise.

        """
        for cidr in self:
            if other in cidr:
                return True

    def any_match(self, other):
        """
        @param other: An IP or CIDR object.

        @return: The first CIDR object that matches the C{other} CIDR object
            from any of the members in this CIDRSet, None otherwise.

        """
        for cidr in self:
            if other in cidr:
                return cidr

    def all_matches(self, other):
        """
        @param other: An IP or CIDR object.

        @return: All CIDR objects matching the C{other} CIDR object from this
        CIDRSet, an empty list otherwise.
        """
        cidrs = []
        for cidr in self:
            if other in cidr:
                cidrs.append(cidr)
        return cidrs

    def min_match(self, other):
        """
        @param other: An IP or CIDR object.

        @return: The smallest CIDR matching the C{other} CIDR object from this
        CIDRSet, None otherwise.
        """
        cidrs = self.all_matches(other)
        cidrs.sort()
        return cidrs[0]


    def max_match(self, other):
        """
        @param other: An IP or CIDR object.

        @return: The largest CIDR matching the C{other} CIDR object from this
        CIDRSet, None otherwise.

        """
        cidrs = self.all_matches(other)
        cidrs.sort()
        return cidrs[-1]

#-----------------------------------------------------------------------------
def read_caches():
    """
    Read from caches and update module variables with information retrieved.
    """
    from external import ShelveReader, IANA_IPV4_PATH, IANA_IPV6_PATH, \
        IANA_MULTICAST_PATH, IEEE_OUI_PATH

    #   Populate IPv4 lookup.
    ipv4 = ShelveReader(IANA_IPV4_PATH)
    for prefix, data in ipv4.db.items():
        cidr = CIDR(prefix)
        EXT_LOOKUP['IPv4'][cidr] = data

    #   Populate IPv6 lookup.
    ipv6 = ShelveReader(IANA_IPV6_PATH)
    for prefix, data in ipv6.db.items():
        cidr = CIDR(prefix)
        EXT_LOOKUP['IPv6'][cidr] = data

    #   Populate IPv4 multicast lookup.
    mcast = ShelveReader(IANA_MULTICAST_PATH)
    for ip_lookup, data in mcast.db.items():
        iprange = None
        if '-' in ip_lookup:
            (first, last) = ip_lookup.split('-')
            iprange = IPRange(first, last)
        else:
            iprange = IPRange(ip_lookup, ip_lookup)
        EXT_LOOKUP['multicast'][iprange] = data

    #   Populate OUI lookup.
    EXT_LOOKUP['OUI'] = ShelveReader(IEEE_OUI_PATH)

#   On module import, read shelve data and populate module level lookups.
read_caches()

#-----------------------------------------------------------------------------
def cidr_set():
    c1 = IPRangeSet([
        CIDR('192.168.0.0/28'),
        CIDR('192.168.0.32/28'),
    ])
    c2 = IPRangeSet([
        CIDR('192.168.0.0/28'),
        CIDR('192.168.0.0/24'),
        IP('192.168.0.5'),
        CIDR('192.168.0.16/28'),
        CIDR('192.168.0.32/28'),
    ])

    c3 = IPRangeSet([
        '10.0.168.0-79',
        '10.0.168.88-175',
        '10.0.168.184-255',
        '10.0.169.*',
        '10.0.172.0-175',
        '10.0.172.192-255',
        '10.0.173.*',
        '10.0.152.0-143',
        '10.0.152.152-207',
        '10.0.152.224-227',
        '10.0.152.232-255',
        '10.0.153.0-31',
        '10.0.153.40-79',
        '10.0.153.112-255',
        '10.0.154.0-207',
        '10.0.154.224-255',
        '10.0.155.0-79',
        '10.0.155.96-127',
        '10.0.46.0-63',
        '10.0.46.128-191',
        '10.0.48.0-63',
        '10.0.48.128-191',
        '10.0.252.0-63',
        '10.0.49.*',
        '10.0.206.0-111',
        '10.0.206.128-255',
        '10.0.163.*',
        '10.0.170.16-255',
        '10.0.171.*',
        '10.0.226.0-127',
        '10.0.228.0-127',
    ])

    print c1.issubset(c2)
    print c2.issuperset(c1)
    print c1.intersection(c2)
    print c1.union(c2)
#    print "%r" % c2.any_match(IP('10.0.0.1'))
#    print c2.all_matches(CIDR('10.0.0.5/32'))

    for cidr in sorted(c3):
        print "%r" % cidr

    for i in c1:
        print i

#-----------------------------------------------------------------------------
def add_sub_wildcard():
    wc = Wildcard('192.168.0.15-250')
    print wc
    print wc - Wildcard('192.168.0.235-240')

#-----------------------------------------------------------------------------
def cidr_addition_and_supernet():
    l = ['::', '::255.255.255.255']
    print l
    c = CIDR.supernet(l)
    print c, c[0], c[-1], c.size()

    print "%r" % (CIDR('192.168.0.0/24', klass=str) + CIDR('192.168.255.0/24'))

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #cidr_set()
    #add_sub_wildcard()
    #cidr_addition_and_supernet()

    #print Wildcard('192.168.0.32-63').overlaps(Wildcard('192.168.0.33-35'))
    pass
