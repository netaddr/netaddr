#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
classes and functions representing supported network addresses and associated
aggregation options.
"""
from netaddr.strategy import AT_UNSPEC, AT_LINK, AT_INET, AT_INET6, \
                             AT_EUI64, ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64

#-----------------------------------------------------------------------------
_TRANSLATE_STR = ''.join([chr(_i) for _i in range(256)])

#-----------------------------------------------------------------------------
class Addr(object):
    """
    A class whose objects represent network addresses of different types based
    on arguments passed to the constructor.

    The address type can either be auto-detected from the string form of the
    address or specified explicitly via the second argument.

    The behaviour of this class varies depending on the type of address that
    it represents.
    """
    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        addr - the string form of a network address, or a network byte order
        int/long value within the supported range for the address type.

        addr_type - (optional) the network address type. If addr is an int or
        long, this argument becomes mandatory.
        """
        if not isinstance(addr, (str, unicode, int, long)):
            raise Exception("addr must be an address in string form or a " \
                "positive int/long!")

        if isinstance(addr, (int, long)) and addr_type is None:
            raise Exception("addr_type must be provided with  int/long " \
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
            raise Exception("Failed to detect address type from %r!" % addr)

        if addr is None:
            addr = 0

        self.addr_type = self.strategy.addr_type
        self.setvalue(addr)

    def setvalue(self, addr):
        """
        Sets the value of this address.

        addr - the string form of a network address, or a network byte order
        int/long value within the supported range for the address type.

        Raises a TypeError if addr is of an unsupported type.

        Raises an OverflowError if addr is an int/long value that is is out of
        bounds for the address type this instance represents.
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
        Returns the value of this address as an network byte order int, if
        possible.

        If the value of int is greater than 2 ** 31 - 1, a long is returned
        instead of an int (standard Python behaviour).
        """
        return self.value

    def __long__(self):
        """
        Returns the value of this address as a network byte order long int.

        If the value of int is less than 2 ** 31 - 1, an int is returned
        instead of a long (standard Python behaviour).
        """
        return self.value

    def __str__(self):
        """
        Return the string representation for this address. Format varies
        dependent on address type.
        """
        return self.strategy.int_to_str(self.value)

    def __repr__(self):
        return "netaddr.address.%s(%r)" % (self.__class__.__name__, str(self))

    def bits(self):
        """
        Return a human-readable binary digit string representation of this
        address.
        """
        return self.strategy.int_to_bits(self.value)

    def __len__(self):
        """
        Return the size of this address (in bits).
        """
        return self.strategy.width

    def __iter__(self):
        """
        Provide an iterator over words (based on word_size) in this address.
        """
        return iter(self.strategy.int_to_words(self.value))

    def __getitem__(self, index):
        """
        Return the integer value of the word indicated by index. Raises an
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
        string.
        """
        return hex(self.value).rstrip('L').lower()

    def __iadd__(self, increment):
        """
        Increment the value of this network address by the specified value.

        If the result exceeds maximum value for the address type, it rolls
        around the minimum boundary value.
        """
        try:
            new_value = self.value + increment
            if new_value > self.strategy.max_int:
                #   Roll around on integer boundaries.
                self.value = new_value - (self.strategy.max_int + 1)
            else:
                self.value = new_value
        except TypeError:
            raise Exception('Increment requires int or long!')

        return self

    def __isub__(self, decrement):
        """
        Decrement the value of this network address by specified value.

        If the result is lower than the address type mininum value it rolls
        around the maximum boundary value.
        """
        try:
            new_value = self.value - decrement
            if new_value < self.strategy.min_int:
                #   Roll around on integer boundaries.
                self.value = new_value + (self.strategy.max_int + 1)
            else:
                self.value = new_value
        except TypeError:
            raise Exception('Decrement requires int or long!')

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


#-----------------------------------------------------------------------------
class EUI(Addr):
    """
    A class whose objects represent IEEE Extended Unique Identifiers. Supports
    EUI-48 (along with common MAC flavours) and EUI-64.
    """
    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        addr - the string form of an EUI-48/64 address or a network byte
        order int/long value.

        addr_type - (optional) the EUI address type (AT_LINK or AT_EUI64). If
        addr is an int or long, this argument becomes mandatory.
        """
        if not isinstance(addr, (str, unicode, int, long)):
            raise Exception("addr must be an address in string form or a " \
                "positive int/long!")

        if isinstance(addr, (int, long)) and addr_type is None:
            raise Exception("addr_type must be provided with  int/long " \
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
            raise Exception("Failed to detect EUI type from %r!" % addr)

        if addr is None:
            addr = 0

        self.addr_type = self.strategy.addr_type
        self.setvalue(addr)

    def oui(self):
        """
        Returns the OUI (Organisationally Unique Identifier for this
        EUI-48/MAC address.
        """
        return '-'.join(["%02x" % i for i in self[0:3]]).upper()

    def ei(self):
        """
        Returns the EI (Extension Identifier) for this EUI-48 address.
        """
        if self.strategy == ST_EUI48:
            return '-'.join(["%02x" % i for i in self[3:6]]).upper()
        elif self.strategy == ST_EUI64:
            return '-'.join(["%02x" % i for i in self[3:8]]).upper()

    def to_eui64(self):
        """
        Returns the value of this EUI object as a new EUI address initialised
        as a 64-bit EUI.

        So if this address represents an EUI-48 address it converts the value
        of this address to EUI-64 as per the standard.

        If this class is already and EUI-64 address, it just returns a new
        object that is numerically equivalent to itself.
        """
        if self.addr_type == AT_LINK:
            eui64_words = ["%02x" % i for i in self[0:3]] + ['ff', 'fe'] + \
                     ["%02x" % i for i in self[3:6]]

            return self.__class__('-'.join(eui64_words))
        else:
            return EUI(str(self))

    def ipv6_link_local(self):
        """
        Returns an IP() object class (IPv6 address type) initialised using the
        value of this EUI.
        """
        prefix = 'fe80:0000:0000:0000:'

        #   Add 2 to the first octet of this MAC address temporarily.
        self[0] += 2

        if self.addr_type == AT_LINK:
            #   Modify MAC to make it an EUI-64.
            suffix = ["%02x" % i for i in self[0:3]] + ['ff', 'fe'] + \
                     ["%02x" % i for i in self[3:6]]
        else:
            suffix = ["%02x" % i for i in list(self)]

        suffix = ["%02x%02x" % (int(x[0], 16), int(x[1], 16)) for x in \
            zip(suffix[::2], suffix[1::2])]

        #   Subtract 2 again to return MAC address to original value.
        self[0] -= 2

        eui64 = ':'.join(suffix)
        addr = prefix + eui64
        return IP(addr)


#-----------------------------------------------------------------------------
class IP(Addr):
    """
    A class whose objects represent Internet Protocol network addresses that
    can be either IPv4 or IPv6.
    """
    def __init__(self, addr, addr_type=AT_UNSPEC):
        """
        Constructor.

        addr - the string form of a IPv4 or IPv6 address, or a network byte
        order int/long value.

        addr_type - (optional) the IP address type (AT_INET or AT_INET6). If
        addr is an int or long, this argument becomes mandatory.
        """
        if not isinstance(addr, (str, unicode, int, long)):
            raise Exception("addr must be an address in string form or a " \
                "positive int/long!")

        if isinstance(addr, (int, long)) and addr_type is None:
            raise Exception("addr_type must be provided with  int/long " \
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
            raise Exception("Failed to detect IP version from %r!" % addr)

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
        mask_bits = bits.translate(_TRANSLATE_STR, '.0')
        mask_length = len(mask_bits)

        if not 1 <= mask_length <= self.strategy.width:
            raise Exception('Unexpected mask length %d for address type!' \
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

#-----------------------------------------------------------------------------
def nrange(start, stop, step=1, klass=None):
    """
    A generator producing sequences of addresses based on start and stop
    values, in intervals of step.

    start - first network address as string or instance of Addr (sub)class.

    stop - last network address as string or instance of Addr (sub)class.

    step - (optional) size of step between addresses in range. Default is 1.

    klass - (optional) a class used to create each object returned.
    Default: Addr objects.

    a) str returns string representation of network address

    b) int, long and hex return actual values

    c) Addr (sub)class or duck type(*) return objects of that class.

    (*) - if you use your own duck class, make sure you handle 2 arguments
    passed in (addr_value, addr_type) to avoid frustration.
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
        #   Yield raw value of iterator.
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
        #   Yield string representation of address type.
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
        #   Yield network address object.
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
    Represents a block of contiguous network addresses bounded by an arbitrary
    start and stop address. There is no requirement that they fall on strict
    bit mask boundaries.

    This is the only network address aggregate class that supports all network
    address types (essentially Addr (sub)class objects). Most if not all
    subclasses of AddrRange tend towards support for only a subset of address
    types.
    """
    def __init__(self, start_addr, stop_addr, klass=None):
        """
        Constructor.

        start_addr - start address for this network address range.

        stop_addr - stop address for this network address range.

        klass - (optional) class used to create each return object.
        Default: Addr objects. See nrange() documentations for
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

            #   Make klass the same class as start_addr object.
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
        Protected method. Not for public use!
        """
        #   Decides on the flavour of a value to be return based on klass
        #   setting.
        if self.klass in (str, unicode):
            return str(addr)
        elif self.klass in (int, long, hex):
            return self.klass(int(addr))
        else:
            return self.klass(int(addr), self.addr_type)

    def first(self):
        """
        Returns the Addr instance for the lower boundary of this network
        address range.
        """
        return self._retval(self.start_addr)

    def last(self):
        """
        Returns the Addr instance for the upper boundary of this network
        address range.
        """
        return self._retval(self.stop_addr)

    def __len__(self):
        """
        Return total number of addresses to be found in this address range.

        NB - Use this method only for ranges that contain less than 2 ** 31
        addresses. Raises an IndexError if size is exceeded.
        """
        size = self.size()
        if size > (2 ** 31):
            #   Use size() method in this class instead as len() will b0rk!
            raise IndexError("AddrRange contains more than 2^31 addresses! " \
                "Try using size() method instead.")
        return size

    def size(self):
        """
        Return total number of addresses to be found in this address range.

        NB - Use this method in preference to __len__() when size of ranges
        exceeds 2 ** 31 addresses.
        """
        return int(self.stop_addr) - int(self.start_addr) + 1

    def __getitem__(self, index):
        """
        Return the Addr instance from this address range indicated by index
        or slice.

        Raises an IndexError exception if index is out of bounds in relation
        to size of address range.

        Slicing objects of this class can potentially produce truly massive
        sequences so generators are returned in preference to sequences. The
        extra step of wrapping a raw slice with list() or tuple() may be
        required dependent on context.
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
        Returns an iterator object providing lazily evaluated access to all
        Addr() instances within this network address range.
        """
        return nrange(self.start_addr, self.stop_addr, klass=self.klass)

    def __contains__(self, addr):
        """
        Returns True if given address or address range falls within the
        boundary of this network address False otherwise.

        addr - object of (sub)class Addr/AddrRange or string based address to
        be compared.
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
            raise Exception('%r is an unsupported object/type!' % addr)

        return False

    def __eq__(self, other):
        """
        True if the boundary addresses of this address range are the same as
        those of the other and the address types they represent are the same,
        False otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) == int(other.start_addr):
            if int(self.stop_addr) == int(other.stop_addr):
                return True

        return False

    def __ne__(self, other):
        """
        True if the boundary addresses of this address range are not the same
        as those of the other, False otherwise.

        Raises a TypeError if address type of other is not the same as self.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) != int(other.start_addr):
            return True

        return False

    def __lt__(self, other):
        """
        True if the lower boundary address of this address range is less than
        that of the other and the address types they represent are the same,
        False otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) < int(other.start_addr):
            return True

        return False

    def __le__(self, other):
        """
        True if the lower boundary address of this address range is less than
        or equal to that of the other and the address types they represent
        are the same, False otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) <= int(other.start_addr):
            return True

        return False

    def __gt__(self, other):
        """
        True if the lower boundary address of this address range is greater
        than that of the other and the address types they represent are the
        same, False otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) > int(other.start_addr):
            return True

        return False

    def __ge__(self, other):
        """
        True if the lower boundary address of this address range is greater
        than or equal to that of the other and the address types they
        represent are the same, False otherwise.
        """
        if self.start_addr.addr_type != other.start_addr.addr_type:
            raise TypeError('comparison failure due to type mismatch!')

        if int(self.start_addr) >= int(other.start_addr):
            return True

        return False

    def __str__(self):
        return "%s-%s" % (self.start_addr, self.stop_addr)

    def __repr__(self):
        return "netaddr.address.%s(%r, %r)" % (self.__class__.__name__,
            str(self.start_addr), str(self.stop_addr))

#-----------------------------------------------------------------------------
class CIDR(AddrRange):
    """
    Represents a block of contiguous IPv4/IPv6 network addresses defined by an
    IP address prefix and either a prefix mask measured in bits or
    alternatively a traditional subnet mask in IP address format.

    Examples of supported formats :-

    1) CIDR address format - <address>/<mask_length>

    192.168.0.0/16

    2) Address and subnet mask combo :-

    192.168.0.0/255.255.0.0
    """
    def __init__(self, addr_mask, klass=IP):
        """
        Constructor.

        addr_mask - a valid CIDR address (IPv4 and IPv6 types supported).

        klass - (optional) class used to create each return object.
        Default: IP objects. See nrange() documentations for
        additional details on options.
        """
        tokens = addr_mask.split('/')

        if len(tokens) != 2:
            raise Exception('%r is not a recognised CIDR format!' \
                % addr_mask)

        addr = IP(tokens[0])

        try:
            #   Try int value.
            prefixlen = int(tokens[1])
        except ValueError:
            #   Try subnet mask.
            mask = IP(tokens[1])
            if not mask.is_netmask():
                raise Exception('%r does not contain a valid subnet mask!' \
                    % addr_mask)
            prefixlen = mask.prefixlen()
            if mask.addr_type != addr.addr_type:
                raise Exception('Address and netmask types do not match!')

        self._addr = addr

        if not 0 <= prefixlen <= self._addr.strategy.width:
            raise IndexError('CIDR prefix is out of bounds for %s addresses' \
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
        Returns the subnet mask address for this CIDR range.
        """
        return self._retval(self.netmask_addr)

    def hostmask(self):
        """
        Returns the host mask address for this CIDR range.
        """
        return self._retval(self.hostmask_addr)

    def prefixlen(self):
        """
        Returns size of mask (in bits) for this CIDR range.
        """
        return self.mask_len

    def __str__(self):
        return "%s/%d" % (self.start_addr, self.mask_len)

    def __repr__(self):
        return "netaddr.address.%s('%s/%d')" % (self.__class__.__name__,
            str(self._addr), self.mask_len)

#-----------------------------------------------------------------------------
class Wildcard(AddrRange):
    """
    Represents a block of contiguous IPv4 network addresses defined using a
    wildcard/glob style syntax.

    Individual octets can be represented using the following shortcuts :-

    1) The asterisk '*' octet.

    This represents the values 0 through 255.

    2) The hyphenated octet 'x-y'

    This represents a range of values between x and y.

    x must always be greater than y, therefore :-

    values of x are 0 through 254
    values of y are 1 through 255

    NB - only one hyphenated octet per wildcard is allowed.

    Example wildcards :-

    '192.168.0.1'       #   a single address
    '192.168.0.0-31'    #   32 addresses
    '192.168.0.*'       #   256 addresses
    '192.168.0-1.*'     #   512 addresses
    '192.168-169.*.*'   #   131,072 addresses
    '*.*.*.*'           #   the whole IPv4 address space

    Aside: Wildcard ranges are not directly equivalent to CIDR ranges as they
    can represent address ranges that do not conform to bit mask boundaries.
    All CIDR ranges can be represented as wilcard ranges but the reverse isn't
    always true.
    """
    def __init__(self, wildcard, klass=IP):
        """
        Constructor.

        wildcard - a valid wildcard address (only IPv4 is supported).

        klass - (optional) class used to create each return object.
        Default: IP objects. See nrange() documentations for
        additional details on options.
        """
        if not self.is_wildcard(wildcard):
            raise Exception('Invalid wildcard address range %r!' \
                % wildcard)

        l_tokens = []
        u_tokens = []

        for octet in wildcard.split('.'):
            if '-' in octet:
                oct_tokens = octet.split('-')
                l_tokens += [oct_tokens[0]]
                u_tokens += [oct_tokens[1]]
            elif octet == '*':
                l_tokens += ['0']
                u_tokens += ['255']
            else:
                l_tokens += [octet]
                u_tokens += [octet]

        start_addr = IP('.'.join(l_tokens))
        stop_addr = IP('.'.join(u_tokens))

        if start_addr.addr_type != AT_INET:
            raise Exception('%s is an invalid IPv4 wildcard!' % start_addr)

        super(self.__class__, self).__init__(start_addr, stop_addr,
              klass=klass)

    def is_wildcard(self, wildcard):
        """
        True if wildcard address is valid, False otherwise.
        """
        seen_hyphen = False
        seen_asterisk = False

        try:
            octets = wildcard.split('.')
            if len(octets) != 4:
                return False
            for octet in octets:
                if '-' in octet:
                    if seen_hyphen:
                        return False
                    seen_hyphen = True

                    if seen_asterisk:
                        #   Asterisks cannot precede hyphenated octets.
                        return False
                    (oct1, oct2) = map(lambda x: int(x), octet.split('-'))
                    if oct1 >= oct2:
                        return False
                    if not 0 <= oct1 <= 254:
                        return False
                    if not 1 <= oct2 <= 255:
                        return False
                elif octet == '*':
                    seen_asterisk = True
                elif octet != '*':
                    if not 0 <= int(octet) <= 255:
                        return False
        except AttributeError:
            return False
        except ValueError:
            return False
        return True

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
                        raise Exception('only one hyphenated octet ' \
                            ' per wildcard allowed!')
                else:
                    raise Exception('asterisks not permitted before ' \
                        'hyphenated octets!')

        return '.'.join(tokens)

    def __repr__(self):
        return "netaddr.address.%s(%r)" % (self.__class__.__name__, str(self))

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    pass
