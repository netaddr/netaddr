#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Provides access to public network address information published by the IEEE.

More details can be found at the following URLs :-

Institute of Electrical and Electronics Engineers (IEEE)

    - http://www.ieee.org/
    - http://standards.ieee.org/regauth/oui/
"""

import sys as _sys
import os as _os
import os.path as _path
import csv as _csv

import pprint as _pprint

from netaddr.core import Subscriber, Publisher

#-----------------------------------------------------------------------------
#   Constants.
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

    http://standards.ieee.org/regauth/oui/oui.txt

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

    http://standards.ieee.org/regauth/oui/iab.txt

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
class OUI(object):
    """
    Represents an individual IEEE OUI (Organisationally Unique Identifier)
    identifier.

    For online details see - http://standards.ieee.org/regauth/oui/
    """
    def __init__(self, oui):
        """
        Constructor

        @param oui: an OUI string C{XX-XX-XX} or an unsigned integer.
            Also accepts and parses full MAC/EUI-48 address strings (but not
            MAC/EUI-48 integers)!
        """
        self.value = None
        self.records = []

        if isinstance(oui, str):
#FIXME: Improve string parsing here. Accept full MAC/EUI-48 addressse as
#FIXME: well as XX-XX-XX and just take /16 (see IAB for details)!
            self.value = int(oui.replace('-', ''), 16)
        elif isinstance(oui, (int, long)):
            if 0 <= oui <= 0xffffff:
                self.value = oui
            else:
                raise ValueError('OUI int outside expected range: %r' % oui)
        else:
            raise TypeError('unexpected OUI format: %r' % oui)

        #   Discover offsets.
        if self.value in IEEE_OUI_INDEX:
            fh = open(IEEE_OUI_REGISTRY, 'rb')
            for (offset, size) in IEEE_OUI_INDEX[self.value]:
                fh.seek(offset)
                data = fh.read(size)
                self._parse_data(data, offset, size)
            fh.close()
        else:
            raise NotRegisteredError('OUI %r not registered!' % oui)

    def _parse_data(self, data, offset, size):
        """Returns a dict record from raw OUI record data"""
        record = {
            'idx': 0,
            'oui': '',
            'org': '',
            'address' : [],
            'offset': offset,
            'size': size,
        }

        for line in data.split("\n"):
            line = line.strip()
            if line == '':
                continue

            if '(hex)' in line:
                record['idx'] = self.value
                record['org'] = ' '.join(line.split()[2:])
                record['oui'] = str(self)
            elif '(base 16)' in line:
                continue
            else:
                record['address'].append(line)

        self.records.append(record)

    def org_count(self):
        """@return: number of organisations with this OUI"""
        return len(self.records)

    def address(self, index=0):
        """
        @param index: the index of record (multiple registrations)
            (Default: 0 - first registration)

        @return: registered address of organisation linked to OUI
        """
        return self.records[index]['address']

    def org(self, index=0):
        """
        @param index: the index of record (multiple registrations)
            (Default: 0 - first registration)

        @return: the name of organisation linked to OUI
        """
        return self.records[index]['org']

    organisation = org

    def __int__(self):
        """@return: integer representation of this OUI"""
        return self.value

    def __hex__(self):
        """
        @return: hexadecimal string representation of this OUI (in network byte
        order).
        """
        return hex(self.value).rstrip('L').lower()

    def __str__(self):
        """@return: string representation of this OUI"""
        int_val = self.value
        words = []
        for _ in range(3):
            word = int_val & 0xff
            words.append('%02x' % word)
            int_val >>= 8
        return '-'.join(reversed(words)).upper()

    def registration(self):
        """@return: registration details for this IAB"""
        return self.records

    def __repr__(self):
        """@return: executable Python string to recreate equivalent object."""
        return '%s(%r)' % (self.__class__.__name__, str(self))

#-----------------------------------------------------------------------------
class IAB(object):
    """
    Represents an individual IEEE IAB (Individual Address Block) identifier.

    For online details see - http://standards.ieee.org/regauth/oui/
    """
    def split_iab_mac(eui_int, strict=False):
        """
        @param eui_int: a MAC IAB as an unsigned integer.

        @param strict: If True, raises a ValueError if the last 12 bits of
            IAB MAC/EUI-48 address are non-zero, ignores them otherwise.
            (Default: False)
        """
        if 0x50c2000 <= eui_int <= 0x50c2fff:
            return eui_int, 0

        user_mask = 2 ** 12 - 1
        iab_mask = (2 ** 48 - 1) ^ user_mask
        iab_bits = eui_int >> 12
        user_bits = (eui_int | iab_mask) - iab_mask

        if 0x50c2000 <= iab_bits <= 0x50c2fff:
            if strict and user_bits != 0:
                raise ValueError('%r is not a strict IAB!' % hex(user_bits))
        else:
            raise ValueError('%r is not an IAB address!' % hex(eui_int))

        return iab_bits, user_bits

    split_iab_mac = staticmethod(split_iab_mac)

    def __init__(self, iab, strict=False):
        """
        Constructor

        @param iab: an IAB string C{00-50-C2-XX-X0-00} or an unsigned integer.
            This address looks like an EUI-48 but it should not have any
            non-zero bits in the last 3 bytes.

        @param strict: If True, raises a ValueError if the last 12 bits of
            IAB MAC/EUI-48 address are non-zero, ignores them otherwise.
            (Default: False)
        """
        self.value = None
        self.record = {
            'idx': 0,
            'iab': '',
            'org': '',
            'address' : [],
            'offset': 0,
            'size': 0,
        }

        if isinstance(iab, str):
#FIXME: Improve string parsing here !!! '00-50-C2' is actually invalid.
#FIXME: Should be '00-50-C2-00-00-00' (i.e. a full MAC/EUI-48)
            int_val = int(iab.replace('-', ''), 16)
            (iab_int, user_int) = IAB.split_iab_mac(int_val, strict)
            self.value = iab_int
        elif isinstance(iab, (int, long)):
            (iab_int, user_int) = IAB.split_iab_mac(iab, strict)
            self.value = iab_int
        else:
            raise TypeError('unexpected IAB format: %r!' % iab)

        #   Discover offsets.
        if self.value in IEEE_IAB_INDEX:
            fh = open(IEEE_IAB_REGISTRY, 'rb')
            (offset, size) = IEEE_IAB_INDEX[self.value][0]
            self.record['offset'] = offset
            self.record['size'] = size
            fh.seek(offset)
            data = fh.read(size)
            self._parse_data(data, offset, size)
            fh.close()
        else:
            raise NotRegisteredError('IAB %r not unregistered!' % iab)

    def _parse_data(self, data, offset, size):
        """Returns a dict record from raw IAB record data"""
        for line in data.split("\n"):
            line = line.strip()
            if line == '':
                continue

            if '(hex)' in line:
                self.record['idx'] = self.value
                self.record['org'] = ' '.join(line.split()[2:])
                self.record['iab'] = str(self)
            elif '(base 16)' in line:
                continue
            else:
                self.record['address'].append(line)

    def address(self):
        """@return: registered address of organisation"""
        return self.record['address']

    def org(self):
        """@return: the name of organisation"""
        return self.record['org']

    organisation = org

    def __int__(self):
        """@return: integer representation of this IAB"""
        return self.value

    def __hex__(self):
        """
        @return: hexadecimal string representation of this IAB (in network
            byte order)
        """
        return hex(self.value).rstrip('L').lower()

    def __str__(self):
        """@return: string representation of this IAB"""
        int_val = self.value << 12
        words = []
        for _ in range(6):
            word = int_val & 0xff
            words.append('%02x' % word)
            int_val >>= 8
        return '-'.join(reversed(words)).upper()

    def registration(self):
        """@return: registration details for this IAB"""
        return self.record

    def __repr__(self):
        """@return: executable Python string to recreate equivalent object."""
        return '%s(%r)' % (self.__class__.__name__, str(self))

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
    """Load OUI and IAB indices into memory"""
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
