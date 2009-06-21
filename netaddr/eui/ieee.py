#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
#
#   DISCLAIMER
#
#   netaddr is not sponsored nor endorsed by the IEEE.
#
#   Use of data from the IEEE (Institute of Electrical and Electronics
#   Engineers) is subject to copyright. See the following URL for
#   details :-
#
#    U{http://www.ieee.org/web/publications/rights/legal.html}
#
#   IEEE data files included with netaddr are not modified in any way but are
#   parsed and made available to end users through an API. There is no
#   guarantee that referenced files are not out of date.
#
#   See README file and source code for URLs to latest copies of the relevant
#   files.
#
#-----------------------------------------------------------------------------
"""
Provides access to public OUI and IAB registration data published by the IEEE.

More details can be found at the following URLs :-

    - IEEE Home Page - U{http://www.ieee.org/}
    - Registration Authority Home Page - U{http://standards.ieee.org/regauth/}
"""

import os as _os
import os.path as _path
import csv as _csv

from netaddr.core import Subscriber, Publisher

#-----------------------------------------------------------------------------

#: Path to local copy of IEEE OUI Registry data file.
IEEE_OUI_REGISTRY = _path.join(_path.dirname(__file__), 'oui.txt')
#: Path to netaddr OUI index file.
IEEE_OUI_METADATA = _path.join(_path.dirname(__file__), 'oui.idx')

#: OUI index lookup dictionary.
IEEE_OUI_INDEX = {}

#: Path to local copy of IEEE IAB Registry data file.
IEEE_IAB_REGISTRY = _path.join(_path.dirname(__file__), 'iab.txt')

#: Path to netaddr IAB index file.
IEEE_IAB_METADATA = _path.join(_path.dirname(__file__), 'iab.idx')

#: IAB index lookup dictionary.
IEEE_IAB_INDEX = {}

#-----------------------------------------------------------------------------
class NotRegisteredError(Exception):
    """
    An Exception indicating that an OUI or IAB was not found in the IEEE
    Registry.
    """
    pass

#-----------------------------------------------------------------------------
class FileIndexer(Subscriber):
    """Stores index data found by a parser in a CSV file"""
    def __init__(self, filename):
        """
        Constructor.

        filename - location of CSV index file.
        """
        self.fh = open(filename, 'w')
        self.writer = _csv.writer(self.fh, lineterminator="\n")

    def update(self, data):
        """
        Write received record to a CSV file

        @param data: record containing offset record information.
        """
        self.writer.writerow(data)

#-----------------------------------------------------------------------------
class OUIIndexParser(Publisher):
    """
    A parser that processes OUI (Organisationally Unique Identifier)
    registration file data published by the IEEE.

    It sends out notifications to registered subscribers for each record it
    encounters, passing on the record's position relative to file start
    (offset) and the size of the record (in bytes).

    The file is available online here :-

        - U{http://standards.ieee.org/regauth/oui/oui.txt}

    Sample record::

        00-CA-FE   (hex)        ACME CORPORATION
        00CAFE     (base 16)        ACME CORPORATION
                        1 MAIN STREET
                        SPRINGFIELD
                        UNITED STATES
    """
    def __init__(self, filename):
        """
        Constructor.

        filename - location of file containing OUI records.
        """
        super(OUIIndexParser, self).__init__()
        self.fh = open(filename, 'rb')

    def parse(self):
        """Parse an OUI registration file for records notifying subscribers"""
        skip_header = True
        record = None
        size = 0

        while True:
            line = self.fh.readline() # unbuffered to obtain correct offsets

            if not line:
                break   # EOF, we're done

            if skip_header and '(hex)' in line:
                skip_header = False

            if skip_header:
                #   ignoring header section
                continue

            if '(hex)' in line:
                #   record start
                if record is not None:
                    #   a complete record.
                    record.append(size)
                    self.notify(record)

                size = len(line)
                offset = (self.fh.tell() - len(line))
                oui = line.split()[0]
                index = int(oui.replace('-', ''), 16)
                record = [index, offset]
            else:
                #   within record
                size += len(line)

        #   process final record on loop exit
        record.append(size)
        self.notify(record)

#-----------------------------------------------------------------------------
class IABIndexParser(Publisher):
    """
    A parser that processes IAB (Individual Address Block) registration file
    data published by the IEEE.

    It sends out notifications to registered Subscriber objects for each
    record it encounters, passing on the record's position relative to file
    start (offset) and the size of the record (in bytes).

    The file is available online here :-

        - U{http://standards.ieee.org/regauth/oui/iab.txt}

    Sample record::

        00-50-C2   (hex)        ACME CORPORATION
        ABC000-ABCFFF     (base 16)        ACME CORPORATION
                        1 MAIN STREET
                        SPRINGFIELD
                        UNITED STATES
    """
    def __init__(self, filename):
        """
        Constructor.

        filename - location of file containing IAB records.
        """
        super(IABIndexParser, self).__init__()
        self.fh = open(filename, 'rb')

    def parse(self):
        """Parse an IAB registration file for records notifying subscribers"""
        skip_header = True
        record = None
        size = 0
        while True:
            line = self.fh.readline()   # unbuffered

            if not line:
                break   # EOF, we're done

            if skip_header and '(hex)' in line:
                skip_header = False

            if skip_header:
                #   ignoring header section
                continue

            if '(hex)' in line:
                #   record start
                if record is not None:
                    record.append(size)
                    self.notify(record)

                offset = (self.fh.tell() - len(line))
                iab_prefix = line.split()[0]
                index = iab_prefix
                record = [index, offset]
                size = len(line)
            elif '(base 16)' in line:
                #   within record
                size += len(line)
                prefix = record[0].replace('-', '')
                suffix = line.split()[0]
                suffix = suffix.split('-')[0]
                record[0] = (int(prefix + suffix, 16)) >> 12
            else:
                #   within record
                size += len(line)

        #   process final record on loop exit
        record.append(size)
        self.notify(record)

#-----------------------------------------------------------------------------
def create_ieee_indices():
    """Create indices for OUI and IAB file based lookups"""
    oui_parser = OUIIndexParser(IEEE_OUI_REGISTRY)
    oui_parser.attach(FileIndexer(IEEE_OUI_METADATA))
    oui_parser.parse()

    iab_parser = IABIndexParser(IEEE_IAB_REGISTRY)
    iab_parser.attach(FileIndexer(IEEE_IAB_METADATA))
    iab_parser.parse()

#-----------------------------------------------------------------------------
def load_ieee_indices():
    """Load OUI and IAB lookup indices into memory"""
    for row in _csv.reader(open(IEEE_OUI_METADATA)):
        (key, offset, size) = [int(_) for _ in row]
        IEEE_OUI_INDEX.setdefault(key, [])
        IEEE_OUI_INDEX[key].append((offset, size))

    for row in _csv.reader(open(IEEE_IAB_METADATA)):
        (key, offset, size) = [int(_) for _ in row]
        IEEE_IAB_INDEX.setdefault(key, [])
        IEEE_IAB_INDEX[key].append((offset, size))

#-----------------------------------------------------------------------------
def get_latest_files():
    """Download the latest files from the IEEE"""
    import urllib2

    urls = [
        'http://standards.ieee.org/regauth/oui/oui.txt',
        'http://standards.ieee.org/regauth/oui/iab.txt',
    ]

    for url in urls:
        print 'downloading latest copy of %s' % url
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        save_path = _path.dirname(__file__)
        filename = _path.join(save_path, _os.path.basename(response.geturl()))
        fh = open(filename, 'wb')
        fh.write(response.read())
        fh.close()

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #   Generate indices when module is executed as a script.
    get_latest_files()
    create_ieee_indices()


#   On module load read indices in memory to enable lookups.
load_ieee_indices()
