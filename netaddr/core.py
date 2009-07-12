#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""Common code shared between various netaddr sub modules"""

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
    An Exception indicating a network address is not correctly formatted.
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
def num_bits(int_val):
    """
    @param int_val: an unsigned integer.

    @return: the minimum number of bits needed to represent value provided.
    """
    int_val = abs(int_val)
    numbits = 0
    while int_val:
         numbits += 1
         int_val >>= 1
    return numbits

#-----------------------------------------------------------------------------
class Subscriber(object):
    """
    An abstract class defining the interface expected by a Publisher.
    """
    def update(self, data):
        """
        A callback method used by a Publisher to notify this Subscriber about
        updates.

        @param data: a Python object containing data provided by Publisher.
        """
        raise NotImplementedError('cannot invoke virtual method!')

#-----------------------------------------------------------------------------
class PrettyPrinter(Subscriber):
    """
    A concrete Subscriber that employs the pprint in the standard library to
    format all data from updates received, writing them to a file-like
    object.

    Useful as a debugging aid.
    """
    def __init__(self, fh=_sys.stdout, write_eol=True):
        """
        Constructor.

        @param fh: a file-like object to write updates to.
            Default: sys.stdout.


        @param write_eol: if C{True} this object will write newlines to
            output, if C{False} it will not.
        """
        self.fh = fh
        self.write_eol = write_eol

    def update(self, data):
        """
        A callback method used by a Publisher to notify this Subscriber about
        updates.

        @param data: a Python object containing data provided by Publisher.
        """
        self.fh.write(_pprint.pformat(data))
        if self.write_eol:
            self.fh.write("\n")

#-----------------------------------------------------------------------------
class Publisher(object):
    """
    A 'push' Publisher that maintains a list of Subscriber objects notifying
    them of state changes by passing them update data when it encounter events
    of interest.
    """
    def __init__(self):
        """Constructor"""
        self.subscribers = []

    def attach(self, subscriber):
        """
        Add a new subscriber.

        @param subscriber: a new object that implements the Subscriber object
            interface.
        """
        if hasattr(subscriber, 'update') and \
           callable(eval('subscriber.update')):
            if subscriber not in self.subscribers:
                self.subscribers.append(subscriber)
        else:
            raise TypeError('%r does not support required interface!' \
                % subscriber)

    def detach(self, subscriber):
        """
        Remove an existing subscriber.

        @param subscriber: a new object that implements the Subscriber object
            interface.
        """
        try:
            self.subscribers.remove(subscriber)
        except ValueError:
            pass

    def notify(self, data):
        """
        Send update data to to all registered Subscribers.

        @param data: the data to be passed to each registered Subscriber.
        """
        for subscriber in self.subscribers:
            subscriber.update(data)

