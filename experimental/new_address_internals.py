#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
This is the new proposal for internals of Addr and AddrRange base classes to
facilitate better policing of assignments and simpler logic and cleaner code
in sub classes.

This will make up part of netaddr release 0.5

NOW MERGED WITH address.py. NO FURTHER EDITS TO THIS FILE REQUIRED!
"""
import math as _math
import socket as _socket


from netaddr import AddrFormatError, AddrConversionError, AT_UNSPEC, \
    AT_INET, AT_INET6, AT_LINK,  AT_EUI64

from netaddr.strategy import ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64, \
    AddrStrategy

#   *** To be added to netaddr.__init__.py ***
AT_STRATEGIES = {
    #   Address Type : Strategy Object.
    AT_UNSPEC   : None,
    AT_INET     : ST_IPV4,
    AT_INET6    : ST_IPV6,
    AT_LINK     : ST_EUI48,
    AT_EUI64    : ST_EUI64,
}

#   *** To be added to netaddr.__init__.py ***
AT_NAMES = {
    #   Address Type : Strategy Object.
    AT_UNSPEC   : 'unspecified',
    AT_INET     : 'IPv4',
    AT_INET6    : 'IPv6',
    AT_LINK     : 'MAC',
    AT_EUI64    : 'EUI-64',
}

import unittest

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
    #   Class properties.
    STRATEGIES = (ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_INET, AT_INET6, AT_LINK, AT_EUI64)

    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: the string form of a network address, or a network byte
            order integer within the supported range for the address type.

        @param addr_type: (optional) the network address type. If addr is an
            integer, this argument becomes mandatory.
        """
        #   NB - These should only be are accessed via property() methods.
        self._strategy = None
        self._value = None
        self._addr_type = None

        self.addr_type = addr_type
        self.value = addr

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   START - managed attributes.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def _get_addr_type(self):
        return self._addr_type

    def _set_addr_type(self, val):
        if val == AT_UNSPEC:
            pass
        else:
            #   Validate addr_type and keep in sync with strategy.
            if val not in self.__class__.ADDR_TYPES:
                raise ValueError('addr_type %r is invalid for objects of ' \
                    'the %s() class!' % (val, self.__class__.__name__))
            self._strategy = AT_STRATEGIES[val]

        self._addr_type = val

    def _get_value(self):
        return self._value

    def _set_value(self, val):
        #   Select a strategy object for this address.
        if self._addr_type == AT_UNSPEC:
            for strategy in self.__class__.STRATEGIES:
                if strategy.valid_str(val):
                    self.strategy = strategy
                    break

        #   Make sure we picked up a strategy object.
        if self._strategy is None:
            raise AddrFormatError('%r is not a recognised address ' \
                'format!' % val)

        #   Calculate and validate the value for this address.
        if isinstance(val, (str, unicode)):
            val = self._strategy.str_to_int(val)
        elif isinstance(val, (int, long)):
            if not self._strategy.valid_int(val):
                raise OverflowError('value %r cannot be represented ' \
                    'in %d bit(s)!' % (val, self._strategy.width))
        self._value = val

    def _get_strategy(self):
        return self._strategy

    def _set_strategy(self, val):
        #   Validate strategy and keep in sync with addr_type.
        if not issubclass(val.__class__, AddrStrategy):
            raise TypeError('%r is not an object of (sub)class of ' \
                'AddrStrategy!' % val)
        self._addr_type = val.addr_type

        self._strategy = val

    #   Initialise accessors and tidy the namespace.
    value = property(_get_value, _set_value, None,
        """
        The value of this address object (a network byte order integer).
        """)
    del _get_value, _set_value

    addr_type = property(_get_addr_type, _set_addr_type, None,
        """
        An integer value indicating the specific type of this address object.
        """)
    del _get_addr_type, _set_addr_type

    strategy = property(_get_strategy, _set_strategy, None,
        """
        An instance of AddrStrategy (sub)class.
        """)
    del _get_strategy, _set_strategy

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   END - managed attributes.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def __int__(self):
        """
        @return: The value of this address as an network byte order integer.
        """
        return self._value

    def __long__(self):
        """
        @return: The value of this address as an network byte order integer.
        """
        return self._value

    def __str__(self):
        """
        @return: The common string representation for this address type.
        """
        return self._strategy.int_to_str(self._value)

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
        return self._strategy.int_to_bits(self._value)

    def __len__(self):
        """
        @return: The size of this address (in bits).
        """
        return self._strategy.width

    def __iter__(self):
        """
        @return: An iterator over individual words in this address.
        """
        return iter(self._strategy.int_to_words(self._value))

    def __getitem__(self, index):
        """
        @return: The integer value of the word indicated by index. Raises an
            C{IndexError} if index is wrong size for address type. Full
            slicing is also supported.
        """
        if isinstance(index, (int, long)):
            #   Indexing, including negative indexing goodness.
            word_count = self._strategy.word_count
            if not (-word_count) <= index <= (word_count - 1):
                raise IndexError('index out range for address type!')
            return self._strategy.int_to_words(self._value)[index]
        elif isinstance(index, slice):
            #   Slicing baby!
            words = self._strategy.int_to_words(self._value)
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

        if not 0 <= index <= (self._strategy.word_count - 1):
            raise IndexError('index %d outside address type boundary!' % index)

        if not isinstance(value, (int, long)):
            raise TypeError('value not an integer!')

        if not 0 <= value <= (2 ** self._strategy.word_size - 1):
            raise IndexError('value %d outside word size maximum of %d bits!'
                % (value, self._strategy.word_size))

        words = list(self._strategy.int_to_words(self._value))
        words[index] = value
        self.setvalue(self._strategy.words_to_int(words))

    def __hex__(self):
        """
        @return: The value of this address as a network byte order hexadecimal
        number.
        """
        return hex(self._value).rstrip('L').lower()

    def __iadd__(self, i):
        """
        Increments network address by specified value.

        If the result exceeds address type maximum, it rolls around the
        minimum boundary.
        """
        try:
            new_value = self._value + i
            if new_value > self._strategy.max_int:
                self._value = new_value - (self._strategy.max_int + 1)
            else:
                self._value = new_value
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
            new_value = self._value - i
            if new_value < self._strategy.min_int:
                self.value = new_value + (self._strategy.max_int + 1)
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
        if (self._addr_type, self._value) == (other._addr_type, other._value):
            return True
        return False

    def __ne__(self, other):
        """
        @return: C{True} if this network address instance does not have the
            same numerical value as another, C{False} otherwise.
        """
        if (self._addr_type, self._value) != (other._addr_type, other._value):
            return True
        return False

    def __lt__(self, other):
        """
        @return: C{True} if this network address instance has a lower
            numerical value than another, C{False} otherwise.
        """
        if (self._addr_type, self._value) < (other._addr_type, other._value):
            return True
        return False

    def __le__(self, other):
        """
        @return: C{True} if this network address instance has a lower or
            equivalent numerical value than another, C{False} otherwise.
        """
        if (self._addr_type, self._value) <= (other._addr_type, other._value):
            return True
        return False

    def __gt__(self, other):
        """
        @return: C{True} if this network address instance has a higher
            numerical value than another, C{False} otherwise.
        """
        if (self._addr_type, self._value) > (other._addr_type, other._value):
            return True
        return False

    def __ge__(self, other):
        """
        @return: C{True} if this network address instance has a higher or
            equivalent numerical value than another, C{False} otherwise.
        """
        if (self._addr_type, self._value) >= (other._addr_type, other._value):
            return True
        return False

#-----------------------------------------------------------------------------
class EUI(Addr):
    """
    EUI objects represent IEEE Extended Unique Identifiers. Input parsing is
    flexible, supporting EUI-48, EUI-64 and all MAC (Media Access Control)
    address flavours.
    """
    #   Class properties.
    STRATEGIES = (ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_LINK, AT_EUI64)

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
        if self._addr_type == AT_LINK:
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

        if self._addr_type == AT_LINK:
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

#-----------------------------------------------------------------------------
class IP(Addr):
    """
    A class whose objects represent Internet Protocol network addresses. Both
    IPv4 and IPv6 are fully supported and include an optional subnet bit mask
    prefix, for example ::

        192.168.0.1/24
        fe80::20f:1fff:fe12:e733/64

    This class B{does not make a requirement to omit non-zero bits to the
    right of the subnet prefix} when it is applied to the address.

    See the L{CIDR()} class if you require B{*strict*} subnet prefix checking.
    """
    #   Class properties.
    STRATEGIES = (ST_IPV4, ST_IPV6)
    ADDR_TYPES = (AT_INET, AT_INET6)

    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: an IPv4 or IPv6 address string with an optional subnet
        prefix or a network byte order integer.

        @param addr_type: (optional) the IP address type (C{AT_INET} or
        C{AT_INET6}). If L{addr} is an integer, this argument is mandatory.
        """
        #   NB - This should only be are accessed via property() methods.
        self._prefixlen = None

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
            self._prefixlen = self._strategy.width
        else:
            self.prefixlen = prefixlen

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   START - managed attributes.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def _get_prefixlen(self):
        return self._prefixlen

    def _set_prefixlen(self, val):
        try:
            #   Basic integer subnet prefix.
            prefixlen = int(val)
        except ValueError:
            #   Convert possible subnet mask to integer subnet prefix.
            ip = IP(val)
            if self._addr_type != ip.addr_type:
                raise ValueError('address and netmask type mismatch!')
            if not ip.is_netmask():
                raise ValueError('%s is not a valid netmask!' % ip)
            prefixlen = ip.netmask_bits()

        #   Validate subnet prefix.
        if not 0 <= prefixlen <= self._strategy.width:
            raise ValueError('%d is an invalid CIDR prefix for %s!' \
                % (prefixlen, AT_NAMES[self._addr_type]))

        self._prefixlen = prefixlen

    prefixlen = property(_get_prefixlen, _set_prefixlen, None,
        """The CIDR subnet prefix for this IP address.""")
    del _get_prefixlen, _set_prefixlen

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   END - managed attributes.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def is_netmask(self):
        """
        @return: C{True} if this addr is a mask that would return a host id,
        C{False} otherwise.
        """
        #   There is probably a better way to do this.
        #   Change at will, just don't break the unit tests :-)
        bits = self._strategy.int_to_bits(self._value).replace('.', '')

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
        @return: The number of bits set to one in this address if it is a
        valid netmask, otherwise the width (in bits) for the given address
        type is returned instead.
        """
        if not self.is_netmask():
            return self._strategy.width

        bits = self._strategy.int_to_bits(self._value)
        translate_str = ''.join([chr(_i) for _i in range(256)])
        mask_bits = bits.translate(translate_str, '.0')
        mask_length = len(mask_bits)

        if not 1 <= mask_length <= self._strategy.width:
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
        bits = self._strategy.int_to_bits(self._value).replace('.', '')

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
        return _socket.gethostbyaddr(str(self))[0]

    def cidr(self):
        """
        @return: A valid L{CIDR} object for this IP address.
        """
        hostmask = (1 << (self._strategy.width - self._prefixlen)) - 1
        start = (self._value | hostmask) - hostmask
        network = self._strategy.int_to_str(start)
        return CIDR("%s/%d" % (network, self._prefix))

    def ipv4(self):
        """
        @return: A new L{IP} object numerically equivalent this address.
            - If its address type is IPv4.
            - If object's address type is IPv6 and its value is mappable to
            IPv4, a new IPv4 L{IP} object is returned instead.
            - Raises an L{AddrConversionError} if IPv6 address is not mappable
            to IPv4.
        """
        raise NotImplementedError('TODO. Not yet implemented!')

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
        raise NotImplementedError('TODO. Not yet implemented!')

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
        if self._addr_type == AT_INET:
            if 0xe0000000 <= self._value <= 0xefffffff:
                return True
        elif  self._addr_type == AT_INET6:
            if 0xff000000000000000000000000000000 <= self._value <= \
               0xffffffffffffffffffffffffffffffff:
                return True
        return False

    def __str__(self):
        """
        @return: The common string representation for this IP address.
        """
        return self._strategy.int_to_str(self._value)

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        if self.prefixlen == self._strategy.width:
            return "netaddr.address.%s('%s')" % (self.__class__.__name__,
                str(self))

        return "netaddr.address.%s('%s/%d')" % (self.__class__.__name__,
            str(self), self.prefixlen)

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

    The only network address aggregate supporting all network address types.
    Most AddrRange subclasses only support a subset of address types.


    Sortability
    -----------
    A sequence of address ranges sort first by address type then by magnitude.
    So for a list containing ranges of all currently supported address types,
    IPv4 ranges come first, then IPv6, EUI-48 and lastly EUI-64.
    """
    def __init__(self, start_addr, stop_addr, klass=None):
        """
        Constructor.

        @param start_addr: start address for this network address range.

        @param stop_addr: stop address for this network address range.

        @param klass: (optional) class used to create each object returned.
            Default: L{Addr()} objects. See L{nrange()} documentations for
            additional details on options.
        """
        #   NB - These should only be are accessed via property() methods.
        self._first = 0
        self._last = 0
        self._strategy = None
        self._addr_type = None
        self._klass = None

        self.first = start_addr
        self.last = stop_addr
        self.klass = klass

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   START of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def _get_first(self):
        return self._first

    def _set_first(self, val):
        if not issubclass(val.__class__, Addr):
            if isinstance(val, (str, unicode)):
                addr = Addr(val)
                self._first = int(addr)
                self.strategy = addr.strategy
            else:
                raise TypeError('%r is not recognised string format ' \
                    'address or a (sub)class of Addr!' % val)
        else:
            self._first = int(val)
            self.strategy = val.strategy

    def _get_last(self):
        return self._last

    def _set_last(self, val):
        if not issubclass(val.__class__, Addr):
            if isinstance(val, (str, unicode)):
                self._last = int(Addr(val))
            else:
                raise TypeError('%r is not recognised string format ' \
                    'address or a (sub)class of Addr!' % val)
        else:
            self._last = int(val)

            if self.strategy is not None:
                if self._addr_type != val.addr_type:
                    raise TypeError('start and stop address types are different!')

        if self._last < self._first:
            raise IndexError('start address is greater than stop address!')

    def _get_strategy(self):
        return self._strategy

    def _set_strategy(self, val):
        if not issubclass(val.__class__, AddrStrategy):
            raise ValueError('%r is not AddrStrategy (sub)class!' % val)

        if val.max_int < self._last:
            raise ValueError('Present range boundary values exceed ' \
                'maximum values for address type %s!' \
                    % AT_NAMES[val.addr_type])

        self._strategy = val
        self._addr_type = self._strategy.addr_type

    def _get_addr_type(self):
        return self._strategy.addr_type

    def _get_klass(self):
        return self._klass

    def _set_klass(self, val):
        if isinstance(val, type):
            if val in (str, int, long, unicode):
                pass
            elif issubclass(val, Addr):
                pass
            else:
                raise TypeError("%r is an unsupported type!" % val)
        elif val is hex:
            #   hex() is a BIF, not a type, so do a separate check for it.
            pass
        elif val is None:
            #   Default class in None is specified.
            val = Addr
        else:
            raise ValueError("%r is not a supported type, BIF or class!" % val)

        self._klass = val

    #   Initialise accessors and tidy up the namespace at the same time.

    first = property(_get_first, _set_first, None, """
        The lower boundary network address of this range.""")
    del _get_first, _set_first

    last = property(_get_last, _set_last, None, """
        The upper boundary network address of this range.""")
    del _get_last, _set_last

    strategy = property(_get_strategy, _set_strategy, None, """
        An instance of AddrStrategy (sub)class.""")
    del _get_strategy, _set_strategy

    addr_type = property(_get_addr_type, None, None, """
        A read-only integer indentifying the address type of this range.""")
    del _get_addr_type

    klass = property(_get_klass, _set_klass, None, """
        A type, BIF or class used to create each object returned by an
        instance of this class including first and last properties when they
        are accessed.""")
    del _get_klass, _set_klass

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   END of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

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
        return self._last - self._first + 1

    def data_flavour(self, int_addr):
        """
        @param int_addr: an network address as a network byte order integer.

        @return: a network address in whatever 'flavour' is required based on
        the value of the klass property.
        """
        if self.klass in (str, unicode):
            return self._strategy.int_to_str(int_addr)
        elif self.klass in (int, long, hex):
            return self.klass(int_addr)
        else:
            return self.klass(int_addr, self._addr_type)

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
                return self.data_flavour(self._last + index + 1)
            elif 0 <= index <= (self.size() - 1):
                #   Positive index or zero index.
                return self.data_flavour(self._first + index)
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

            start_addr = Addr(self._first + start, self._addr_type)
            end_addr = Addr(self._first + stop - step, self._addr_type)
            return nrange(start_addr, end_addr, step, klass=self.klass)
        else:
            raise TypeError('unsupported type %r!' % index)

    def __iter__(self):
        """
        @return: An iterator object providing access to all network addresses
            within this range.
        """
        start_addr = Addr(self._first, self._addr_type)
        end_addr = Addr(self._last, self._addr_type)
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
            if c_addr.addr_type == self._addr_type:
                if self._first <= int(c_addr) <= self._last:
                    return True
        elif issubclass(addr.__class__, Addr):
            #   Single value check.
            if self._first <= int(addr) <= self._last:
                return True
        elif issubclass(addr.__class__, AddrRange):
            #   Range value check.
            if (addr.first >= self._first) and (addr.last <= self._last):
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
        if (self._addr_type, self._first, self._last) == \
           (other._addr_type, other._first, other._last):
            return True

        return False

    def __ne__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are not the same as
            other, C{False} otherwise.
        """
        if (self._addr_type, self._first, self._last) != \
           (other._addr_type, other._first, other._last):
            return True

        return False

    def __lt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are less than other,
            C{False} otherwise.
        """
        if (self._addr_type, self._first, self._last) < \
           (other._addr_type, other._first, other._last):
            return True

        return False

    def __le__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are less or equal to
            other, C{False} otherwise.
        """
        if (self._addr_type, self._first, self._last) <= \
           (other._addr_type, other._first, other._last):
            return True

        return False

    def __gt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are greater than
            other, C{False} otherwise.
        """
        if (self._addr_type, self._first, self._last) > \
           (other._addr_type, other._first, other._last):
            return True

        return False

    def __ge__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundaries of this range are greater or equal
            to other, C{False} otherwise.
        """
        if (self._addr_type, self._first, self._last) >= \
           (other._addr_type, other._first, other._last):
            return True

        return False

    def __str__(self):
        return "%s;%s" % (self._strategy.int_to_str(self._first),
                          self._strategy.int_to_str(self._last))

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s(%r, %r)" % (self.__class__.__name__,
            self._strategy.int_to_str(self._first),
            self._strategy.int_to_str(self._last))

#-----------------------------------------------------------------------------
def abbrev_to_cidr(addr):
    """
    @param addr: an abbreviated CIDR network address.

    Uses the old-style classful IP address rules to decide on a default subnet
    prefix if one is not explicitly provided.

    Only supports IPv4 and IPv4 mapped IPv6 addresses.

    Examples ::

        10                  - 10.0.0.0/8
        10/16               - 10.0.0.0/16
        128                 - 128.0.0.0/16
        128/8               - 128.0.0.0/8
        192.168             - 192.168.0.0/16
        ::192.168           - ::192.168.0.0/128
        ::ffff:192.168/120  - ::ffff:192.168.0.0/120

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
        elif 224 <= octet <= 239:
            #   Class D (multicast)
            prefix = 4
        return prefix

    start = ''
    tokens = []
    prefix = None

#FIXME:    #   Check for IPv4 mapped IPv6 addresses.
    if isinstance(addr, (str, unicode)):
    ################
        #   Don't support IPv6 for now...
        if ':' in addr:
            return None
    ################
#FIXME:        if addr.startswith('::ffff:'):
#FIXME:            addr = addr.replace('::ffff:', '')
#FIXME:            start = '::ffff:'
#FIXME:            if '/' not in addr:
#FIXME:                prefix = 128
#FIXME:        elif addr.startswith('::'):
#FIXME:            addr = addr.replace('::', '')
#FIXME:            start = '::'
#FIXME:            if '/' not in addr:
#FIXME:                prefix = 128
    ################

    try:
        #   Single octet partial integer or string address.
        i = int(addr)
        tokens = [str(i), '0', '0', '0']
        return "%s%s/%s" % (start, '.'.join(tokens), classful_prefix(i))

    except ValueError:
        #   Multi octet partial string address with optional prefix.
        part_addr = addr
        tokens = []

        if part_addr == '':
            #   Not a recognisable format.
            return None

        if '/' in part_addr:
            (part_addr, prefix) = part_addr.split('/', 1)

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
            prefix = classful_prefix(tokens[0])

        return "%s%s/%s" % (start, '.'.join(tokens), prefix)

    except TypeError:
        pass
    except IndexError:
        pass

    #   Not a recognisable format.
    return None

#-----------------------------------------------------------------------------
class CIDR(AddrRange):
    """
    A block of contiguous IPv4 or IPv6 network addresses defined by a base
    network address and a bitmask prefix or subnet mask address indicating the
    size/extent of the subnet.

    This class B{does not accept any non zero bits to be set right of the
    bitmask} (unlike the L{IP} class which is less strict). Doing so raises an
    L{AddrFormatError} exception.

    Examples of supported formats :-

        1. CIDR address format - C{<address>/<mask_length>}::

            192.168.0.0/16

        2. Address and subnet mask combo ::

            192.168.0.0/255.255.0.0 == 192.168.0.0/16

        3. Partial or abbreviated formats. Prefixes may be omitted and in this
        case old classful default prefixes apply ::

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
    def __init__(self, cidr, klass=IP):
        """
        Constructor.

        @param cidr: a valid IPv4/IPv6 CIDR address or abbreviated
            IPv4 network address

        @param klass: (optional) type, BIF or class used to create each
            object returned. Default: L{IP} class. See L{nrange()}
            documentations for additional details on options.
        """
        #   NB - This should only be are accessed via property() methods.
        self._prefixlen = None
        self._netmask = None
        self._hostmask = None

        #   Keep a copy of original argument for later reference.
        cidr_arg = cidr

        #   Replace an abbreviation with a verbose CIDR.
        verbose_cidr = abbrev_to_cidr(cidr)
        if verbose_cidr is not None:
            cidr = verbose_cidr

        #   Check for prefix in address and split it out.
        try:
            (network, mask) = cidr.split('/', 1)
        except ValueError:
            raise AddrFormatError('%r is not a recognised CIDR!' % cidr_arg)

        #   Check first addr.
        first_addr = IP(network)
        self._strategy = first_addr.strategy

        #   Check and normalise the CIDR prefix.
        self.prefixlen = mask

        hostmask_int = (1 << (first_addr.strategy.width - self.prefixlen)) - 1
        netmask_int = first_addr.strategy.max_int ^ hostmask_int

        last_int = first_addr.value | hostmask_int
        first_int = last_int - hostmask_int

        self._netmask = netmask_int
        self._hostmask = hostmask_int

        last_addr = IP(last_int, self.addr_type)

        #   Make cidr() stricter than inet() ...
        host = (int(first_addr) | netmask_int) - netmask_int
        if host != 0:
            raise ValueError('non-zero bits to the right of netmask! Base ' \
                'address %s matches CIDR prefix /%s.' \
                    % (self._strategy.int_to_str(first_int), self.prefixlen))

        super(CIDR, self).__init__(first_addr, last_addr, klass=klass)

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   START of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def _get_prefixlen(self):
        return self._prefixlen

    def _set_prefixlen(self, val):
        try:
            #   Basic integer subnet prefix.
            prefixlen = int(val)
        except ValueError:
            #   Convert possible subnet mask to integer subnet prefix.
            ip = IP(val)

            if self.addr_type != ip.addr_type:
                raise ValueError('address and netmask type mismatch!')

            if not ip.is_netmask():
                raise ValueError('%s is not a valid netmask!' % ip)

            prefixlen = ip.netmask_bits()

        #   Validate subnet prefix.
        if not 0 <= prefixlen <= self._strategy.width:
            raise ValueError('%d is an invalid CIDR prefix for %s!' \
                % (prefixlen, AT_NAMES[self.addr_type]))

        self._prefixlen = prefixlen

    prefixlen = property(_get_prefixlen, _set_prefixlen, None,
        """The size of mask (in bits) for this CIDR range.""")
    del _get_prefixlen, _set_prefixlen

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   END of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def netmask(self):
        """
        @return: The subnet mask address of this CIDR range.
        """
        return self.data_flavour(self._netmask)

    def hostmask(self):
        """
        @return: The host mask address of this CIDR range.
        """
        return self.data_flavour(self._hostmask)

    def __str__(self):
        return "%s/%s" % (self._strategy.int_to_str(self._first), self.prefixlen)

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s('%s/%d')" % (self.__class__.__name__,
            str(self._first), self.prefixlen)

    def wildcard(self):
        """
        @return: A L{Wildcard} object equivalent to this CIDR.
            - If CIDR was initialised with C{klass=str} a wildcard string is
            returned, in all other cases a L{Wildcard} object is returned.
            - Only supports IPv4 CIDR addresses.
        """
        t1 = self._strategy.int_to_words(self._first)
        t2 = self._strategy.int_to_words(self._last)

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

#-----------------------------------------------------------------------------
class Wildcard(AddrRange):
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

        I{All CIDR ranges can be represented as wildcard ranges but the reverse
        isn't always true.}
    """
    def __init__(self, wildcard, klass=IP):
        """
        Constructor.

        @param wildcard: a valid IPv4 wildcard address

        @param klass: (optional) class used to create each return object.
            Default: L{IP} objects. See L{nrange()} documentations for
            additional details on options.
        """
        #---------------------------------------------------------------------
        #TODO: Add support for partial wildcards
        #TODO: e.g. 192.168.*.* == 192.168.*
        #TODO:      *.*.*.*     == *
        def _is_wildcard(wildcard):
            """
            True if wildcard address is valid, False otherwise.
            """
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
        #---------------------------------------------------------------------

        if not _is_wildcard(wildcard):
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

        first = IP('.'.join(t1))
        last = IP('.'.join(t2))

        if first.addr_type != AT_INET:
            raise AddrFormatError('Wildcard syntax only supports IPv4!')

        super(self.__class__, self).__init__(first, last, klass=klass)

    def cidr(self):
        """
        @return: A valid L{CIDR} object for this wildcard. If conversion fails
            an L{AddrConversionError} is raised as not all wildcards ranges are
            valid CIDR ranges.
        """
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
        network = self._strategy.int_to_str(self._first)
        try:
            cidr = CIDR("%s/%d" % (network, prefix))
        except:
            raise AddrConversionError('%s cannot be represented with CIDR' \
                % str(self))

        if self.klass == str:
            return str(cidr)

        return cidr

    def __str__(self):
        t1 = self._strategy.int_to_words(self._first)
        t2 = self._strategy.int_to_words(self._last)

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
#   Unit Tests.
#-----------------------------------------------------------------------------

class Test_Addr(unittest.TestCase):

    def test_exceptions(self):
        """
        Check that exception are being raised for unexpected intput.
        """
        invalid_addrs = ([], {}, '', None, 5.2, -1,
            'abc.def.ghi.jkl',
            '::z'
        )

        for addr in invalid_addrs:
            self.failUnlessRaises(AddrFormatError, Addr, addr)

    def test_assignments(self):
        """
        Checks a list of addresses expected to be valid.
        """
        addr = Addr('0.0.0.0')
        self.failUnless(addr.value == 0)
        self.failUnless(addr.addr_type == AT_INET)
        self.failUnless(addr.strategy == ST_IPV4)

        #   Test addr_type assignment.
        addr.addr_type = AT_INET6
        self.failUnless(addr.addr_type == AT_INET6)
        self.failUnless(addr.strategy == ST_IPV6)

        #   Test strategy assignment.
        addr.strategy = ST_EUI48
        self.failUnless(addr.addr_type == AT_LINK)
        self.failUnless(addr.strategy == ST_EUI48)

        addr.strategy = ST_EUI64
        self.failUnless(addr.addr_type == AT_EUI64)
        self.failUnless(addr.strategy == ST_EUI64)

        #   Test value assignment.
        addr.addr_type = AT_INET
        addr.value = '192.168.0.1'
        self.failUnless(addr.value == 3232235521)
        self.failUnless(addr.addr_type == AT_INET)
        self.failUnless(addr.strategy == ST_IPV4)

    def test_sortability(self):
        addresses = (Addr('192.168.0.255'), Addr('192.168.0.1'), Addr('::'))
        for addr in sorted(addresses):
            print addr

#-----------------------------------------------------------------------------
class Test_IP(unittest.TestCase):

    def test_assignments_IPv4(self):
        """
        Checks assignments to managed attributes.
        """
        ip = IP('192.168.0.1')
        self.failUnless(ip.value == 3232235521)
        self.failUnless(ip.addr_type == AT_INET)
        self.failUnless(ip.strategy == ST_IPV4)
        self.failUnless(ip.prefixlen == 32)

        #   Prefix /32 for IPv4 addresses should be implicit.
        self.failUnless(repr(ip) == "netaddr.address.IP('192.168.0.1')")
        ip.prefixlen = 24
        self.failUnless(repr(ip) == "netaddr.address.IP('192.168.0.1/24')")

    def test_assignments_IPv6(self):
        """
        Checks assignments to managed attributes.
        """
        ip = IP('fe80::4472:4b4a:616d')
        self.failUnless(ip.value == 338288524927261089654018972099027820909)
        self.failUnless(ip.addr_type == AT_INET6)
        self.failUnless(ip.strategy == ST_IPV6)
        self.failUnless(ip.prefixlen == 128)

        #   Prefix /128 for IPv6 addresses should be implicit.
        self.failUnless(repr(ip) == "netaddr.address.IP('fe80::4472:4b4a:616d')")
        ip.prefixlen = 64
        self.failUnless(repr(ip) == "netaddr.address.IP('fe80::4472:4b4a:616d/64')")

#-----------------------------------------------------------------------------
class Test_AddrRange(unittest.TestCase):

    def test_basic(self):
        """
        Address ranges now sort as expected based on magnitude.
        """
        print 'foo'
        ranges = (
            AddrRange(Addr('0-0-0-0-0-0-0-0'), Addr('0-0-0-0-0-0-0-0')),
            AddrRange(Addr('::'), Addr('::')),
            AddrRange(Addr('0-0-0-0-0-0'), Addr('0-0-0-0-0-0')),
            AddrRange(Addr('0.0.0.0'), Addr('255.255.255.255')),
            AddrRange(Addr('0.0.0.0'), Addr('0.0.0.0')),
        )
        print '-' * 80
        for r in sorted(ranges):
            print r
        print '-' * 80

#        r1 = AddrRange('255.255.255.250', '255.255.255.255')
#        print r1.klass, list(r1)
#        r1.klass = str
#        print r1.klass, list(r1)
#        r1.klass = int
#        print r1.klass, list(r1)
#        r1.klass = hex
#        print r1.klass, list(r1)

    def test_sortability(self):
        ranges = (
            AddrRange('0.0.0.0', '255.255.255.255'),
            AddrRange('192.168.0.0', '192.168.0.7'),
            AddrRange('192.168.0.0', '192.168.0.16'),
            AddrRange('192.168.0.0', '192.168.0.127'),
            AddrRange('192.168.0.0', '192.168.0.255')
        )

        print "%-25s %-15s %-15s" % ('range', 'start', 'end')
        print "%s %s %s" % ('-'*25, '-'*15, '-'*15)
        for r in sorted(ranges):
            print "%-25s %-15s %-15s" % (r, r[0], r[-1])


#-----------------------------------------------------------------------------
def show_namespace_layout():
    """
    This is just a quick subclass to show what the current namespace looks
    like from an end user perspective. Keep it clean!
    """
    class MyAddr(Addr):

        def __init__(self, *args, **kwargs):
            super(MyAddr, self).__init__(*args, **kwargs)
            print "--- ADDR ---"
            for i in dir(self):
                print "%-25s %s" % (i, type(eval("self.%s" % i)))

    MyAddr('0.0.0.0')


#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #show_namespace_layout()

    ip = IP('192.168.0.1')
    print ip

    c = CIDR('ff00::/8')
    print 'multicast CIDR:', c
    print 'min:', c[0], hex(c[0])
    print 'max:', c[-1], hex(c[-1])
    print c.prefixlen
    print c.size()
    #wc = c.wildcard()
    #print wc
    #print wc.cidr()

    #print '231.1.25.10' in wc
    #print IP('231.1.25.10') in c

    print '------------'
    for addr in sorted((
        IP('ffff::ffff'),
        IP('::'),
        IP('255.255.255.255'),
        IP('0.0.0.0'),
    )):
        print addr
    print '------------'

    unittest.main()

