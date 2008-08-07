#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network addresses and associated aggregates (CIDR, Wilcard, etc).
"""
import math as _math
from netaddr import AddrFormatError, AddrConversionError
from netaddr.strategy import AT_UNSPEC, AT_LINK, AT_INET, AT_INET6, \
                             AT_EUI64, ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64

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
    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: the string form of a network address, or a network byte
            order integer within the supported range for the address type.

        @param addr_type: (optional) the network address type. If addr is an
            integer, this argument becomes mandatory.
        """
        if not isinstance(addr, (str, unicode, int, long)):
            raise TypeError("addr must be an network address string or a " \
                "positive integer!")

        if isinstance(addr, (int, long)) and addr_type is None:
            raise ValueError("addr_type must be provided with int/long " \
                "address values!")

        self.value = None
        self.strategy = None

        if addr_type is AT_UNSPEC:
            #   Auto-detect address type.
            for strategy in (ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64):
                if strategy.valid_str(addr):
                    self.strategy = strategy
                    break
        elif addr_type == AT_INET:
            self.strategy = ST_IPV4
        elif addr_type == AT_INET6:
            self.strategy = ST_IPV6
        elif addr_type == AT_LINK:
            self.strategy = ST_EUI48
        elif addr_type == AT_EUI64:
            self.strategy = ST_EUI64

        if self.strategy is None:
            #   Whoops - we fell through and didn't match anything!
            raise AddrFormatError("%r is not a recognised address format!" \
                % addr)

        if addr is None:
            addr = 0

        self.addr_type = self.strategy.addr_type
        self.setvalue(addr)

    #TODO: replace this method with __setattr__() instead.
    def setvalue(self, addr):
        """
        Sets the value of this address.

        @param addr: the string form of a network address, or a network byte
        order integer value within the supported range for the address type.
            - Raises a C{TypeError} if addr is of an unsupported type.
            - Raises an C{OverflowError} if addr is an integer outside the
            bounds for this address type.
        """
        if isinstance(addr, (str, unicode)):
            self.value = self.strategy.str_to_int(addr)
        elif isinstance(addr, (int, long)):
            if self.strategy.valid_int(addr):
                self.value = addr
            else:
                raise OverflowError('%r cannot be represented in %r bits!' \
                    % (addr, self.strategy.width))
        else:
            raise TypeError('%r is an unsupported type!')

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
        self.setvalue(self.strategy.words_to_int(words))

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
        if int(self) == int(other):
            return True
        return False

    def __lt__(self, other):
        """
        @return: C{True} if this network address instance has a lower
            numerical value than another, C{False} otherwise.
        """
        if int(self) < int(other):
            return True
        return False

    def __le__(self, other):
        """
        @return: C{True} if this network address instance has a lower or
            equivalent numerical value than another, C{False} otherwise.
        """
        if int(self) <= int(other):
            return True
        return False

    def __gt__(self, other):
        """
        @return: C{True} if this network address instance has a higher
            numerical value than another, C{False} otherwise.
        """
        if int(self) > int(other):
            return True
        return False

    def __ge__(self, other):
        """
        @return: C{True} if this network address instance has a higher or
            equivalent numerical value than another, C{False} otherwise.
        """
        if int(self) >= int(other):
            return True
        return False

    def family(self):
        """
        @return: The integer constant identifying this object's address type.
        """
        return self.strategy.addr_type

#-----------------------------------------------------------------------------
class EUI(Addr):
    """
    EUI objects represent IEEE Extended Unique Identifiers. Input parsing is
    flexible, supporting EUI-48, EUI-64 and all MAC (Media Access Control)
    address flavours.
    """
    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: an EUI/MAC address string or a network byte order
            integer.

        @param addr_type: (optional) the specific EUI address type (C{AT_LINK}
        or C{AT_EUI64}). If addr is an integer, this argument is mandatory.
        """
        if not isinstance(addr, (str, unicode, int, long)):
            raise TypeError("addr must be an EUI/MAC network address " \
                "string or a positive integer!")

        if isinstance(addr, (int, long)) and addr_type is None:
            raise ValueError("addr_type must be provided with integer " \
                "address values!")

        self.value = None
        self.strategy = None

        if addr_type is AT_UNSPEC:
            #   Auto-detect address type.
            for strategy in (ST_EUI48, ST_EUI64):
                if strategy.valid_str(addr):
                    self.strategy = strategy
                    break
        elif addr_type == AT_LINK:
            self.strategy = ST_EUI48
        elif addr_type == AT_EUI64:
            self.strategy = ST_EUI64

        if self.strategy is None:
            #   Whoops - we fell through and didn't match anything!
            raise AddrFormatError("%r is not a recognised EUI or MAC " \
                "address format!" % addr)

        if addr is None:
            addr = 0

        self.addr_type = self.strategy.addr_type
        self.setvalue(addr)

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
    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        @param addr: an IPv4 or IPv6 address string with an optional subnet
        prefix or a network byte order integer.

        @param addr_type: (optional) the IP address type (C{AT_INET} or
        C{AT_INET6}). If L{addr} is an integer, this argument is mandatory.
        """
        if not isinstance(addr, (str, unicode, int, long)):
            raise TypeError("addr must be an network address string or a " \
                "positive integer!")

        if isinstance(addr, (int, long)) and addr_type is AT_UNSPEC:
            raise ValueError("addr_type must be provided with int/long " \
                "address values!")

        self.value = None
        self.strategy = None
        self.prefix = None

        if addr_type == AT_UNSPEC:
            pass
        elif addr_type == AT_INET:
            self.strategy = ST_IPV4
        elif addr_type == AT_INET6:
            self.strategy = ST_IPV6
        else:
            raise ValueError('%r is an unsupported address type!')

        if addr is None:
            addr = 0

        self.setvalue(addr)

    #TODO: replace this method with __setattr__() instead.
    def setvalue(self, addr):
        """
        Sets the value of this address.

        @param addr: the string form of an IP address, or a network byte order
            int/long value within the supported range for the address type.
                - Raises a C{TypeError} if addr is of an unsupported type.
                - Raises an C{OverflowError} if addr is an integer outside the
                bounds for this address type.
        """
        if isinstance(addr, (str, unicode)):
            #   String address.
            if '/' in addr:
                (addr, masklen) = addr.split('/', 1)
                self.prefix = int(masklen)

            #   Auto-detect address type.
            for strategy in (ST_IPV4, ST_IPV6):
                if strategy.valid_str(addr):
                    self.strategy = strategy
                    break

            if self.strategy is None:
                raise AddrFormatError('%r is not a valid IPv4/IPv6 address!' \
                    % addr)

            self.addr_type = self.strategy.addr_type
            self.value = self.strategy.str_to_int(addr)

        elif isinstance(addr, (int, long)):
            if self.strategy.valid_int(addr):
                self.addr_type = self.strategy.addr_type
                self.value = addr
            else:
                raise OverflowError('%r cannot be represented in %r bits!' \
                    % (addr, self.strategy.width))
        else:
            raise TypeError('%r is an unsupported type!')

        #   Set default prefix.
        if self.prefix == None:
            self.prefix = self.strategy.width

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

    def prefixlen(self):
        """
        @return: The number of bits set to one in this address if it is a
        netmask, zero otherwise.
        """
        if not self.is_netmask():
            return self.strategy.width

        bits = self.strategy.int_to_bits(self.value)
        translate_str = ''.join([chr(_i) for _i in range(256)])
        mask_bits = bits.translate(translate_str, '.0')
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

    def cidr(self):
        """
        @return: A valid L{CIDR} object for this IP address.
        """
        hostmask = (1 << (self.strategy.width - self.prefix)) - 1
        start = (self.value | hostmask) - hostmask
        network = self.strategy.int_to_str(start)
        return CIDR("%s/%s" % (network, self.prefix))

    def masklen(self):
        """
        @return: The subnet prefix of this IP address.
        """
        return int(self.prefix)

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
        return "netaddr.address.%s('%s/%d')" % (self.__class__.__name__,
            str(self), self.prefix)

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

    if step < 0:
        negative_step = True

    index = int(start) - step

    #   Set default klass value.
    if klass is None:
        klass = Addr

    if klass in (int, long, hex):
        #   Yield network address integer values.
        while True:
            index += step
            if negative_step:
                if not index >= int(stop):
                    return
            else:
                if not index <= int(stop):
                    return
            yield klass(index)

    elif klass in (str, unicode):
        #   Yield address string values.
        while True:
            index += step
            if negative_step:
                if not index >= int(stop):
                    return
            else:
                if not index <= int(stop):
                    return

            yield str(start.__class__(index, addr_type))
    else:
        #   Yield network address objects.
        while True:
            index += step
            if negative_step:
                if not index >= int(stop):
                    return
            else:
                if not index <= int(stop):
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
        #   Set start address.
        if not issubclass(start_addr.__class__, Addr):
            if isinstance(start_addr, (str, unicode)):
                self.start_addr = Addr(start_addr)
            else:
                raise TypeError('start_addr is not recognised address in ' \
                    'string format or an that is a (sub)class of Addr!')
        else:
            self.start_addr = start_addr

            #   Make klass the same as start_addr object.
            if klass is None:
                klass = start_addr.__class__

        #   Assign default klass.
        if klass is None:
            self.klass = Addr
        else:
            self.klass = klass

        #   Set stop address.
        if not issubclass(stop_addr.__class__, Addr):
            if isinstance(stop_addr, (str, unicode)):
                self.stop_addr = Addr(stop_addr)
            else:
                raise TypeError('stop_addr is not recognised address in ' \
                    'string format or an that is a (sub)class of Addr!')
        else:
            self.stop_addr = stop_addr

        if self.start_addr.addr_type != self.stop_addr.addr_type:
            raise TypeError('start_addr and stop_addr are not the same ' \
                'address type!')

        self.addr_type = self.start_addr.addr_type

        if self.stop_addr < self.start_addr:
            raise IndexError('stop_addr must be greater than start_addr!')

    def __setattr__(self, name, value):
        """
        Police assignments to various class attributes to ensure nothing gets
        broken accidentally.
        """
        if name == 'klass':
            if isinstance(value, type):
                if value in (str, int, long, unicode):
                    pass
                elif issubclass(value, Addr):
                    pass
                else:
                    raise TypeError("unsupported type %r for klass!" % value)
            elif value is hex:
                #   hex() is a BIF, not a type.
                pass
            else:
                raise ValueError("unsupported value %r for klass!" % value)

        self.__dict__[name] = value

    def _retval(self, addr):
        """
        Protected method. B{*** Not intended for public use ***}
        """
        #   Decides on the flavour of a value to be return based on klass
        #   property.
        if self.klass in (str, unicode):
            return str(addr)
        elif self.klass in (int, long, hex):
            return self.klass(int(addr))
        else:
            return self.klass(int(addr), self.addr_type)

    def first(self):
        """
        @return: The lower boundary network address of this range.
        """
        return self._retval(self.start_addr)

    def last(self):
        """
        @return: The upper boundary network address of this range.
        """
        return self._retval(self.stop_addr)

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
        return int(self.stop_addr) - int(self.start_addr) + 1

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
                addr_type = self.stop_addr.addr_type
                index_addr = Addr(int(self.stop_addr), addr_type)
                index_addr += (index + 1)
                return self._retval(index_addr)
            elif 0 <= index <= (self.size() - 1):
                #   Positive index or zero index.
                addr_type = self.start_addr.addr_type
                index_addr = Addr(int(self.start_addr), addr_type)
                index_addr += index
                return self._retval(index_addr)
            else:
                raise IndexError('index out range for address range size!')
        elif isinstance(index, slice):
            #   slices
            addr_type = self.start_addr.addr_type
            int_start_addr = int(self.start_addr)
            #FIXME: IPv6 breaks the .indices() method on the slice object
            #   spectacularly. We'll have to work out the start, stop and
            #   step ourselves :-(
            #
            #   see PySlice_GetIndicesEx function in Python SVN repository for
            #   implementation details :-
            #   http://svn.python.org/view/python/trunk/Objects/sliceobject.c
            (start, stop, step) = index.indices(self.size())

            return nrange(Addr(int_start_addr + start, addr_type),
                          Addr(int_start_addr + stop - step, addr_type),
                          step, klass=self.klass)
        else:
            raise TypeError('unsupported type %r!' % index)

    def __iter__(self):
        """
        @return: An iterator object providing access to all network addresses
            within this range.
        """
        return nrange(self.start_addr, self.stop_addr, klass=self.klass)

    def __contains__(self, addr):
        """
        @param addr: object of Addr/AddrRange (sub)class or a network address
            string to be compared.

        @return: C{True} if given address or range falls within this range,
            C{False} otherwise.
        """
        if isinstance(addr, (str, unicode)):
            #   string address or address range.
            if self.start_addr <= Addr(addr) <= self.stop_addr:
                return True
        elif issubclass(addr.__class__, Addr):
            #   Single value check.
            if self.start_addr <= addr <= self.stop_addr:
                return True
        elif issubclass(addr.__class__, AddrRange):
            #   Range value check.
            if (addr.start_addr >= self.start_addr) \
                and (addr.stop_addr <= self.stop_addr):
                return True
        else:
            raise TypeError('%r is an unsupported class or type!' % addr)

        return False

    def __eq__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundary of this range is the same as other,
            C{False} otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) == int(other.start_addr):
            if int(self.stop_addr) == int(other.stop_addr):
                return True

        return False

    def __ne__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundary of this range is not the same as
            other, C{False} otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) != int(other.start_addr):
            return True

        return False

    def __lt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the lower boundary of this range is less than
            other, C{False} otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) < int(other.start_addr):
            return True

        return False

    def __le__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the lower boundary of this range is less or equal
            to other, C{False} otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) <= int(other.start_addr):
            return True

        return False

    def __gt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the lower boundary of this range is greater than
            other, C{False} otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) > int(other.start_addr):
            return True

        return False

    def __ge__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the lower boundary of this range is greater or
            equal to other, C{False} otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) >= int(other.start_addr):
            return True

        return False

    def __str__(self):
        return "%s-%s" % (self.start_addr, self.stop_addr)

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s(%r, %r)" % (self.__class__.__name__,
            str(self.start_addr), str(self.stop_addr))

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
            prefix = 8
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
    def __init__(self, addr_mask, klass=IP):
        """
        Constructor.

        @param addr_mask: a valid IPv4/IPv6 CIDR address or abbreviated
            IPv4 network address

        @param klass: (optional) type, BIF or class used to create each
            object returned. Default: L{IP} class. See L{nrange()}
            documentations for additional details on options.
        """
        verbose_addr_mask = abbrev_to_cidr(addr_mask)
        if verbose_addr_mask is not None:
            addr_mask = verbose_addr_mask

        tokens = addr_mask.split('/')

        if len(tokens) != 2:
            raise AddrFormatError('%r is not a recognised CIDR ' \
                'format!' % addr_mask)

        addr = IP(tokens[0])

        try:
            #   Try int value.
            prefixlen = int(tokens[1])
        except ValueError:
            #   Try subnet mask.
            mask = IP(tokens[1])
            if not mask.is_netmask():
                raise AddrFormatError('%r does not contain a valid ' \
                    'subnet mask!'  % addr_mask)
            prefixlen = mask.prefixlen()
            if mask.addr_type != addr.addr_type:
                raise AddrFormatError('Address and netmask types do ' \
                    'not match!')

        if not 0 <= prefixlen <= addr.strategy.width:
            raise IndexError('CIDR prefix out of bounds for %s addresses!' \
                % addr.strategy.name)

        self.mask_len = prefixlen
        width = addr.strategy.width
        self.addr_type = addr.strategy.addr_type

        int_hostmask = (1 << (width - self.mask_len)) - 1
        int_stop = int(addr) | int_hostmask
        int_start = int_stop - int_hostmask
        int_netmask = addr.strategy.max_int ^ int_hostmask

        start_addr = IP(int_start, self.addr_type)
        stop_addr = IP(int_stop, self.addr_type)

        super(self.__class__, self).__init__(start_addr, stop_addr,
              klass=klass)

        self.netmask_addr = IP(int_netmask, self.addr_type)
        self.hostmask_addr = IP(int_hostmask, self.addr_type)

        #   Make cidr() stricter than inet() ...
        host = (int(addr) | int_netmask) - int_netmask
        if host != 0:
            raise ValueError('non-zero bits to the right of netmask! ' \
                'Try %s instead.' % str(self))

    def netmask(self):
        """
        @return: The subnet mask address of this CIDR range.
        """
        return self._retval(self.netmask_addr)

    def hostmask(self):
        """
        @return: The host mask address of this CIDR range.
        """
        return self._retval(self.hostmask_addr)

    def prefixlen(self):
        """
        @return: Size of mask (in bits) of this CIDR range.
        """
        return self.mask_len

    def __str__(self):
        return "%s/%s" % (self.start_addr, self.mask_len)

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s('%s/%d')" % (self.__class__.__name__,
            str(self.start_addr), self.mask_len)

    def wildcard(self):
        """
        @return: A L{Wildcard} object equivalent to this CIDR.
            - If CIDR was initialised with C{klass=str} a wildcard string is
            returned, in all other cases a L{Wildcard} object is returned.
            - Only supports IPv4 CIDR addresses.
        """
        t1 = tuple(self.start_addr)
        t2 = tuple(self.stop_addr)

        if self.addr_type != AT_INET:
            raise AddrConversionError('IPv6 CIDR addresses are invalid!')

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

        start_addr = IP('.'.join(t1))
        stop_addr = IP('.'.join(t2))

        if start_addr.addr_type != AT_INET:
            raise AddrFormatError('%s is an invalid IPv4 wildcard!' \
                % start_addr)

        super(self.__class__, self).__init__(start_addr, stop_addr,
              klass=klass)

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
        #   fail. Fine for our purposes here as we only envisage going up to
        #   2^32, for now at least.
        if mantissa != 0.5:
            raise AddrConversionError('%s cannot be represented with CIDR' \
                % str(self))

        prefix = 32 - int(exponent - 1)
        network = str(self.start_addr)
        try:
            cidr = CIDR("%s/%d" % (network, prefix))
        except:
            raise AddrConversionError('%s cannot be represented with CIDR' \
                % str(self))

        if self.klass == str:
            return str(cidr)

        return cidr

    def __str__(self):
        t1 = tuple(self.start_addr)
        t2 = tuple(self.stop_addr)

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
                        #FIXME: police properties with __setattr__ instead...
                        raise AddrFormatError('only one hyphenated octet ' \
                            ' per wildcard allowed!')
                else:
                    #FIXME: police properties with __setattr__ instead...
                    raise AddrFormatError('asterisks not permitted before ' \
                        'hyphenated octets!')

        return '.'.join(tokens)

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s(%r)" % (self.__class__.__name__, str(self))

if __name__ == '__main__':
    pass
