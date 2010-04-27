#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
IPv4 address logic.
"""
import struct as _struct
import platform as _platform

OPT_IMPORTS = False

#   Check whether we need to use fallback code or not.
try:
    import socket as _socket
    #   Check for a common bug on Windows and socket modules on some other
    #   platforms.
    _socket.inet_aton('255.255.255.255')
    from _socket import inet_aton as _inet_aton, \
                        inet_ntoa as _inet_ntoa, \
                        AF_INET
    OPT_IMPORTS = True
except:
    from netaddr.fbsocket import inet_aton as _inet_aton, \
                                 inet_ntoa as _inet_ntoa, \
                                 AF_INET

from netaddr.core import AddrFormatError
from netaddr.strategy import valid_words  as _valid_words, \
    valid_bits   as _valid_bits, \
    bits_to_int  as _bits_to_int, \
    int_to_bits  as _int_to_bits, \
    valid_bin    as _valid_bin, \
    int_to_bin   as _int_to_bin, \
    bin_to_int   as _bin_to_int

#: The width (in bits) of this address type.
width = 32

#: The individual word size (in bits) of this address type.
word_size = 8

#: The format string to be used when converting words to string values.
word_fmt = '%d'

#: The separator character used between each word.
word_sep = '.'

#: The AF_* constant value of this address type.
family = AF_INET

#: A friendly string name address type.
family_name = 'IPv4'

#: The version of this address type.
version = 4

#: The number base to be used when interpreting word values as integers.
word_base = 10

#: The maximum integer value that can be represented by this address type.
max_int = 2 ** width - 1

#: The number of words in this address type.
num_words = width / word_size

#: The maximum integer value for an individual word in this address type.
max_word = 2 ** word_size - 1

#-----------------------------------------------------------------------------
def valid_str(addr):
    """
    @param addr: An IPv4 address in presentation (string) format.

    @return: C{True} if IPv4 address is valid, C{False} otherwise.
    """
    if addr == '':
        raise AddrFormatError('Empty strings are not supported!')

    try:
        _inet_aton(addr)
    except:
        return False
    return True

#-----------------------------------------------------------------------------
def str_to_int(addr):
    """
    @param addr: An IPv4 dotted decimal address in string form.

    @return: The equivalent unsigned integer for a given IPv4 address.
    """
    if addr == '':
        raise AddrFormatError('Empty strings are not supported!')
    try:
        return _struct.unpack('>I', _inet_aton(addr))[0]
    except:
        #   Windows platform workaround.
        if hasattr(addr, 'lower') and _platform.system() == 'Windows':
            if addr.lower() == '0xffffffff':
                return 0xffffffff

        raise AddrFormatError('%r is not a valid IPv4 address string!' \
            % addr)

#-----------------------------------------------------------------------------
def int_to_str(int_val, dialect=None):
    """
    @param int_val: An unsigned integer.

    @param dialect: (unused) Any value passed in is ignored.

    @return: The IPv4 presentation (string) format address equivalent to the
        unsigned integer provided.
    """
    if 0 <= int_val <= max_int:
        return _inet_ntoa(_struct.pack('>I', int_val))
    else:
        raise ValueError('%r is not a valid 32-bit unsigned integer!' \
            % int_val)

#-----------------------------------------------------------------------------
def int_to_arpa(int_val):
    """
    @param int_val: An unsigned integer.

    @return: The reverse DNS lookup for an IPv4 address in network byte
        order integer form.
    """
    words = ["%d" % i for i in int_to_words(int_val)]
    words.reverse()
    words.extend(['in-addr', 'arpa', ''])
    return '.'.join(words)

#-----------------------------------------------------------------------------
def int_to_packed(int_val):
    """
    @param int_val: the integer to be packed.

    @return: a packed string that is equivalent to value represented by an
    unsigned integer.
    """
    return _struct.pack('>I', int_val)

#-----------------------------------------------------------------------------
def packed_to_int(packed_int):
    """
    @param packed_int: a packed string containing an unsigned integer.
        It is assumed that string is packed in network byte order.

    @return: An unsigned integer equivalent to value of network address
        represented by packed binary string.
    """
    return _struct.unpack('>I', packed_int)[0]

#-----------------------------------------------------------------------------
def valid_words(words):
    return _valid_words(words, word_size, num_words)

#-----------------------------------------------------------------------------
def int_to_words(int_val):
    """
    @param int_val: An unsigned integer.

    @return: An integer word (octet) sequence that is equivalent to value
        represented by an unsigned integer.
    """
    if not 0 <= int_val <= max_int:
        raise ValueError('%r is not a valid integer value supported ' \
            'by this address type!' % int_val)
    return ( (int_val >> 24),
             (int_val >> 16 & 255),
             (int_val >> 8 & 255),
             (int_val & 255) )

#-----------------------------------------------------------------------------
def words_to_int(words):
    """
    @param words: A list or tuple containing integer octets.

    @return: An unsigned integer that is equivalent to value represented
        by word (octet) sequence.
    """
    if not valid_words(words):
        raise ValueError('%r is not a valid octet list for an IPv4 ' \
            'address!' % words)
    return _struct.unpack('>I', _struct.pack('4B', *words))[0]

#-----------------------------------------------------------------------------
def valid_bits(bits):
    return _valid_bits(bits, width, word_sep)

#-----------------------------------------------------------------------------
def bits_to_int(bits):
    return _bits_to_int(bits, width, word_sep)

#-----------------------------------------------------------------------------
def int_to_bits(int_val, word_sep=None):
    if word_sep is None:
        word_sep = globals()['word_sep']
    return _int_to_bits(int_val, word_size, num_words, word_sep)

#-----------------------------------------------------------------------------
def valid_bin(bin_val):
    return _valid_bin(bin_val, width)

#-----------------------------------------------------------------------------
def int_to_bin(int_val):
    return _int_to_bin(int_val, width)

#-----------------------------------------------------------------------------
def bin_to_int(bin_val):
    return _bin_to_int(bin_val, width)
