#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network address conversion logic, constants and shared strategy objects.
"""
import socket as _socket
import struct as _struct
import re as _re

USE_IPV4_OPT=True   #: Use optimised IPv4 strategy? Default: True

try:
    #   Detects a common bug in various Python implementations.
    _socket.inet_aton('255.255.255.255')
except:
    USE_IPV4_OPT=False

from netaddr import BIG_ENDIAN_PLATFORM, AT_UNSPEC, AT_INET, AT_INET6, \
                    AT_LINK, AT_EUI64, AT_NAMES, AddrFormatError

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
    """Basic support for common operations performed on each address type"""

    #: Lookup table for struct module format strings.
    STRUCT_FORMATS = {
         8 : 'B',   # unsigned char
        16 : 'H',   # unsigned short
        32 : 'I',   # unsigned int
    }

    def __init__(self, width, word_size, word_sep, word_fmt='%x',
                 addr_type=AT_UNSPEC, word_base=16, uppercase=False):
        """
        Constructor.

        @param width: size of address in bits.
            (e.g. 32 - IPv4, 48 - MAC, 128 - IPv6)

        @param word_size: size of each word.
            (e.g. 8 - octets, 16 - hextets)

        @param word_sep: separator between each word.
            (e.g. '.' - IPv4, ':' - IPv6, '-' - EUI-48)

        @param word_fmt: format string for each word.
            (Default: '%x')

        @param addr_type: address type.
            (Default: AT_UNSPEC)

        @param word_base: number base used to convert each word using int().
            (Default: 16)

        @param uppercase: uppercase address.
            (Default: False)
        """

        self.width = width
        self.max_int = 2 ** width - 1
        self.word_size = word_size
        self.num_words = width / word_size
        self.max_word = 2 ** word_size - 1
        self.word_sep = word_sep
        self.word_fmt  = word_fmt
        self.word_base = word_base
        self.addr_type = addr_type
        self.uppercase = uppercase

        try:
            self.name = AT_NAMES[addr_type]
        except KeyError:
            self.name = AT_NAMES[AT_UNSPEC]

    def __repr__(self):
        """@return: executable Python string to recreate equivalent object"""
        return "%s(%r, %r, %r, %r, %r, %r)" %  (self.__class__.__name__,
            self.width, self.word_size, self.word_sep, self.addr_type,
            self.word_base, self.uppercase)

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

        bits = bits.replace(self.word_sep, '')

        if len(bits) != self.width:
            return False

        try:
            if 0 <= int(bits, 2) <= self.max_int:
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
        if not self.valid_bits(bits):
            raise ValueError('%r is not a valid binary form string for ' \
                'address type!' % bits)

        word_bits = bits.split(self.word_sep)
        if len(word_bits) != self.num_words:
            raise ValueError('invalid number of words within binary form ' \
                'string for address type!' % bits)

        words = tuple([int(i, 2) for i in word_bits])

        return self.words_to_int(words)

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

        return 0 <= int_val <= self.max_int

    def int_to_str(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: A network address in string form that is equivalent to value
            represented by a network byte order integer.
        """
        words = self.int_to_words(int_val)
        tokens = [self.word_fmt % i for i in words]
        addr = self.word_sep.join(tokens)

        if self.uppercase is True:
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
            bits = []
            while word:
                bits.append(_BYTES_TO_BITS[word&255])
                word >>= 8
            bits.reverse()
            bit_str = ''.join(bits) or '0'*self.word_size
            bits = ('0'*self.word_size+bit_str)[-self.word_size:]
            bit_words.append(bits)

        return self.word_sep.join(bit_words)

    def int_to_bin(self, int_val):
        """
        @param int_val: A network byte order integer.

        @return: A network address in standard binary representation format
            that is equivalent to integer address value. Essentially a back
            port of the bin() builtin in Python 2.6.x and higher.
        """
        bit_words = []

        for word in self.int_to_words(int_val):
            bits = []
            while word:
                bits.append(_BYTES_TO_BITS[word&255])
                word >>= 8
            bits.reverse()
            bit_str = ''.join(bits) or '0'*self.word_size
            bits = ('0'*self.word_size+bit_str)[-self.word_size:]
            bit_words.append(bits)

        return '0b' + ''.join(bit_words)

    def int_to_words(self, int_val, num_words=None, word_size=None):
        """
        @param int_val: A network byte order integer to be split.

        @param num_words: (optional) number of words expected in return value
            tuple. Uses address type default if not specified.

        @param word_size: (optional) size/width of individual words (in bits).
             Uses address type default if not specified.
        """
        if not self.valid_int(int_val):
            raise IndexError('integer %r is out of bounds!' % hex(int_val))

        #   Set defaults for optional args.
        if num_words is None:
            num_words = self.num_words
        if word_size is None:
            word_size = self.word_size

        max_word_size = 2 ** word_size - 1

        words = []
        for _ in range(num_words):
            word = int_val & max_word_size
            words.append(int(word))
            int_val >>= word_size
        words.reverse()

        return tuple(words)

    def int_to_packed(self, int_val):
        """
        @param int_val: the integer to be packed.

        @return: a packed string that is equivalent to value represented by a
        network byte order integer.
        """

        words = self.int_to_words(int_val, self.num_words, self.word_size)

        try:
            fmt = '>%d%s' % (self.num_words, AddrStrategy.STRUCT_FORMATS[
                self.word_size])
        except KeyError:
            raise ValueError('unsupported word size: %d!' % self.word_size)

        return _struct.pack(fmt, *words)


    #-------------------------------------------------------------------------
    #   Packed string methods.
    #-------------------------------------------------------------------------

    def packed_to_int(self, packed_int):
        """
        @param packed_int: a packed string containing an unsigned integer.
            Network byte order is assumed.

        @return: A network byte order integer that is equivalent to value
            of network address represented by packed binary string.
        """
        try:
            fmt = '>%d%s' % (self.num_words, AddrStrategy.STRUCT_FORMATS[
                self.word_size])
        except KeyError:
            raise ValueError('unsupported word size: %d!' % self.word_size)

        words = list(_struct.unpack(fmt, packed_int))
        words.reverse()

        int_val = 0
        for i, num in enumerate(words):
            word = num
            word = word << self.word_size * i
            int_val = int_val | word

        return int_val

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

        tokens = addr.split(self.word_sep)
        if len(tokens) != self.num_words:
            return False

        try:
            for token in tokens:
                if not 0 <= int(token, self.word_base) <= \
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
        if not self.valid_str(addr):
            raise ValueError('%r is not a recognised string representation' \
                ' of this address type!' % addr)

        tokens = addr.split(self.word_sep)
        words = [ int(token, self.word_base) for token in tokens ]

        return self.words_to_int(words)

    #-------------------------------------------------------------------------
    #   Word list methods.
    #-------------------------------------------------------------------------

    def valid_words(self, words):
        """
        @param words: A sequence containing integer word values.

        @return: C{True} if word sequence is valid for this address type,
            C{False} otherwise.
        """
        if not hasattr(words, '__iter__'):
            return False

        if len(words) != self.num_words:
            return False

        for i in words:
            if not isinstance(i, (int, long)):
                return False

            if not 0 <= i <= self.max_word:
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
              word_fmt='%d', word_sep='.', addr_type=AT_INET, word_base=10)

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

    def valid_str(self, addr):
        """
        @param addr: An IP address in presentation (string) format.

        @return: C{True} if network address in string form is valid for this
            address type, C{False} otherwise.
        """
        try:
            #   This call handles a lot of older IPv4 address formats that
            #   it would be a lot of work to implement (many edge cases).
            #   Please Note: only this optimised strategy class will have
            #   the ability to parse these less common formats for the
            #   moment.
            _socket.inet_aton(addr)
        except _socket.error:
            return False
        except TypeError:
            return False
        return True

    def str_to_int(self, addr):
        """
        @param addr: An IPv4 dotted decimal address in string form.

        @return: A network byte order integer that is equivalent to value
            represented by the IPv4 dotted decimal address string.
        """
        if not self.valid_str(addr):
            raise ValueError('%r is not a valid IPv4 address string!' \
                % addr)
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

    def int_to_words(self, int_val, num_words=None, word_size=None):
        """
        @param int_val: A network byte order integer.

        @param num_words: (unused) *** interface compatibility only ***

        @param word_size: (unused) *** interface compatibility only ***

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
            width=128, word_size=16, word_fmt='%x', word_sep=':')

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
                        ''.join(["%.2x" % i for i in ipv4_words[0:2]]))
                    l_suffix.append(
                        ''.join(["%.2x" % i for i in ipv4_words[2:4]]))

            token_count = len(l_prefix) + len(l_suffix)

            if not 0 <= token_count <= self.num_words - 1:
                return False

            try:
                for token in l_prefix + l_suffix:
                    word = int(token, 16)
                    if not 0 <= word <= self.max_word:
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
                    if len(tokens) != (self.num_words - 1):
                        return False
                    ipv4_str = tokens[-1]
                    if ST_IPV4.valid_str(ipv4_str):
                        ipv4_int = ST_IPV4.str_to_int(ipv4_str)
                        ipv4_words = ST_IPV4.int_to_words(ipv4_int)
                        tokens.pop()
                        tokens.append(
                            ''.join(["%.2x" % i for i in ipv4_words[0:2]]))
                        tokens.append(
                            ''.join(["%.2x" % i for i in ipv4_words[2:4]]))
                else:
                    #   IPv6 verbose mode.
                    if len(tokens) != self.num_words:
                        return False
                try:
                    for token in tokens:
                        word = int(token, 16)
                        if not 0 <= word <= self.max_word:
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
                        ''.join(["%.2x" % i for i in ipv4_words[0:2]]))
                    l_suffix.append(
                        ''.join(["%.2x" % i for i in ipv4_words[2:4]]))

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
                    tokens.append(''.join(["%.2x" % i for i in ipv4_words[0:2]]))
                    tokens.append(''.join(["%.2x" % i for i in ipv4_words[2:4]]))

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

        _word_fmt = self.word_fmt
        if word_fmt is not None:
            _word_fmt = word_fmt

        if not self.valid_int(int_val):
            raise ValueError('%r is not a valid integer value supported ' \
                'by this address type!' % int_val)

        tokens = []
        for i in range(self.num_words):
            word = int_val & (2 ** self.word_size - 1)
            tokens += [_word_fmt % word]
            int_val >>= self.word_size

        tokens.reverse()

        if compact == True:
            new_tokens = []

            positions = []
            within_run = False
            start_index = None
            num_tokens = 0

            #   Discover all runs of zeros.
            for idx, token in enumerate(tokens):
                if token == '0':
                    within_run = True
                    if start_index is None:
                        start_index = idx
                    num_tokens += 1
                else:
                    if num_tokens > 1:
                        positions.append((num_tokens, start_index))
                    within_run = False
                    start_index = None
                    num_tokens = 0

                new_tokens.append(token)

            #   Store any position not saved before loop exit.
            if num_tokens > 1:
                positions.append((num_tokens, start_index))

            #   Replace first longest run with an empty string.
            if len(positions) != 0:
                #   Locate longest, left-most run of zeros.
                positions.sort(lambda x, y: cmp(x[1], y[1]))
                best_position = positions[0]
                for position in positions:
                    if position[0] > best_position[0]:
                        best_position = position
                #   Replace chosen zero run.
                (length, start_idx) = best_position
                new_tokens = new_tokens[0:start_idx] + [''] + \
                             new_tokens[start_idx+length:]

                #   Add start and end blanks so join creates '::'.
                if new_tokens[0] == '':
                    new_tokens.insert(0, '')

                if new_tokens[-1] == '':
                    new_tokens.append('')

            tokens = new_tokens

        return self.word_sep.join(tokens)

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
    (Extended Unique Identifer) a.k.a. a MAC (Media Access Control) layer 2
    address.

    Supports all common (and some less common MAC string formats including
    Cisco's 'triple hextet' format and also bare MACs that contain no
    delimiters.
    """
    #   Regular expression to match the numerous different MAC formats.
    RE_MAC_FORMATS = (
        #   2 bytes x 6 (UNIX, Windows, EUI-48)
        '^' + ':'.join(['([0-9A-F]{1,2})'] * 6) + '$',
        '^' + '-'.join(['([0-9A-F]{1,2})'] * 6) + '$',

        #   4 bytes x 3 (Cisco)
        '^' + ':'.join(['([0-9A-F]{1,4})'] * 3) + '$',
        '^' + '-'.join(['([0-9A-F]{1,4})'] * 3) + '$',

        #   6 bytes x 2 (PostgreSQL)
        '^' + '-'.join(['([0-9A-F]{5,6})'] * 2) + '$',
        '^' + ':'.join(['([0-9A-F]{5,6})'] * 2) + '$',

        #   12 bytes (bare, no delimiters)
        '^(' + ''.join(['[0-9A-F]'] * 12) + ')$',
        '^(' + ''.join(['[0-9A-F]'] * 11) + ')$',
    )
    #   For efficiency, replace each string regexp with its compiled
    #   equivalent.
    RE_MAC_FORMATS = [_re.compile(_, _re.IGNORECASE) for _ in RE_MAC_FORMATS]

    def __init__(self, word_fmt='%02x', word_sep='-', uppercase=True):
        """
        Constructor.

        @param word_sep: separator between each word.
            (Default: '-')

        @param word_fmt: format string for each hextet.
            (Default: '%02x')

        @param uppercase: return uppercase MAC/EUI-48 addresses.
            (Default: True)
        """
        super(self.__class__, self).__init__(addr_type=AT_LINK, width=48,
              word_size=8, word_fmt=word_fmt, word_sep=word_sep,
              uppercase=uppercase)

    def reset(self):
        """
        Resets the internal state of this strategy to safe default values.
        """
        #   These are the settings for EUI-48 specific formatting.
        self.width = 48
        self.max_int = 2 ** self.width - 1
        self.word_size = 8
        self.num_words = self.width / self.word_size
        self.max_word = 2 ** self.word_size - 1
        self.word_sep = '-'
        self.word_fmt  = '%02x'
        self.word_base = 16
        self.addr_type = AT_LINK
        self.uppercase = True

    def valid_str(self, addr):
        """
        @param addr: An EUI-48 or MAC address in string form.

        @return: C{True} if MAC address string is valid, C{False} otherwise.
        """
        if not isinstance(addr, (str, unicode)):
            return False

        for regexp in EUI48Strategy.RE_MAC_FORMATS:
            match_result = regexp.findall(addr)
            if len(match_result) != 0:
                return True
        return False

    def str_to_int(self, addr):
        """
        @param addr: An EUI-48 or MAC address in string form.

        @return: A network byte order integer that is equivalent to value
            represented by EUI-48/MAC string address.
        """
        words = []
        if isinstance(addr, (str, unicode)):
            found_match = False
            for regexp in EUI48Strategy.RE_MAC_FORMATS:
                match_result = regexp.findall(addr)
                if len(match_result) != 0:
                    found_match = True
                    if isinstance(match_result[0], tuple):
                        words = match_result[0]
                    else:
                        words = (match_result[0],)
                    break
            if not found_match:
                raise AddrFormatError('%r is not a supported MAC format!' \
                    % addr)
        else:
            raise TypeError('%r is not str() or unicode()!' % addr)

        int_val = None

        if len(words) == 6:
            #   2 bytes x 6 (UNIX, Windows, EUI-48)
            int_val = int(''.join(['%02x' % int(w, 16) for w in words]), 16)
        elif len(words) == 3:
            #   4 bytes x 3 (Cisco)
            int_val = int(''.join(['%04x' % int(w, 16) for w in words]), 16)
        elif len(words) == 2:
            #   6 bytes x 2 (PostgreSQL)
            int_val = int(''.join(['%06x' % int(w, 16) for w in words]), 16)
        elif len(words) == 1:
            #   12 bytes (bare, no delimiters)
            int_val = int('%012x' % int(words[0], 16), 16)
        else:
            raise AddrFormatError('unexpected word count in MAC address %r!' \
                % addr)

        return int_val

    def int_to_str(self, int_val, word_sep=None, word_fmt=None):
        """
        @param int_val: A network byte order integer.

        @param word_sep: (optional) The separator used between words in an
            address string.

        @param word_fmt: (optional) A Python format string used to format
            each word of address.

        @return: A MAC address in string form that is equivalent to value
            represented by a network byte order integer.
        """
        _word_sep = self.word_sep
        if word_sep is not None:
            _word_sep = word_sep

        _word_fmt = self.word_fmt
        if word_fmt is not None:
            _word_fmt = word_fmt

        words = self.int_to_words(int_val)
        tokens = [_word_fmt % i for i in words]
        addr = _word_sep.join(tokens)

        if self.uppercase:
            return addr.upper()
        else:
            return addr.lower()

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
ST_EUI64 = AddrStrategy(addr_type=AT_EUI64, width=64, word_size=8, \
                         word_fmt='%02x', word_sep='-', uppercase=True)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    pass

