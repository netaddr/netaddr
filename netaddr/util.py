#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""utility functions"""

def num_bits(n):
    """Minimum number of bits needed to represent a given unsigned integer."""
    n = abs(n)
    numbits = 0
    while n:
         numbits += 1
         n >>= 1
    return numbits

#-----------------------------------------------------------------------------
def bytes_to_bits():
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

BYTES_TO_BITS = bytes_to_bits()

