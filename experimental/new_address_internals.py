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
"""
from netaddr import AddrFormatError, AT_UNSPEC, AT_INET, AT_INET6, AT_LINK, \
    AT_EUI64

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
    Base class representing individual addresses.
    """
    #   Class properties.
    STRATEGIES = (ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_INET, AT_INET6, AT_LINK, AT_EUI64)

    def __init__(self, addr, addr_type=AT_UNSPEC):
        #   NB - These should only be are accessed via property() methods.
        self.__strategy = None
        self.__value = None
        self.__addr_type = None

        self.addr_type = addr_type
        self.value = addr

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   START of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def _get_addr_type(self):
        return self.__addr_type

    def _set_addr_type(self, val):
        if val == AT_UNSPEC:
            pass
        else:
            #   Validate addr_type and keep in sync with strategy.
            if val not in self.__class__.ADDR_TYPES:
                raise ValueError('addr_type %r is invalid for objects of ' \
                    'the %s() class!' % (val, self.__class__.__name__))
            self.__strategy = AT_STRATEGIES[val]

        self.__addr_type = val

    def _get_value(self):
        return self.__value

    def _set_value(self, val):
        #   Select a strategy object for this address.
        if self.addr_type == AT_UNSPEC:
            for strategy in self.__class__.STRATEGIES:
                if strategy.valid_str(val):
                    self.strategy = strategy
                    break

        #   Make sure we picked up a strategy object.
        if self.__strategy is None:
            raise AddrFormatError('%r is not a recognised address ' \
                'format!' % val)

        #   Calculate and validate the value for this address.
        if isinstance(val, (str, unicode)):
            val = self.strategy.str_to_int(val)
        elif isinstance(val, (int, long)):
            if not self.strategy.valid_int(val):
                raise OverflowError('value %r cannot be represented ' \
                    'in %d bit(s)!' % (val, self.strategy.width))
        self.__value = val

    def _get_strategy(self):
        return self.__strategy

    def _set_strategy(self, val):
        #   Validate strategy and keep in sync with addr_type.
        if not issubclass(val.__class__, AddrStrategy):
            raise TypeError('%r is not an object of (sub)class of ' \
                'AddrStrategy!' % val)
        self.__addr_type = val.addr_type

        self.__strategy = val

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
    #   END of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

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

    def bits(self):
        """
        @return: A human-readable binary digit string for this address type.
        """
        return self.strategy.int_to_bits(self.value)

    def __hex__(self):
        """
        @return: The value of this address as a network byte order hexadecimal
        number.
        """
        return hex(self.value).rstrip('L').lower()

    def __len__(self):
        """
        @return: The size of this address (in bits).
        """
        return self.strategy.width

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
        if self.value == other.value:
            return True
        return False

    def __ne__(self, other):
        """
        @return: C{True} if this network address instance does not have the
            same numerical value as another, C{False} otherwise.
        """
        if self.value != other.value:
            return True
        return False

    def __lt__(self, other):
        """
        @return: C{True} if this network address instance has a lower
            numerical value than another, C{False} otherwise.
        """
        if self.value < other.value:
            return True
        return False

    def __le__(self, other):
        """
        @return: C{True} if this network address instance has a lower or
            equivalent numerical value than another, C{False} otherwise.
        """
        if self.value <= other.value:
            return True
        return False

    def __gt__(self, other):
        """
        @return: C{True} if this network address instance has a higher
            numerical value than another, C{False} otherwise.
        """
        if self.value > other.value:
            return True
        return False

    def __ge__(self, other):
        """
        @return: C{True} if this network address instance has a higher or
            equivalent numerical value than another, C{False} otherwise.
        """
        if self.value >= other.value:
            return True
        return False

#-----------------------------------------------------------------------------
class IP(Addr):
    """
    Class representing individual IPv4 or IPv6 addresses.
    """
    #   Class properties.
    STRATEGIES = (ST_IPV4, ST_IPV6)
    ADDR_TYPES = (AT_INET, AT_INET6)

    def __init__(self, addr, addr_type=AT_UNSPEC):
        #   NB - This should only be are accessed via property() methods.
        self.__prefixlen = None

        prefixlen = None
        #   Check for prefix in address and split it out.
        if isinstance(addr, (str, unicode)):
            if '/' in addr:
                (addr, prefixlen) = addr.split('/', 1)

        #   Call superclass constructor before processing subnet prefix to
        #   assign the strategyn object.
        super(IP, self).__init__(addr, addr_type)

        #   Set the subnet prefix.
        if prefixlen is None:
            self.__prefixlen = self.strategy.width
        else:
            self.prefixlen = prefixlen

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   START of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def _get_prefixlen(self):
        return self.__prefixlen

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
        if not 0 <= prefixlen <= self.strategy.width:
            raise ValueError('%d is an invalid CIDR prefix for %s!' \
                % (prefixlen, AT_NAMES[self.addr_type]))

        self.__prefixlen = prefixlen

    prefixlen = property(_get_prefixlen, _set_prefixlen, None,
        """The CIDR subnet prefix for this IP address.""")
    del _get_prefixlen, _set_prefixlen

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   END of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

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
        @return: The number of bits set to one in this address if it is a
        valid netmask, otherwise the width (in bits) for the given address
        type is returned instead.
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
class EUI(Addr):
    """
    Class representing individual MAC, EUI-48 or EUI-64 addresses.
    """
    #   Class properties.
    STRATEGIES = (ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_LINK, AT_EUI64)

    def __init__(self, addr, addr_type=AT_UNSPEC):
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
        self.__first = 0
        self.__last = 0
        self.__strategy = None
        self.__addr_type = None
        self.__klass = None

        self.first = start_addr
        self.last = stop_addr
        self.klass = klass

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   START of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def _get_first(self):
        return self.__first

    def _set_first(self, val):
        if not issubclass(val.__class__, Addr):
            if isinstance(val, (str, unicode)):
                addr = Addr(val)
                self.__first = int(addr)
                self.strategy = addr.strategy
            else:
                raise TypeError('%r is not recognised string format ' \
                    'address or a (sub)class of Addr!' % val)
        else:
            self.__first = int(val)
            self.strategy = val.strategy

    def _get_last(self):
        return self.__last

    def _set_last(self, val):
        if not issubclass(val.__class__, Addr):
            if isinstance(val, (str, unicode)):
                self.__last = int(Addr(val))
            else:
                raise TypeError('%r is not recognised string format ' \
                    'address or a (sub)class of Addr!' % val)
        else:
            self.__last = int(val)

            if self.strategy is not None:
                if self.addr_type != val.addr_type:
                    raise TypeError('start and stop address types are different!')

        if self.last < self.first:
            raise IndexError('start address is greater than stop address!')

    def _get_strategy(self):
        return self.__strategy

    def _set_strategy(self, val):
        print val
        if not issubclass(val.__class__, AddrStrategy):
            raise ValueError('%r is not AddrStrategy (sub)class!' % val)

        if val.max_int < self.last:
            raise ValueError('Present range boundary values exceed ' \
                'maximum values for address type %s!' \
                    % AT_NAMES[val.addr_type])

        self.__strategy = val
        self.__addr_type = self.__strategy.addr_type

    def _get_addr_type(self):
        return self.strategy.addr_type

    def _get_klass(self):
        return self.__klass

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

        self.__klass = val

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
                index_addr = Addr(self.last, self.addr_type)
                index_addr += (index + 1)
                return self._retval(index_addr)
            elif 0 <= index <= (self.size() - 1):
                #   Positive index or zero index.
                index_addr = Addr(self.first, self.addr_type)
                index_addr += index
                return self._retval(index_addr)
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
            if (addr.first >= self.first) and (addr.last <= self.last):
                return True
        else:
            raise TypeError('%r is an unsupported type or class!' % addr)

        return False

    def __eq__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundary of this range is the same as other,
            C{False} otherwise.
        """
        if self.addr_type != other.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if self.first == other.first and self.last == other.last:
            return True

        return False

    def __ne__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the boundary of this range is not the same as
            other, C{False} otherwise.
        """
        if self.addr_type != other.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if self.first == other.first and self.last == other.last:
            return False

        return True

    def __lt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the lower boundary of this range is less than
            other, C{False} otherwise.
        """
        if self.addr_type != other.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if self.first < other.first:
            return True

        return False

    def __le__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the lower boundary of this range is less or equal
            to other, C{False} otherwise.
        """
        if self.addr_type != other.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if self.first <= other.first:
            return True

        return False

    def __gt__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the lower boundary of this range is greater than
            other, C{False} otherwise.
        """
        if self.addr_type != other.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if self.first > other.first:
            return True

        return False

    def __ge__(self, other):
        """
        @param other: an address object of the same address type as C{self}.

        @return: C{True} if the lower boundary of this range is greater or
            equal to other, C{False} otherwise.
        """
        if self.addr_type != other.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if self.first >= other.first:
            return True

        return False

    def __str__(self):
        return "%s-%s" % (self.strategy.int_to_str(self.first),
                          self.strategy.int_to_str(self.last))

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s(%r, %r)" % (self.__class__.__name__,
            self.strategy.int_to_str(self.first), self.strategy.int_to_str(self.last))

#-----------------------------------------------------------------------------
#..........
#   CIDR and Wildcard TODO
#..........

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
        Checks assignments to managed attributes.
        """
        r1 = AddrRange(Addr('192.168.0.250'), Addr('192.168.1.7'), klass=str)
        print r1
        print repr(r1)
        print r1.size()
        print r1[0]
        print r1[-1]
        print list(r1[2:4])

        print '192.168.0.250' in r1

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
