#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network address type logic, constants used to identify them and shared
strategy objects.
"""
import socket as _socket
import struct as _struct

USE_IPV4_OPT=True   #: Use IPv4 optimised strategy class? Default: True

try:
    #   The following call erroneous raises errors on various Python
    #   implementations.
    _socket.inet_aton('255.255.255.255')
except:
    USE_IPV4_OPT=False

from netaddr import BIG_ENDIAN_PLATFORM, AT_UNSPEC, AT_INET, AT_INET6, \
                    AT_LINK, AT_EUI64, AT_NAMES

#-----------------------------------------------------------------------------
def _BYTES_TO_BITS():
    """
    Generates a 256 element list of 8-bit binary digit strings. List index is
    equivalent to the bit string value.
    """
    lookup = []
    bits_per_byte = range(7, -1, -1)
    for num in range(256):
        bits = 8*[None]
        for i in bits_per_byte:
            bits[i] = '01'[num&1]
            num >>= 1
        lookup.append(''.join(bits))
    return lookup

_BYTES_TO_BITS = _BYTES_TO_BITS()

#-----------------------------------------------------------------------------
class AddrStrategy(object):
    """
    Very basic support for all common operations performed on each network
    type.

    There are usually subclasses for each address type that over-ride methods
    implemented here to optimise their performance and add additional
    features.
    """
    def __init__(self, width, word_size, delimiter, word_fmt='%x',
                 addr_type=AT_UNSPEC, hex_words=True, to_upper=False):

        self.width = width
        self.min_int = 0
        self.max_int = 2 ** width - 1
        self.word_size = word_size
        self.word_count = width / word_size
        self.min_word = 0
        self.max_word = 2 ** word_size - 1
        self.delimiter = delimiter
        self.word_fmt  = word_fmt
        self.hex_words = hex_words
        self.word_base = 16
        self.addr_type = addr_type
        self.to_upper = to_upper

        if self.hex_words is False:
            self.word_base = 10

        try:
            self.name = AT_NAMES[addr_type]
        except KeyError:
            self.name = AT_NAMES[AT_UNSPEC]

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s(%r, %r, %r, %r, %r, %r)" % \
            (self.__class__.__name__, self.width, self.word_size,
            self.delimiter, self.addr_type, self.hex_words, self.to_upper)

    #-------------------------------------------------------------------------
    #   Binary methods.
    #-------------------------------------------------------------------------

    def valid_bits(self, bits):
        """
        @param bits: A network address in readable binary form.

        @return: C{True} if network address is valid for this address type,
            C{False} otherwise.
        """
        if not isinstance(bits, (str, unicode)):
            return False

        bits = bits.replace(self.delimiter, '')

        if len(bits) != self.width:
            return False

        try:
            if self.min_int <= int(bits, 2) <= self.max_int:
                return True
        except ValueError:
            return False
        return False

    def bits_to_int(self, bits):
        """
        @param bits: A network address in readable binary form.

        @return: A network byte order integer that is equivalent to value
            represented by network address in readable binary form.
        """
        words = self.bits_to_words(bits)
        return self.words_to_int(words)

    def bits_to_str(self, bits):
        """
        @param bits: A network address in readable binary form.

        @return: A network address in string form that is equivalent to value
            represented by network address in readable binary form.
        """
        words = self.bits_to_words(bits)
        return self.words_to_str(words)

    def bits_to_words(self, bits):
        """
        @param bits: A network address in readable binary form.

        @return: An integer word sequence that is equivalent to value
            represented by network address in readable binary form.
        """
        if not self.valid_bits(bits):
            raise ValueError('%r is not a valid binary form string for ' \
                'address type!' % bits)

        word_bits = bits.split(self.delimiter)
        if len(word_bits) != self.word_count:
            raise ValueError('invalid number of words within binary form ' \
                'string for address type!' % bits)

        return tuple([int(i, 2) for i in word_bits])

    #-------------------------------------------------------------------------
    #   Integer methods.
    #-------------------------------------------------------------------------

    def valid_int(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: C{True} if network byte order integer falls within the
            boundaries of this address type, C{False} otherwise.
        """
        if not isinstance(int_val, (int, long)):
            return False

        if self.min_int <= int_val <= self.max_int:
            return True

        return False

    def int_to_str(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: A network address in string form that is equivalent to value
            represented by a network byte order integer.
        """
        words = self.int_to_words(int_val)
        tokens = [self.word_fmt % i for i in words]
        addr = self.delimiter.join(tokens)

        if self.to_upper is True:
            return addr.upper()

        return addr

    def int_to_bits(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: A network address in readable binary form that is equivalent
            to value represented by a network byte order integer.
        """
        bit_words = []
        for word in self.int_to_words(int_val):
            bits = self.word_to_bits(word)
            bit_words.append(bits)

        return self.delimiter.join(bit_words)

    def int_to_words(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: An integer word sequence that is equivalent to value
            represented by a network byte order integer.
        """
        if not self.valid_int(int_val):
            raise ValueError('%r is not a valid integer value for this ' \
                'address type!' % int_val)

        words = []
        for i in range(self.word_count):
            word = int_val & (2 ** self.word_size - 1)
            words.append(int(word))
            int_val >>= self.word_size

        words.reverse()
        return tuple(words)

    #-------------------------------------------------------------------------
    #   String methods.
    #-------------------------------------------------------------------------

    def valid_str(self, addr):
        """
        @param addr: A network address in string form.

        @return: C{True} if network address in string form is valid for this
            address type, C{False} otherwise.
        """
        if not isinstance(addr, (str, unicode)):
            return False

        tokens = addr.split(self.delimiter)
        if len(tokens) != self.word_count:
            return False

        try:
            for token in tokens:
                if not self.min_word <= int(token, self.word_base) <= \
                       self.max_word:
                    return False
        except TypeError:
            return False
        except ValueError:
            return False
        return True

    def str_to_int(self, addr):
        """
        @param addr: A network address in string form.

        @return: A network byte order integer that is equivalent to value
            represented by network address in string form.
        """
        words = self.str_to_words(addr)
        return self.words_to_int(words)

    def str_to_bits(self, addr):
        """
        @param addr: A network address in string form.

        @return: A network address in readable binary form that is equivalent
            to value represented by network address in string form.
        """
        words = self.str_to_words(addr)
        return self.words_to_bits(words)

    def str_to_words(self, addr):
        """
        @param addr: A network address in string form.

        @return: An integer word sequence that is equivalent in value to the
            network address in string form.
        """
        if not self.valid_str(addr):
            raise ValueError('%r is not a recognised string representation' \
                ' of this address type!' % addr)

        words = addr.split(self.delimiter)
        return tuple([ int(word, self.word_base) for word in words ])

    #-------------------------------------------------------------------------
    #   Word list methods.
    #-------------------------------------------------------------------------

    def valid_words(self, words):
        """
        @param words: A list or tuple containing integer word values.

        @return: C{True} if word sequence is valid for this address type,
            C{False} otherwise.
        """
        if not isinstance(words, (list, tuple)):
            return False

        if len(words) != self.word_count:
            return False

        for i in words:
            if not isinstance(i, (int, long)):
                return False

            if not self.min_word <= i <= self.max_word:
                return False
        return True

    def words_to_int(self, words):
        """
        @param words: A list or tuple containing integer word values.

        @return: A network byte order integer that is equivalent to value
            represented by word sequence.
        """
        if not self.valid_words(words):
            raise ValueError('%r is not a valid word list!' % words)

        #   tuples have no reverse() method and reversed() is only available
        #   in Python 2.4. Ugly but necessary.
        if isinstance(words, tuple):
            words = list(words)
        words.reverse()

        int_val = 0
        for i, num in enumerate(words):
            word = num
            word = word << self.word_size * i
            int_val = int_val | word

        return int_val

    def words_to_str(self, words):
        """
        @param words: A list or tuple containing integer word values.

        @return: A network address in string form that is equivalent to value
            represented by word sequence.
        """
        if not self.valid_words(words):
            raise ValueError('%r is not a valid word list!' % words)

        tokens = [self.word_fmt % i for i in words]
        addr = self.delimiter.join(tokens)
        return addr

    def words_to_bits(self, words):
        """
        @param words: A list or tuple containing integer word values.

        @return: A network address in readable binary form that is equivalent
            to value represented by word sequence.
        """
        if not self.valid_words(words):
            raise ValueError('%r is not a valid word list!' % words)

        bit_words = []
        for word in words:
            bits = self.word_to_bits(word)
            bit_words.append(bits)

        return self.delimiter.join(bit_words)

    #-------------------------------------------------------------------------
    #   Other methods.
    #-------------------------------------------------------------------------

    def word_to_bits(self, int_val):
        """
        @param int_val: An individual integer word value.

        @return: An integer word value for this address type in a fixed width
            readable binary form.
        """
        bits = []

        while int_val:
            bits.append(_BYTES_TO_BITS[int_val&255])
            int_val >>= 8

        bits.reverse()
        bit_str = ''.join(bits) or '0'*self.word_size
        return ('0'*self.word_size+bit_str)[-self.word_size:]

    def description(self):
        """
        @return: String detailing setup of this L{AddrStrategy} instance.
            Useful for debugging.
        """
        tokens = []
        for k in sorted(self.__dict__):
            v = self.__dict__[k]
            if isinstance(v, bool):
                tokens.append("%s: %r" % (k, v))
            elif isinstance(v, (int, long)):
                tokens.append(
                    "%s: %r (%s)" % (k, v, hex(v).rstrip('L').lower()))
            else:
                tokens.append("%s: %r" % (k, v))
        return "\n".join(tokens)

#-----------------------------------------------------------------------------
class IPv4StrategyStd(AddrStrategy):
    """
    A 'safe' L{AddrStrategy} for IPv4 addresses. Unlike L{IPv4StrategyOpt}.

    It contains all methods related to IPv4 addresses that the optimised
    version has, without the reliance on the socket or struct modules. There
    are several cases where the use of this class are preferable when either
    the modules mentioned do not exist on certain Python implementations or
    contain bugs like the infamous inet_aton('255.255.255.254') bug.

    All methods shared between the optimised class and this one should be
    defined here.
    """
    def __init__(self):
        """Constructor."""
        super(IPv4StrategyStd, self).__init__(width=32, word_size=8,
              word_fmt='%d', delimiter='.', addr_type=AT_INET,
              hex_words=False)

    def int_to_arpa(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: The reverse DNS lookup for an IPv4 address in network byte
            order integer form.
        """
        words = ["%d" % i for i in self.int_to_words(int_val)]
        words.reverse()
        words.extend(['in-addr', 'arpa', ''])
        return '.'.join(words)

#-----------------------------------------------------------------------------
class IPv4StrategyOpt(IPv4StrategyStd):
    """
    An optimised L{AddrStrategy} for IPv4 addresses.

    It uses C{pack()} and C{unpack()} from the C{struct} module along with the
    C{inet_ntoa()} and C{inet_aton()} from the C{socket} module great improve
    the speed of certain operations (approx. 2.5 times faster than a standard
    L{AddrStrategy} configured for IPv4).

    However, keep in mind that these modules might not be available everywhere
    that Python itself is. Runtimes such as Google App Engine gut the
    C{socket} module. C{struct} is also limited to processing 32-bit integers
    which is fine for IPv4 but isn't suitable for IPv6.
    """
    def __init__(self):
        """Constructor."""
        super(IPv4StrategyOpt, self).__init__()

    def str_to_int(self, addr):
        """
        @param addr: An IPv4 dotted decimal address in string form.

        @return: A network byte order integer that is equivalent to value
            represented by the IPv4 dotted decimal address string.
        """
        if not self.valid_str(addr):
            raise ValueError('%r is not a valid IPv4 dotted decimal' \
                ' address string!' % addr)
        return _struct.unpack('>I', _socket.inet_aton(addr))[0]

    def int_to_str(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: An IPv4 dotted decimal address string that is equivalent to
            value represented by a 32 bit integer in network byte order.
        """
        if not self.valid_int(int_val):
            raise ValueError('%r is not a valid 32-bit integer!' % int_val)
        return _socket.inet_ntoa(_struct.pack('>I', int_val))

    def int_to_words(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: An integer word (octet) sequence that is equivalent to value
            represented by network byte order integer.
        """
        if not self.valid_int(int_val):
            raise ValueError('%r is not a valid integer value supported ' \
                'by this address type!' % int_val)
        return _struct.unpack('4B', _struct.pack('>I', int_val))

    def words_to_int(self, octets):
        """
        @param octets: A list or tuple containing integer octets.

        @return: A network byte order integer that is equivalent to value
            represented by word (octet) sequence.
        """
        if not self.valid_words(octets):
            raise ValueError('%r is not a valid octet list for an IPv4 ' \
                'address!' % octets)
        return _struct.unpack('>I', _struct.pack('4B', *octets))[0]

#-----------------------------------------------------------------------------
class IPv6Strategy(AddrStrategy):
    """
    Implements the operations that can be performed on an Internet Protocol
    version 6 network address in accordance with RFC 4291.

    NB - This class would benefit greatly from access to inet_pton/inet_ntop()
    function calls in Python's socket module. Sadly, they aren't available so
    we'll have to put up with the pure-Python implementation here (for now at
    least).
    """
    def __init__(self):
        """Constructor."""
        super(self.__class__, self).__init__(addr_type=AT_INET6,
            width=128, word_size=16, word_fmt='%x', delimiter=':')

    def valid_str(self, addr):
        """
        @param addr: An IPv6 address in string form.

        @return: C{True} if IPv6 network address string is valid, C{False}
            otherwise.
        """
        #TODO: Reduce the length of this method ...
        if not isinstance(addr, (str, unicode)):
            return False

        if '::' in addr:
            #   IPv6 compact mode.
            try:
                prefix, suffix = addr.split('::')
            except ValueError:
                return False

            l_prefix = []
            l_suffix = []

            if prefix != '':
                l_prefix = prefix.split(':')

            if suffix != '':
                l_suffix = suffix.split(':')

            #   IPv6 compact IPv4 compatibility mode.
            if len(l_suffix) and '.' in l_suffix[-1]:
                ipv4_str = l_suffix[-1]
                if ST_IPV4.valid_str(ipv4_str):
                    ipv4_int = ST_IPV4.str_to_int(ipv4_str)
                    ipv4_words = ST_IPV4.int_to_words(ipv4_int)
                    l_suffix.pop()
                    l_suffix.append(
                        ''.join(["%x" % i for i in ipv4_words[0:2]]))
                    l_suffix.append(
                        ''.join(["%x" % i for i in ipv4_words[2:]]))

            token_count = len(l_prefix) + len(l_suffix)

            if not 0 <= token_count <= self.word_count - 1:
                return False

            try:
                for token in l_prefix + l_suffix:
                    word = int(token, 16)
                    if not self.min_word <= word <= self.max_word:
                        return False
            except ValueError:
                return False
        else:
            #   IPv6 verbose mode.
            if ':' in addr:
                tokens = addr.split(':')

                if '.' in addr:
                    ipv6_prefix = tokens[:-1]
                    if ipv6_prefix[:-1] != ['0', '0', '0', '0', '0']:
                        return False
                    if ipv6_prefix[-1].lower() not in ('0', 'ffff'):
                        return False
                    #   IPv6 verbose IPv4 compatibility mode.
                    if len(tokens) != (self.word_count - 1):
                        return False
                    ipv4_str = tokens[-1]
                    if ST_IPV4.valid_str(ipv4_str):
                        ipv4_int = ST_IPV4.str_to_int(ipv4_str)
                        ipv4_words = ST_IPV4.int_to_words(ipv4_int)
                        tokens.pop()
                        tokens.append(
                            ''.join(["%x" % i for i in ipv4_words[0:2]]))
                        tokens.append(
                            ''.join(["%x" % i for i in ipv4_words[2:]]))
                else:
                    #   IPv6 verbose mode.
                    if len(tokens) != self.word_count:
                        return False
                try:
                    for token in tokens:
                        word = int(token, 16)
                        if not self.min_word <= word <= self.max_word:
                            return False
                except ValueError:
                    return False
            else:
                return False

        return True

    def str_to_int(self, addr):
        """
        @param addr: An IPv6 address in string form.

        @return: The equivalent network byte order integer for a given IPv6
            address.
        """
        if not self.valid_str(addr):
            raise ValueError("'%s' is an invalid IPv6 address!" % addr)

        values = []

        if addr == '::':
            #   Unspecified address.
            return 0
        elif '::' in addr:
            #   Abbreviated form IPv6 address.
            prefix, suffix = addr.split('::')

            if prefix == '':
                l_prefix = ['0']
            else:
                l_prefix = prefix.split(':')

            if suffix == '':
                l_suffix = ['0']
            else:
                l_suffix = suffix.split(':')

            #   Check for IPv4 compatibility address form.
            if len(l_suffix) and '.' in l_suffix[-1]:
                if len(l_suffix) > 2:
                    return False
                if len(l_suffix) == 2 and l_suffix[0].lower() != 'ffff':
                    return False

                ipv4_str = l_suffix[-1]
                if ST_IPV4.valid_str(ipv4_str):
                    ipv4_int = ST_IPV4.str_to_int(ipv4_str)
                    ipv4_words = ST_IPV4.int_to_words(ipv4_int)
                    l_suffix.pop()
                    l_suffix.append(
                        ''.join(["%x" % i for i in ipv4_words[0:2]]))
                    l_suffix.append(
                        ''.join(["%x" % i for i in ipv4_words[2:]]))

            gap_size = 8 - ( len(l_prefix) + len(l_suffix) )

            values = ["%04x" % int(i, 16) for i in l_prefix] \
                   + ['0000' for i in range(gap_size)] \
                   + ["%04x" % int(i, 16) for i in l_suffix]
        else:
            #   Verbose form IPv6 address.
            if '.' in addr:
                #   IPv4 compatiblility mode.
                tokens = addr.split(':')
                ipv4_str = tokens[-1]
                if ST_IPV4.valid_str(ipv4_str):
                    ipv4_int = ST_IPV4.str_to_int(ipv4_str)
                    ipv4_words = ST_IPV4.int_to_words(ipv4_int)
                    tokens.pop()
                    tokens.append(''.join(["%x" % i for i in ipv4_words[0:2]]))
                    tokens.append(''.join(["%x" % i for i in ipv4_words[2:]]))

                values = ["%04x" % int(i, 16) for i in tokens]
            else:
                #   non IPv4 compatiblility mode.
                values = ["%04x" % int(i, 16) for i in addr.split(':')]

        value = int(''.join(values), 16)

        return value

    def int_to_str(self, int_val, compact=True, word_fmt=None):
        """
        @param int_val: A network byte order integer.

        @param compact: (optional) A boolean flag indicating if compact
            formatting should be used. If True, this method uses the '::'
            string to represent the first adjacent group of words with a value
            of zero. Default: True

        @param word_fmt: (optional) The Python format string used to override
            formatting for each word.

        @return: The IPv6 string form equal to the network byte order integer
        value provided.
        """
        #   Use basic parent class implementation if compact string form is
        #   not required.
        if not compact:
            return super(self.__class__, self).int_to_str(int_val)

        the_word_fmt = self.word_fmt
        if word_fmt is not None:
            the_word_fmt = word_fmt

        if not self.valid_int(int_val):
            raise ValueError('%r is not a valid integer value supported ' \
                'by this address type!' % int_val)

        tokens = []
        for i in range(self.word_count):
            word = int_val & (2 ** self.word_size - 1)
            tokens += [the_word_fmt % word]
            int_val >>= self.word_size

        tokens.reverse()

        #   This can probably be optimised.
        if compact == True:
            new_tokens = []
            compact_start = False
            compact_end = False
            for token in tokens:
                if token == '0':
                    if compact_start == False and compact_end == False:
                        new_tokens += ['']
                        compact_start = True
                    elif compact_start == True and compact_end == False:
                        pass
                    else:
                        new_tokens += ['0']
                else:
                    if compact_start == True:
                        compact_end = True
                    new_tokens += [token]

            #   Post loop fixups.
            if len(new_tokens) == 1 and new_tokens[0] == '':
                new_tokens += ['', '']
            elif new_tokens[-1] == '':
                new_tokens += ['']
            elif new_tokens[0] == '':
                new_tokens.insert(0, '')

            tokens = new_tokens

        return ':'.join(tokens)

    def int_to_arpa(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: The reverse DNS lookup for an IPv6 address in network byte
            order integer form.
        """
        addr = self.int_to_str(int_val, word_fmt='%04x')
        tokens = list(addr.replace(':', ''))
        tokens.reverse()
        #   We won't support ip6.int here - see RFC 3152 for details.
        tokens = tokens + ['ip6', 'arpa', '']
        return '.'.join(tokens)

#-----------------------------------------------------------------------------
class EUI48Strategy(AddrStrategy):
    """
    Implements the operations that can be performed on an IEEE 48-bit EUI
    (Extended Unique Identifer). For all intents and purposes here, a MAC
    address.

    Supports most common MAC address formats including Cisco's string format.
    """
    def __init__(self):
        """Constructor."""
        super(self.__class__, self).__init__(addr_type=AT_LINK, width=48,
              word_size=8, word_fmt='%02x', delimiter='-', to_upper=True)

    def valid_str(self, addr):
        """
        @param addr: An EUI-48 or MAC address in string form.

        @return: C{True} if MAC address string is valid, C{False} otherwise.
        """
        if not isinstance(addr, (str, unicode)):
            return False

        try:
            if '.' in addr:
                #   Cisco style.
                words = [int("0x%s" % i, 0)  for i in addr.split('.')]
                if len(words) != 3:
                    return False
                for i in words:
                    if not (0 <= i <= 0xffff):
                        return False
            else:
                if '-' in addr:
                    #   Windows style.
                    words = [int("0x%s" % i, 0)  for i in addr.split('-')]
                elif ':' in addr:
                    #   UNIX style.
                    words = [int("0x%s" % i, 0)  for i in addr.split(':')]
                else:
                    return False
                if len(words) != 6:
                    return False
                for i in words:
                    if not (0 <= i <= 0xff):
                        return False
        except TypeError:
            return False
        except ValueError:
            return False

        return True

    def str_to_words(self, addr):
        """
        @param addr: An EUI-48 or MAC address in string form.

        Returns an integer word sequence that is equivalent in value to MAC
        address in string form.
        """
        if not self.valid_str(addr):
            raise ValueError('%r is not a recognised string representation' \
                ' of this address type!' % addr)

        if ':' in addr:
            #   UNIX style.
            words = addr.split(':')
            return tuple([ int(word, self.word_base) for word in words ])
        elif '-' in addr:
            #   Windows style.
            words = addr.split('-')
            return tuple([ int(word, self.word_base) for word in words ])
        elif '.' in addr:
            #   Cisco style.
            words = []
            for num in addr.split('.'):
                octets = []
                int_val = int(num, 16)
                for i in range(2):
                    word = int_val & 0xff
                    octets.append(int(word))
                    int_val >>= 8
                octets.reverse()
                words.extend(octets)
            return tuple(words)

    def int_to_str(self, int_val, delimiter=None, word_fmt=None,
                   to_upper=True):
        """
        @param int_val: A network byte order integer.

        @param delimiter: (optional) A delimiter string override to be used
            instead of the default between words in string value returned.

        @param word_fmt: (optional) A Python format string override used to
            format each word of address instead of the default.

        @return: A MAC address in string form that is equivalent to value
        represented by a network byte order integer.
        """
        the_delimiter = self.delimiter
        if delimiter is not None:
            the_delimiter = delimiter

        the_word_fmt = self.word_fmt
        if word_fmt is not None:
            the_word_fmt = word_fmt

        the_to_upper = self.to_upper
        if to_upper is not True:
            the_to_upper = to_upper

        words = self.int_to_words(int_val)
        tokens = [the_word_fmt % i for i in words]
        addr = the_delimiter.join(tokens)

        if the_to_upper is True:
            return addr.upper()

        return addr

#-----------------------------------------------------------------------------
#   Shared strategy objects for supported address types.
#-----------------------------------------------------------------------------

#: A shared strategy object supporting all operations on IPv4 addresses.
ST_IPV4 = None
#   Use the right strategy class dependent upon Python implementation (work-
#   around for various Python bugs).
if USE_IPV4_OPT is True:
    ST_IPV4 = IPv4StrategyOpt()
else:
    ST_IPV4 = IPv4StrategyStd()

#: A shared strategy object supporting all operations on IPv6 addresses.
ST_IPV6  = IPv6Strategy()
#: A shared strategy object supporting all operations on EUI-48/MAC addresses.
ST_EUI48 = EUI48Strategy()

#: A shared strategy object supporting all operations on EUI-64 addresses.
ST_EUI64 = AddrStrategy(addr_type=AT_EUI64, width=64, word_size=8,
                         word_fmt='%02x', delimiter='-', to_upper=True)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    pass

