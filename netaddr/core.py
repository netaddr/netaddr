#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""common code shared between various modules"""

import sys as _sys
import struct as _struct
import pprint as _pprint

#: True if platform is natively big endian, False otherwise.
BIG_ENDIAN_PLATFORM = _struct.pack('=h', 1) == _struct.pack('>h', 1)

#-----------------------------------------------------------------------------
#   Custom exceptions.
#-----------------------------------------------------------------------------
class AddrFormatError(Exception):
    """
    An Exception indicating that a network address format is not recognised.
    """
    pass

#-----------------------------------------------------------------------------
class AddrConversionError(Exception):
    """
    An Exception indicating a failure to convert between address types or
    notations.
    """
    pass

#-----------------------------------------------------------------------------
def num_bits(n):
    """Minimum number of bits needed to represent a given unsigned integer."""
    n = abs(n)
    numbits = 0
    while n:
         numbits += 1
         n >>= 1
    return numbits

#-----------------------------------------------------------------------------
class Subscriber(object):
    """
    Abstract class defining interface expected by a Publisher that concrete
    subclass instances register with to receive updates from.
    """
    def update(self, data):
        """
        Callback function used by Publisher to notify this Subscriber about
        an update.
        """
        raise NotImplementedError('cannot invoke virtual method!')

#-----------------------------------------------------------------------------
class PrettyPrinter(Subscriber):
    """
    Concrete Subscriber that uses the pprint module to format all data from
    updates received writing them to any file-like object. Useful for
    debugging.
    """
    def __init__(self, fh=_sys.stdout, write_eol=True):
        """
        Constructor.

        fh - file or file like object to write to. Default: sys.stdout.
        """
        self.fh = fh
        self.write_eol = write_eol

    def update(self, data):
        """
        Callback function used by Publisher to notify this Subscriber about
        an update.
        """
        self.fh.write(_pprint.pformat(data))
        if self.write_eol:
            self.fh.write("\n")

#-----------------------------------------------------------------------------
class Publisher(object):
    """
    A 'push' publisher that maintains a list of Subscriber objects notifying
    them of state changes when its subclasses encounter events of interest.
    """
    def __init__(self):
        """Constructor"""
        self.subscribers = []

    def attach(self, subscriber):
        """Add a new subscriber"""
        if hasattr(subscriber, 'update') and \
           callable(eval('subscriber.update')):
            if subscriber not in self.subscribers:
                self.subscribers.append(subscriber)
        else:
            raise TypeError('%r does not support required interface!' \
                % subscriber)

    def detach(self, subscriber):
        """Remove an existing subscriber"""
        try:
            self.subscribers.remove(subscriber)
        except ValueError:
            pass

    def notify(self, data):
        """Send notification message to all registered subscribers"""
        for subscriber in self.subscribers:
            subscriber.update(data)

