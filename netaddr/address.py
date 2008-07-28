#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
classes and functions representing supported network addresses and associated
aggregate types such as CIDR and Wilcards.
"""
from netaddr.strategy import AT_UNSPEC, AT_LINK, AT_INET, AT_INET6, \
                             AT_EUI64, ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64

#-----------------------------------------------------------------------------
class AddrFormatError(Exception):
    """
   Network address format not recognised.
    """
    pass

#-----------------------------------------------------------------------------
class AddrConversionError(Exception):
    """
   Attempt convert between address types failed.
    """
    pass

#-----------------------------------------------------------------------------
class Addr(object):
    """
    A heuristic-style class whose objects represent any of the supported
    network address types based on the arguments passed to the constructor.

    The address type is auto-detected from the the address or explicitly
    defined via a second address type option.

    Objects of this class behave differently dependent upon the type of
    address they represent.
    """
    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        addr - the string form of a network address, or a network byte order
        integer within the supported range for the address type.

        addr_type - (optional) the network address type. If addr is an integer,
        this argument becomes mandatory.
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

        addr - the string form of a network address, or a network byte order
        int/long value within the supported range for the address type.

        Raises a TypeError if addr is of an unsupported type. Raises an
        OverflowError if addr is an integer outside the bounds for this
        address type.
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
        Returns the value of this address as an network byte order integer.
        """
        return self.value

    def __long__(self):
        """
        Returns the value of this address as an network byte order integer.
        """
        return self.value

    def __str__(self):
        """
        Returns the common string representation for this address type.
        """
        return self.strategy.int_to_str(self.value)

    def __repr__(self):
        """
        Returns an executable Python statement that can be used to recreate an
        object of equivalent value.
        """
        return "netaddr.address.%s(%r)" % (self.__class__.__name__, str(self))

    def bits(self):
        """
        Returns a human-readable binary digit string for this address type.
        """
        return self.strategy.int_to_bits(self.value)

    def __len__(self):
        """
        Returns the size of this address (in bits).
        """
        return self.strategy.width

    def __iter__(self):
        """
        Provide an iterator over words (based on word_size) in this address.
        """
        return iter(self.strategy.int_to_words(self.value))

    def __getitem__(self, index):
        """
        Returns the integer value of the word indicated by index. Raises an
        IndexError exception if index is wrong size for address type

        Full slicing support is also available.
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
        Set the value of the word of this address indicated by index.
        """
        if isinstance(index, slice):
            #   TODO - settable slices.
            raise NotImplementedError

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
        Returns the value of this address as a network byte order hexadecimal
        number.
        """
        return hex(self.value).rstrip('L').lower()

    def __iadd__(self, i):
        """
        Increment network address by specified value.

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
        Decrement network address by specified value.

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
        True if this network address instance has the same numerical value as
        another, False otherwise.
        """
        if int(self) == int(other):
            return True
        return False

    def __lt__(self, other):
        """
        True if this network address instance has a lower numerical value than
        another, False otherwise.
        """
        if int(self) < int(other):
            return True
        return False

    def __le__(self, other):
        """
        True if this network address instance has a lower or equivalent
        numerical value than another, False otherwise.
        """
        if int(self) <= int(other):
            return True
        return False

    def __gt__(self, other):
        """
        True if this network address instance has a higher numerical value
        than another, False otherwise.
        """
        if int(self) > int(other):
            return True
        return False

    def __ge__(self, other):
        """
        True if this network address instance has a higher or equivalent
        numerical value than another, False otherwise.
        """
        if int(self) >= int(other):
            return True
        return False

    def family(self):
        """
        Returns an integer constant identifying this object's address type
        family.
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

        addr - an EUI/MAC address string or a network byte order integer.

        addr_type - (optional) the specific EUI address type (AT_LINK or
        AT_EUI64). If addr is an integer, this argument is mandatory.
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
        Returns the OUI (Organisationally Unique Identifier) for this EUI.
        """
        return '-'.join(["%02x" % i for i in self[0:3]]).upper()

    def ei(self):
        """
        Returns the EI (Extension Identifier) for this EUI.
        """
        if self.strategy == ST_EUI48:
            return '-'.join(["%02x" % i for i in self[3:6]]).upper()
        elif self.strategy == ST_EUI64:
            return '-'.join(["%02x" % i for i in self[3:8]]).upper()

    def eui64(self):
        """
        Returns the value of this EUI object as a new 64-bit EUI object.

        If this object represents an EUI-48 it is converted to EUI-64 as per
        the standard.

        If this object is already and EUI-64, it just returns a new,
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
        Returns an IPv6 IP object initialised using the value of this EUI.

        See RFC 4921 for details.
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
    prefix.

    NB - parsing of the prefix in this class isn't as strict as the CIDR
    aggregate class, which does not allow non zero bits to the right of the
    specified subnet prefix.

    See CIDR() class for further details.
    """
    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        addr - an IPv4 or IPv6 address string with an optional subnet prefix
        or a network byte order integer.

        addr_type - (optional) the IP address type (AT_INET or AT_INET6). If
        addr is an integer, this argument is mandatory.
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
            for strategy in (ST_IPV4, ST_IPV6):
                if strategy.valid_str(addr):
                    self.strategy = strategy
                    break
        elif addr_type == AT_INET:
            self.strategy = ST_IPV4
        elif addr_type == AT_INET6:
            self.strategy = ST_IPV6

        if self.strategy is None:
            #   Whoops - we fell through and didn't match anything!
            raise AddrFormatError("%r is not a recognised IP address format!"\
                % addr)

        if addr is None:
            addr = 0

        self.addr_type = self.strategy.addr_type
        self.setvalue(addr)

    def is_netmask(self):
        """
        Returns True if this addr is a mask that would return a host id,
        False otherwise.
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
        Returns the number of bits set to 1 if this address is a netmask, zero
        otherwise.
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
        Returns the reverse DNS lookup string for this IP address.
        """
        return self.strategy.int_to_arpa(self.value)

    def is_hostmask(self):
        """
        Returns True if this address is a mask that would return a network id,
        False otherwise.
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
        Returns a valid CIDR object for this IP address.
        """
        raise NotImplementedError('TODO. Not yet implemented!')

    def masklen(self):
        """
        Returns the subnet prefix of this IP address.
        """
        raise NotImplementedError('TODO. Not yet implemented!')

    def host(self):
        """
        Returns the IP address value without the subnet prefix.
        """
        raise NotImplementedError('TODO. Not yet implemented!')

    def ipv4(self):
        """
        If object's address type is IPv4 it returns a new IP object that is
        numerically equivalent.

        If object's address type is IPv6 and it's value is mappable to IPv4
        it return a new IP object intialised as an IPv4 address type.

        An AddrConversionError is raised if IPv6 address is not mappable to
        IPv4.
        """
        raise NotImplementedError('TODO. Not yet implemented!')

    def ipv6(self):
        """
        If object's address type is IPv6 it returns a new IPv6 IP object that
        is numerically equivalent.

        If object's address type is IPv4 it returns a new IPv6 IP object
        intialised as an IPv4 mapped address.

        NB - this method uses the preferred IPv4 embedded in IPv6 form :-

        '::ffff:x.x.x.x' (IPv4-mapped IPv6 address)

        over the (now deprecated form) :-

        '::x.x.x.x' (IPv4-Compatible IPv6 address).

        See RFC 4921 for details.
        """
        raise NotImplementedError('TODO. Not yet implemented!')

    def is_unicast(self):
        """
        Returns True if this address is unicast, False otherwise.
        """
        raise NotImplementedError('TODO. Not yet implemented!')

    def is_multicast(self):
        """
        Returns True if this address is multicast, False otherwise.
        """
        raise NotImplementedError('TODO. Not yet implemented!')

#-----------------------------------------------------------------------------
def nrange(start, stop, step=1, klass=None):
    """
    A generator producing sequences of network addresses based on start and
    stop values, in intervals of step.

    start - first network address as string or instance of Addr (sub)class.

    stop - last network address as string or instance of Addr (sub)class.

    step - (optional) size of step between addresses in range. Default is 1.

    klass - (optional) the class used to create objects returned.
    Default: Addr() class.

    a) str returns string representation of network address

    b) int, long and hex return actual values

    c) Addr (sub)class or duck type* return objects of that class.

    * - if you use your own duck class, make sure you handle both arguments
    (addr_value, addr_type) passed to the constructor.
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
    boundaries, unlike CIDR addresses.

    The only network address aggregate supporting all network address types.
    Most AddrRange subclasses only support a subset of address types.
    """
    def __init__(self, start_addr, stop_addr, klass=None):
        """
        Constructor.

        start_addr - start address for this network address range.

        stop_addr - stop address for this network address range.

        klass - (optional) class used to create each object returned.
        Default: Addr() objects.

        See nrange() documentations for additional details on options.
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

    def _retval(self, addr):
        """
        Protected method. *** Not intended for public use ***
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
        Returns the lower boundary network address of this range.
        """
        return self._retval(self.start_addr)

    def last(self):
        """
        Returns the upper boundary network address of this range.
        """
        return self._retval(self.stop_addr)

    def __len__(self):
        """
        Returns the total number of network addresses in this range.

        NB - Use this method only for ranges that contain less than 2 ** 31
        addresses. Raises an IndexError if size is exceeded.
        """
        size = self.size()
        if size > (2 ** 31):
            #   Use size() method in this class instead as len() will b0rk!
            raise IndexError("range contains more than 2^31 addresses! " \
                "Use size() method instead.")
        return size

    def size(self):
        """
        Returns the total number of network addresses in this range.

        NB - Use this method in preference to __len__() when size of ranges
        exceeds 2 ** 31 addresses.
        """
        return int(self.stop_addr) - int(self.start_addr) + 1

    def __getitem__(self, index):
        """
        Returns the network address(es) in this address range indicated by
        index/slice.

        Slicing objects can produce large sequences so generator objects are
        returned instead to the usual sequences. Wrapping a raw slice with
        list() or tuple() may be required dependent on context.
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
        Returns an iterator object providing access to all network addresses
        within this range.
        """
        return nrange(self.start_addr, self.stop_addr, klass=self.klass)

    def __contains__(self, addr):
        """
        Returns True if given address or range falls within this range, False
        otherwise.

        addr - object of Addr/AddrRange (sub)class or a network address string
        to be compared.
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
        True if the boundary of this range is the same as other, False
        otherwise.

        NB - address types of self and other must match.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) == int(other.start_addr):
            if int(self.stop_addr) == int(other.stop_addr):
                return True

        return False

    def __ne__(self, other):
        """
        True if the boundary of this range is not the same as other, False
        otherwise.

        NB - address types of self and other must match.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) != int(other.start_addr):
            return True

        return False

    def __lt__(self, other):
        """
        True if the lower boundary of this range is less than other,
        False otherwise.

        NB - address types of self and other must match.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) < int(other.start_addr):
            return True

        return False

    def __le__(self, other):
        """
        True if the lower boundary of this range is less or equal to other,
        False otherwise.

        NB - address types of self and other must match.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) <= int(other.start_addr):
            return True

        return False

    def __gt__(self, other):
        """
        True if the lower boundary of this range is greater than other,
        False otherwise.

        NB - address types of self and other must match.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) > int(other.start_addr):
            return True

        return False

    def __ge__(self, other):
        """
        True if the lower boundary of this range is greater or equal to other,
        False otherwise.

        NB - address types of self and other must match.
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
        Returns an executable Python statement that can be used to recreate an
        object of equivalent value.
        """
        return "netaddr.address.%s(%r, %r)" % (self.__class__.__name__,
            str(self.start_addr), str(self.stop_addr))

#-----------------------------------------------------------------------------
def abbrev_to_cidr(addr):
    """
    Returns a verbose CIDR from an abbreviated CIDR or old-style classful
    network address, None if format provided was not recognised or supported.

    Uses the old-style classful IP address rules to decide on a default subnet
    prefix if one is not explicitly provided.

    Only supports IPv4 and IPv4 mapped IPv6 addresses.

    Examples :-

    10                  - 10.0.0.0/8
    10/16               - 10.0.0.0/16
    128                 - 128.0.0.0/16
    128/8               - 128.0.0.0/8
    192.168             - 192.168.0.0/16
    ::192.168           - ::192.168.0.0/128
    ::ffff:192.168/120  - ::ffff:192.168.0.0/120
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

    CIDR does not accept any non zero bits to be set right of the applied
    bitmask (unlike the IP class which does). Doing so raises an
    AddrFormatError exception.

    Examples of supported formats :-

    1) CIDR address format - <address>/<mask_length>

    192.168.0.0/16

    2) Address and subnet mask combo :-

    192.168.0.0/255.255.0.0

    3) Partial or abbreviated formats. Prefixes may be omitted and in this
    case old classful default prefixes apply :-

    10   - 10.0.0.0/8
    10.0 - 10.0.0.0/8
    10/8 - 10.0.0.0/8

    128    - 10.0.0.0/16
    128.0  - 10.0.0.0/16
    128/16 - 10.0.0.0/16

    192        - 10.0.0.0/24
    192.168.0  - 192.168.0.0/24
    192.168/16 - 192.168.0.0/16
    """
    def __init__(self, addr_mask, klass=IP):
        """
        Constructor.

        addr_mask - a valid IPv4 or IPv6 CIDR address.

        klass - (optional) class used to create each return object.
        Default: IP objects

        See nrange() documentations for additional details on options.
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

        self._addr = addr

        if not 0 <= prefixlen <= self._addr.strategy.width:
            raise IndexError('CIDR prefix out of bounds for %s addresses!' \
                % self._addr.strategy.name)

        self.mask_len = prefixlen
        width = self._addr.strategy.width
        self.addr_type = self._addr.strategy.addr_type

        int_hostmask = (1 << (width - self.mask_len)) - 1
        int_stop = int(self._addr) | int_hostmask
        int_start = int_stop - int_hostmask
        int_netmask = self._addr.strategy.max_int ^ int_hostmask

        start_addr = IP(int_start, self.addr_type)
        stop_addr = IP(int_stop, self.addr_type)

        super(self.__class__, self).__init__(start_addr, stop_addr,
              klass=klass)

        self.netmask_addr = IP(int_netmask, self.addr_type)
        self.hostmask_addr = IP(int_hostmask, self.addr_type)

    def addr(self):
        """
        Returns the network address used to initialize this CIDR range.
        """
        if self.klass in (str, unicode):
            return str(self._addr)
        elif self.klass in (int, long, hex):
            return self.klass(int(self._addr))
        else:
            return self.klass(int(self._addr), self.addr_type)

    def netmask(self):
        """
        Returns the subnet mask address of this CIDR range.
        """
        return self._retval(self.netmask_addr)

    def hostmask(self):
        """
        Returns the host mask address of this CIDR range.
        """
        return self._retval(self.hostmask_addr)

    def prefixlen(self):
        """
        Returns size of mask (in bits) of this CIDR range.
        """
        return self.mask_len

    def __str__(self):
        return "%s/%d" % (self.start_addr, self.mask_len)

    def __repr__(self):
        """
        Returns an executable Python statement that can be used to recreate an
        object of equivalent value.
        """
        return "netaddr.address.%s('%s/%d')" % (self.__class__.__name__,
            str(self._addr), self.mask_len)

    def wildcard(self):
        """
        Returns a Wildcard range equivalent to this CIDR range.

        If CIDR was initialised with klass=str a wildcard string is returned,
        in all other cases a Wildcard object is returned.

        NB - Only supports IPv4 CIDR addresses.
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

    Individual octets can be represented using the following shortcuts :-

    1) The asterisk '*' octet.

    This represents the values 0 through 255.

    2) The hyphenated octet 'x-y'

    This represents a range of values between x and y.

    x must always be greater than y, therefore :-

    values of x are 0 through 254
    values of y are 1 through 255

    NB - only one hyphenated octet per wildcard is allowed and only asterisks
    are permitted after a hyphenated octet.

    Example wildcards :-

    '192.168.0.1'       #   a single address
    '192.168.0.0-31'    #   32 addresses
    '192.168.0.*'       #   256 addresses
    '192.168.0-1.*'     #   512 addresses
    '192.168-169.*.*'   #   131,072 addresses
    '*.*.*.*'           #   the whole IPv4 address space

    Aside: Wildcard ranges are not directly equivalent to CIDR ranges as they
    can represent address ranges that do not fall on strict bit mask
    boundaries. All CIDR ranges can be represented as wildcard ranges but the
    reverse isn't always true.
    """
    def __init__(self, wildcard, klass=IP):
        """
        Constructor.

        wildcard - a valid IPv4 wildcard address.

        klass - (optional) class used to create each return object.
        Default: IP objects. See nrange() documentations for
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
        Returns a valid CIDR object for this wildcard. If conversion fails a
        AddrConversionError exception is raised as not all wildcards ranges
        are valid CIDR ranges.
        """
        raise NotImplementedError('TODO. Not yet implemented!')

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
        Returns an executable Python statement that can be used to recreate an
        object of equivalent value.
        """
        return "netaddr.address.%s(%r)" % (self.__class__.__name__, str(self))

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    pass
