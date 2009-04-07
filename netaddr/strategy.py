#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network address conversion logic, constants and shared strategy objects.
"""
import struct as _struct
import re as _re
from netaddr.util import BYTES_TO_BITS as _BYTES_TO_BITS

#   Check whether we need to use fallback code or not.
try:
    import socket as _socket
    #   Check for a common bug on Windows and some other socket modules.
    _socket.inet_aton('255.255.255.255')
    from socket import inet_aton as _inet_aton, \
                       inet_ntoa as _inet_ntoa, \
                       AF_INET as _AF_INET
except:
    from netaddr.fallback import inet_aton as _inet_aton, \
                                 inet_ntoa as _inet_ntoa, \
                                 AF_INET as _AF_INET
try:
    import socket as _socket
    #   These might all generate exceptions on different platforms.
    _socket.inet_pton
    _socket.AF_INET6
    from socket import inet_pton as _inet_pton, \
                       inet_ntop as _inet_ntop, \
                       AF_INET6 as _AF_INET6
except:
    from netaddr.fallback import inet_pton as _inet_pton, \
                                 inet_ntop as _inet_ntop, \
                                 AF_INET6 as _AF_INET6

from netaddr import BIG_ENDIAN_PLATFORM, AT_UNSPEC, AT_INET, AT_INET6, \
                    AT_LINK, AT_EUI64, AT_NAMES, AddrFormatError

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
                 addr_type=AT_UNSPEC, word_base=16):
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

        try:
            self.name = AT_NAMES[addr_type]
        except KeyError:
            self.name = AT_NAMES[AT_UNSPEC]

    def __repr__(self):
        """@return: executable Python string to recreate equivalent object"""
        return "%s(%r, %r, %r, %r, %r, %r)" %  (self.__class__.__name__,
            self.width, self.word_size, self.word_sep, self.addr_type,
            self.word_base)

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

        @return: An unsigned integer that is equivalent to value represented
            by network address in readable binary form.
        """
        if not self.valid_bits(bits):
            raise ValueError('%r is not a valid binary form string for ' \
                'address type!' % bits)

        return int(bits.replace(self.word_sep, ''), 2)

    #-------------------------------------------------------------------------
    #   Integer methods.
    #-------------------------------------------------------------------------

    def valid_int(self, int_val):
        """
        @param int_val: An unsigned integer.

        @return: C{True} if integer falls within the boundaries of this
            address type, C{False} otherwise.
        """
        if not isinstance(int_val, (int, long)):
            return False

        return 0 <= int_val <= self.max_int

    def int_to_str(self, int_val):
        """
        @param int_val: An unsigned integer.

        @return: A network address in string form that is equivalent to value
            represented by an unsigned integer.
        """
        words = self.int_to_words(int_val)
        tokens = [self.word_fmt % i for i in words]
        addr = self.word_sep.join(tokens)

        return addr

    def int_to_bits(self, int_val, word_sep=None):
        """
        @param int_val: An unsigned integer.

        @param word_sep: (optional) the separator to insert between words.
            Default: None - use default separator for address type.

        @return: A network address in readable binary form that is equivalent
            to value represented by an unsigned integer.
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

        if word_sep is not None:
            #   Custom separator.
            if not hasattr(word_sep, 'join'):
                raise ValueError('Word separator must be a string!')
            return word_sep.join(bit_words)

        #   Default separator.
        return self.word_sep.join(bit_words)

    def int_to_bin(self, int_val):
        """
        @param int_val: An unsigned integer.

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
        @param int_val: An unsigned integer to be divided up into words.

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

        return tuple(reversed(words))

    def int_to_packed(self, int_val):
        """
        @param int_val: the integer to be packed.

        @return: a packed string that is equivalent to value represented by an
        unsigned integer.
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
            It is assumed that the string is packed in network byte order.

        @return: An unsigned integer equivalent to value of network address
            represented by packed binary string.
        """
        try:
            fmt = '>%d%s' % (self.num_words, AddrStrategy.STRUCT_FORMATS[
                self.word_size])
        except KeyError:
            raise ValueError('unsupported word size: %d!' % self.word_size)

        words = list(_struct.unpack(fmt, packed_int))

        int_val = 0
        for i, num in enumerate(reversed(words)):
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

        @return: An unsigned integer equivalent to value represented by network
            address in string form.
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

        @return: An unsigned integer that is equivalent to value represented
            by word sequence.
        """
        if not self.valid_words(words):
            raise ValueError('%r is not a valid word list!' % words)

        int_val = 0
        for i, num in enumerate(reversed(words)):
            word = num
            word = word << self.word_size * i
            int_val = int_val | word

        return int_val

#-----------------------------------------------------------------------------
class IPv4Strategy(AddrStrategy):
    """An L{AddrStrategy} for IPv4 address processing."""
    def __init__(self):
        """Constructor."""
        super(IPv4Strategy, self).__init__(width=32, word_size=8,
              word_fmt='%d', word_sep='.', addr_type=AT_INET, word_base=10)

    def valid_str(self, addr):
        """
        @param addr: An IP address in presentation (string) format.

        @return: C{True} if network address in string form is valid for this
            address type, C{False} otherwise.
        """
        if addr == '':
            raise AddrFormatError('Empty strings are not supported!')

        try:
            _inet_aton(addr)
        except:
            return False
        return True

    def str_to_int(self, addr):
        """
        @param addr: An IPv4 dotted decimal address in string form.

        @return: An unsigned integer that is equivalent to value represented
            by the IPv4 dotted decimal address string.
        """
        if addr == '':
            raise AddrFormatError('Empty strings are not supported!')
        try:
            return _struct.unpack('>I', _inet_aton(addr))[0]
        except:
            raise AddrFormatError('%r is not a valid IPv4 address string!' \
                % addr)

    def int_to_str(self, int_val):
        """
        @param int_val: An unsigned integer.

        @return: An IPv4 dotted decimal address string that is equivalent to
            value represented by a 32 bit unsigned integer.
        """
        if self.valid_int(int_val):
            return _inet_ntoa(_struct.pack('>I', int_val))
        else:
            raise ValueError('%r is not a valid 32-bit unsigned integer!' \
                % int_val)

    def int_to_words(self, int_val, num_words=None, word_size=None):
        """
        @param int_val: An unsigned integer.

        @param num_words: (unused) *** interface compatibility only ***

        @param word_size: (unused) *** interface compatibility only ***

        @return: An integer word (octet) sequence that is equivalent to value
            represented by an unsigned integer.
        """
        if not self.valid_int(int_val):
            raise ValueError('%r is not a valid integer value supported ' \
                'by this address type!' % int_val)
        return _struct.unpack('4B', _struct.pack('>I', int_val))

    def words_to_int(self, octets):
        """
        @param octets: A list or tuple containing integer octets.

        @return: An unsigned integer that is equivalent to value represented
            by word (octet) sequence.
        """
        if not self.valid_words(octets):
            raise ValueError('%r is not a valid octet list for an IPv4 ' \
                'address!' % octets)
        return _struct.unpack('>I', _struct.pack('4B', *octets))[0]

    def int_to_arpa(self, int_val):
        """
        @param int_val: An unsigned integer.

        @return: The reverse DNS lookup for an IPv4 address in network byte
            order integer form.
        """
        words = ["%d" % i for i in self.int_to_words(int_val)]
        words.reverse()
        words.extend(['in-addr', 'arpa', ''])
        return '.'.join(words)

#-----------------------------------------------------------------------------
class IPv6Strategy(AddrStrategy):
    """
    An L{AddrStrategy} for IPv6 address processing.

    Implements the operations that can be performed on an IPv6 network address
    in accordance with RFC 4291.
    """
    def __init__(self):
        """Constructor."""
        super(IPv6Strategy, self).__init__(addr_type=AT_INET6,
            width=128, word_size=16, word_fmt='%x', word_sep=':')

    def valid_str(self, addr):
        """
        @param addr: An IPv6 address in string form.

        @return: C{True} if IPv6 network address string is valid, C{False}
            otherwise.
        """
        if addr == '':
            raise AddrFormatError('Empty strings are not supported!')

        try:
            _inet_pton(_AF_INET6, addr)
        except _socket.error:
            return False
        except TypeError:
            return False
        except ValueError:
            return False
        return True

    def str_to_int(self, addr):
        """
        @param addr: An IPv6 address in string form.

        @return: The equivalent unsigned integer for a given IPv6 address.
        """
        if addr == '':
            raise AddrFormatError('Empty strings are not supported!')
        try:
            packed_int = _inet_pton(_AF_INET6, addr)
            return self.packed_to_int(packed_int)
        except Exception, e:
            raise AddrFormatError('%r is not a valid IPv6 address string!' \
                % addr)

    def int_to_str(self, int_val, compact=True, word_fmt=None):
        """
        @param int_val: An unsigned integer.

        @param compact: (optional) A boolean flag indicating if compact
            formatting should be used. If True, this method uses the '::'
            string to represent the first adjacent group of words with a value
            of zero. Default: True

        @param word_fmt: (optional) The Python format string used to override
            formatting for each word. Only applies when compact is False.

        @return: The IPv6 string form equal to the unsigned integer provided.
        """
        try:
            packed_int = self.int_to_packed(int_val)
            if compact:
                #   Default return value.
                return _inet_ntop(_AF_INET6, packed_int)
            else:
                #   Custom return value.
                if word_fmt is None:
                    word_fmt = self.word_fmt
                words = list(_struct.unpack('>8H', packed_int))
                tokens = [word_fmt % word for word in words]
                return self.word_sep.join(tokens)
        except Exception, e:
            raise ValueError('%r is not a valid 128-bit unsigned integer!' \
                % int_val)

    def int_to_packed(self, int_val):
        """
        @param int_val: the integer to be packed.

        @return: a packed string that is equivalent to value represented by an
        unsigned integer (in network byte order).
        """
        #   Here we've over-ridden the normal values to get the fastest
        #   possible conversion speeds. Still quite slow versus IPv4 speed ups.
        num_words = 4
        word_size = 32

        words = self.int_to_words(int_val, num_words, word_size)

        try:
            fmt = '>%d%s'% (num_words, AddrStrategy.STRUCT_FORMATS[word_size])
        except KeyError:
            raise ValueError('unsupported word size: %d!' % word_size)

        return _struct.pack(fmt, *words)

    def packed_to_int(self, packed_int):
        """
        @param packed_int: a packed string containing an unsigned integer.
            It is assumed that string is packed in network byte order.

        @return: An unsigned integer that is equivalent to value of network
            address represented by packed binary string.
        """
        #   Here we've over-ridden the normal values to get the fastest
        #   conversion speeds. Still quite slow versus IPv4 speed ups.
        num_words = 4
        word_size = 32

        try:
            fmt = '>%d%s'% (num_words, AddrStrategy.STRUCT_FORMATS[word_size])
        except KeyError:
            raise ValueError('unsupported word size: %d!' % word_size)

        words = list(_struct.unpack(fmt, packed_int))

        int_val = 0
        for i, num in enumerate(reversed(words)):
            word = num
            word = word << word_size * i
            int_val = int_val | word

        return int_val

    def int_to_arpa(self, int_val):
        """
        @param int_val: An unsigned integer.

        @return: The reverse DNS lookup for an IPv6 address in network byte
            order integer form.
        """
        addr = self.int_to_str(int_val, compact=False, word_fmt='%.4x')
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

    def __init__(self, word_fmt='%.2X', word_sep='-'):
        """
        Constructor.

        @param word_sep: separator between each word.
            (Default: '-')

        @param word_fmt: format string for each hextet.
            (Default: '%02x')
        """
        super(self.__class__, self).__init__(addr_type=AT_LINK, width=48,
              word_size=8, word_fmt=word_fmt, word_sep=word_sep)


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
        self.word_fmt  = '%.2X'
        self.word_base = 16
        self.addr_type = AT_LINK

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

        @return: An unsigned integer that is equivalent to value represented
            by EUI-48/MAC string address.
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
            int_val = int(''.join(['%.2x' % int(w, 16) for w in words]), 16)
        elif len(words) == 3:
            #   4 bytes x 3 (Cisco)
            int_val = int(''.join(['%.4x' % int(w, 16) for w in words]), 16)
        elif len(words) == 2:
            #   6 bytes x 2 (PostgreSQL)
            int_val = int(''.join(['%.6x' % int(w, 16) for w in words]), 16)
        elif len(words) == 1:
            #   12 bytes (bare, no delimiters)
            int_val = int('%012x' % int(words[0], 16), 16)
        else:
            raise AddrFormatError('unexpected word count in MAC address %r!' \
                % addr)

        return int_val

    def int_to_str(self, int_val, word_sep=None, word_fmt=None):
        """
        @param int_val: An unsigned integer.

        @param word_sep: (optional) The separator used between words in an
            address string.

        @param word_fmt: (optional) A Python format string used to format
            each word of address.

        @return: A MAC address in string form that is equivalent to value
            represented by an unsigned integer.
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

        return addr

#-----------------------------------------------------------------------------
#   Shared strategy objects for supported address types.
#-----------------------------------------------------------------------------

#: A shared strategy object supporting all operations on IPv4 addresses.
ST_IPV4 = IPv4Strategy()

#: A shared strategy object supporting all operations on IPv6 addresses.
ST_IPV6 = IPv6Strategy()

#: A shared strategy object supporting all operations on EUI-48/MAC addresses.
ST_EUI48 = EUI48Strategy()

#: A shared strategy object supporting all operations on EUI-64 addresses.
ST_EUI64 = AddrStrategy(addr_type=AT_EUI64, width=64, word_size=8, \
                         word_fmt='%.2X', word_sep='-')

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    pass

