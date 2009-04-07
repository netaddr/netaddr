#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Classes and routines that are common to various netaddr sub modules.
"""
import sys as _sys
import pprint as _pprint

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
