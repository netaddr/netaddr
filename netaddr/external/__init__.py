#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
classes and functions providing access to public data from the IEEE and IANA.

Information processed here is made available via various methods on objects of
supported network address types such as IP() and EUI(). See netaddr.address
module documentation for more details.

References
==========

1)  Internet Assigned Numbers Authority (IANA)

http://www.iana.org/

2) Institute of Electrical and Electronics Engineers (IEEE)

http://www.ieee.org/
"""

import os as _os
import os.path as _path
import sys as _sys
import re as _re
import pprint as _pprint
import shelve as _shelve

#-----------------------------------------------------------------------------
#   Constants.
#-----------------------------------------------------------------------------

#: Path where original text-based data files are found.
SRC_PATH = _path.join(_path.dirname(__file__), 'src')

#: Path where shelve persistence files are created and stored.
CACHE_PATH = _path.join(_path.dirname(__file__), 'cache')

#: Path to IANA IPv4 persistence data.
IANA_IPV4_PATH = _path.join(CACHE_PATH, r'iana-ipv4-space.shlv')

#: Path to IANA IPv6 persistence data.
IANA_IPV6_PATH = _path.join(CACHE_PATH, r'iana-ipv6-space.shlv')

#: Path to IANA IPv4 multicast persistence data.
IANA_MULTICAST_PATH = _path.join(CACHE_PATH, r'iana-ipv4-mcast.shlv')

#: Path to OUI registry persistence data.
IEEE_OUI_PATH = _path.join(CACHE_PATH, r'ieee-oui.shlv')

#-----------------------------------------------------------------------------
class Subscriber(object):
    """
    Attaches to a Publisher and receives updates when it changes.
    """
    def update(self, data):
        """
        Callback function used by Publisher to notify this Subscriber about
        an update.
        """
        raise RuntimeError('virtual method!')

#-----------------------------------------------------------------------------
class FileWriter(Subscriber):
    """
    A concrete Subscriber that pretty prints out all data receieved to given
    file or file-like object such as StringIO object.
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
class Parser(object):
    """
    Understands the format of a particular data file type and extracts
    information from it.

    Maintains a list of Subscribers, sending out updates to them when its
    internal state changes.
    """
    def __init__(self, fh):
        """
        Constructor.

        fh - a valid, open file handle to parsable data.
        """
        self.subscribers = []

        if not isinstance(fh, file):
           raise TypeError('A valid Python file object is required!')

        self.fh = fh

    def attach(self, subscriber):
        """
        Register a new subscriber.
        """
        if 'update' in dir(subscriber) and callable(eval('subscriber.update')):
            if subscriber not in self.subscribers:
                self.subscribers.append(subscriber)
        else:
            raise TypeError('%r does not support required interface!' \
                % subscriber)

    def detach(self, subscriber):
        """
        Unregister an existing subscriber.
        """
        try:
            self.subscribers.remove(subscriber)
        except ValueError:
            pass

    def notify(self, data):
        for subscriber in self.subscribers:
            subscriber.update(data)

    def parse(self):
        """
        Method called to initiate parsing and notification of attached
        Subscriber subclass instances.
        """
        pass

#-----------------------------------------------------------------------------
class LineRecordParser(Parser):
    """
    A configurable Parser that understands how to parse line based records.
    """
    def __init__(self, fh, **kwargs):
        """
        Constructor.

        fh - a valid, open file handle to line based record data.
        """
        super(LineRecordParser, self).__init__(fh)

        self.__dict__.update(kwargs)

        #   Regex used to identify start of lines of interest.
        if 're_start' not in self.__dict__:
            self.re_start = r'^.*$'

        #   Regex used to identify line to be parsed within block of interest.
        if 're_parse_line' not in self.__dict__:
            self.re_parse_line = r'^.*$'

        #   Regex used to identify end of lines of interest.
        if 're_stop' not in self.__dict__:
            self.re_stop = r'^.*$'

        #   If enabled, skips blank lines after being stripped.
        if 'skip_blank_lines' not in self.__dict__:
            self.skip_blank_lines = False

    def parse_line(self, line):
        """
        This is the callback method invoked for every line considered valid by
        the line parser's settings. It is usually over-ridden by base classes
        to provide specific line parsing and line skipping logic.

        Any line can be vetoed (not passed to registered Subscriber objects)
        by simply returning None.
        """
        return line

    def parse(self):
        """
        Parse and normalises records, notifying registered subscribers with
        record data as it is encountered.
        """
        record = None
        section_start = False
        section_end = False

        for line in self.fh:
            line = line.strip()

            #   Skip blank lines if required.
            if self.skip_blank_lines and line == '':
                continue

            #   Entered record section.
            if not section_start and len(_re.findall(self.re_start, line)) > 0:
                section_start = True

            #   Exited record section.
            if section_start and len(_re.findall(self.re_stop, line)) > 0:
                section_end = True

            #   Stop parsing.
            if section_end:
                break

            #   Is this a line of interest?
            if section_start and len(_re.findall(self.re_parse_line, line)) == 0:
                continue

            if section_start:
                record = self.parse_line(line)

                #   notify subscribers of final record details.
                self.notify(record)

#-----------------------------------------------------------------------------
class IPv4Parser(LineRecordParser):
    """
    A LineRecordParser that understands how to parse and retrieve data from
    an IANA IPv4 address space file found here :-

    http://www.iana.org/assignments/ipv4-address-space
    """
    def __init__(self, fh, **kwargs):
        """
        Constructor.

        fh - a valid, open file handle to an OUI Registry data file.

        kwargs - additional parser options.

        """
        super(IPv4Parser, self).__init__(fh,
            re_start=r'^Prefix',
            re_parse_line=r'^\d{3}\/\d',
            re_stop=r'^Notes\s*$',
            skip_blank_lines=True,
        )

        self.record_widths = (
            ('prefix', 0, 8),
            ('designation', 8, 37),
            ('date', 45, 10),
            ('whois', 55, 20),
            ('status', 75, 19),
        )

    def parse_line(self, line):
        """
        Callback method invoked for every line considered valid by the line
        parser's settings.

        See base class method for more details.
        """
        record = {}
        for (key, start, width) in self.record_widths:
            value = line[start:start+width]
            record[key] = value.strip()

        #   Strip leading zeros from octet.
        if '/' in record['prefix']:
            (octet, prefix) = record['prefix'].split('/')
            record['prefix'] = "%d/%d" % (int(octet), int(prefix))

        record['status'] = record['status'].capitalize()

        return record

#-----------------------------------------------------------------------------
class IPv6Parser(LineRecordParser):
    """
    A LineRecordParser that understands how to parse and retrieve data from
    an IANA IPv6 address space file found here :-

    http://www.iana.org/assignments/ipv6-address-space
    """
    def __init__(self, fh, **kwargs):
        """
        Constructor.

        fh - a valid, open file handle to an OUI Registry data file.

        kwargs - additional parser options.

        """
        super(IPv6Parser, self).__init__(fh,
        re_start=r'^IPv6 Prefix',
        re_parse_line=r'^[A-F0-9]+::\/\d+',
        re_stop=r'^Notes:\s*$',
            skip_blank_lines=True)

        self.record_widths = (
            ('prefix', 0, 22),
            ('allocation', 22, 24),
            ('reference', 46, 15))

    def parse_line(self, line):
        """
        Callback method invoked for every line considered valid by the line
        parser's settings.

        See base class method for more details.
        """
        record = {}
        for (key, start, width) in self.record_widths:
            value = line[start:start+width]
            record[key] = value.strip()

            #   Remove square brackets from reference field.
            record[key] = record[key].lstrip('[')
            record[key] = record[key].rstrip(']')
        return record

#-----------------------------------------------------------------------------
class MulticastParser(LineRecordParser):
    """
    A LineParser that knows how to process an IANA IPv4 multicast address
    allocation file found here :-

    http://www.iana.org/assignments/multicast-addresses
    """
    def __init__(self, fh, **kwargs):
        """
        Constructor.

        fh - a valid, open file handle to an OUI Registry data file.

        kwargs - additional parser options.

        """
        super(MulticastParser, self).__init__(fh,
        re_start=r'^Registry:',
        re_parse_line=r'^\d+\.\d+\.\d+\.\d+',
        re_stop=r'^Relative',
            skip_blank_lines=True)

    def normalise_addr(self, addr):
        """
        Removes variations from address entries found in this particular file.
        """
        if '-' in addr:
            (a1, a2) = addr.split('-')
            o1 = a1.strip().split('.')
            o2 = a2.strip().split('.')
            return "%s-%s" % ('.'.join([str(int(i)) for i in o1]),
                              '.'.join([str(int(i)) for i in o2]))
        else:
            o1 = addr.strip().split('.')
            return '.'.join([str(int(i)) for i in o1])

    def parse_line(self, line):
        """
        Callback method invoked for every line considered valid by the line
        parser's settings.

        See base class method for more details.
        """
        index = line.find('[')
        if index != -1:
            line = line[0:index].strip()
        (addr, descr) = [i.strip() for i in _re.findall(
            r'^([\d.]+(?:\s*-\s*[\d.]+)?)\s+(.+)$', line)[0]]
        addr = self.normalise_addr(addr)
        return dict(address=addr, descr=descr)

#-----------------------------------------------------------------------------
class OUIParser(Parser):
    """
    A Parser that knows how to process an OUI (Organisationally Unique
    Identifier) Registration Information file, found here :-

    http://standards.ieee.org/regauth/oui/oui.txt
    """
    def __init__(self, fh):
        """
        Constructor.

        fh - a valid, open file handle to an OUI Registry data file.
        """
        super(OUIParser, self).__init__(fh)

    def normalise_org(self, org):
        """
        Fixes some inconsistencies in organisation names for some OUI records.

        """
        #TODO:  It would be good to revisit this and try to fix up
        #TODO:  abbreviations at some point e.g. Corp <-> Corporation.
        org = org.replace('.', ' ')
        org = org.replace(',', ' ')
        tokens = org.split()
        if org.isupper():
            tokens = [t.capitalize() for t in tokens]
        org = ' '.join(tokens)
        return org

    def parse(self):
        """
        Parses an OUI data registration file for OUI data records.
        """
        record = {'address' : [], 'org': None, 'id': None, 'prefix': None}
        for line in self.fh:
            line = line.strip()

            if line == '':
                continue

            fields = line.split()
            #print fields

            #   Skip header fields.
            if fields == ['OUI', 'Organization']:
                continue
            elif fields == ['company_id', 'Organization']:
                continue
            elif fields == ['Address']:
                continue

            if len(fields) == 1:
                record['address'].append(line)
            elif fields[1] == '(hex)':

                #   notify listeners of record details.
                if record['id'] is not None:
                    self.notify(record)

                record = {'address' : [], 'org': None, 'id': None}
                record['id'] = int(fields[0].replace('-', ''), 16)
                record['org'] = self.normalise_org(' '.join(fields[2:]))
                record['prefix'] = fields[0]


            elif fields[1:3] == ['(base', '16)']:
                continue
            else:
                record['address'].append(line)

        #   Get last record.
        record['address'].append(line)

        #   notify listeners of final record details.
        self.notify(record)

#-----------------------------------------------------------------------------
class IABParser(Parser):
    """
    A Parser that knows how to process an IAB (Individual Address Block)
    Registration Information file found here :-

    http://standards.ieee.org/regauth/oui/iab.txt
    """
    #TODO
    pass

#-----------------------------------------------------------------------------
class ShelveArchiver(Subscriber):
    """
    A concrete Subscriber class that listens to updates from a Parser and
    persists information received for later retrieval in a cached archive
    using the 'shelve' Python standard module.
    """
    def __init__(self, fname, key):
        """
        Constructor.

        @param fname: file used to store persisted information received.

        @param key: name of field in each data dictionary received by the
        update() method that contains the unique identifier for each record
        being persisted.
        """
        self.fname = fname
        self.key = key
        self.closed = True
        self.committed = True

        if _path.exists(self.fname) and _path.isfile(self.fname):
            self.db = _shelve.open(self.fname, 'w')    #   Open mode.
        else:
            self.db = _shelve.open(self.fname, 'c')    #   Create mode.

        self.closed = False

    def __del__(self):
        """
        Destructor.

        Ensures shelve file is synchronized and closed.
        """
        if not self.closed:
            self.close()

    def close(self):
        """
        Synchronizes unsaved changes and closes shelve persistence file.
        """
        if not self.committed:
            self.commit()
        self.db.close()
        self.closed = True

    def commit(self):
        """
        Synchronizes unsaved changes to shelve persistence file.
        """
        self.db.sync()
        self.committed = True

    def update(self, data):
        """
        Callback function used by Publisher to notify this Subscriber about
        an update.
        """
        self.committed = False
        key = data[self.key]
        self.db[key] = data


#-----------------------------------------------------------------------------
class ShelveReader(Subscriber):
    """
    Reads records efficiently from shelve persistence files presenting the
    data via simple Python dictionary lookups.

    A read-only class that ignores any dictionary update attempts.
    """

    def __init__(self, fname):
        """
        Constructor.

        @param fname: file used to read persisted information from.
        """
        self.fname = fname
        self.closed = True

        try:
            self.db = _shelve.open(self.fname, 'r')     #   Read mode.
        except Exception, e:
            print 'Error: failed to open file %s' % self.fname
            raise e

        self.closed = False

    def __del__(self):
        """
        Destructor.

        Ensures shelve file is synchronized and closed.
        """
        if not self.closed:
            self.close()

    def close(self):
        """Closes shelve file properly."""
        self.db.close()
        self.closed = True

    def __getitem__(self, key):
        """
        Return data from shelve object if found using key, None otherwise.
        """
        try:
            return self.db[key]
        except KeyError:
            return None

#-----------------------------------------------------------------------------
def update_caches():
    """
    Create and/or updates caches with the latest information from data files.
    """
    print 'updating caches...'

    oui = OUIParser(open(_path.join(SRC_PATH, r'oui.txt')))
    #DEBUG: oui.attach(FileWriter())
    oui.attach(ShelveArchiver(IEEE_OUI_PATH, 'prefix'))
    oui.parse()

    ipv4 = IPv4Parser(open(_path.join(SRC_PATH, r'ipv4-address-space')))
    #DEBUG: ipv4.attach(FileWriter())
    ipv4.attach(ShelveArchiver(IANA_IPV4_PATH, 'prefix'))
    ipv4.parse()

    ipv6 = IPv6Parser(open(_path.join(SRC_PATH, r'ipv6-address-space')))
    #DEBUG: ipv6.attach(FileWriter())
    ipv6.attach(ShelveArchiver(IANA_IPV6_PATH, 'prefix'))
    ipv6.parse()

    mc = MulticastParser(open(_path.join(SRC_PATH, r'multicast-addresses')))
    #DEBUG: mc.attach(FileWriter())
    mc.attach(ShelveArchiver(IANA_MULTICAST_PATH, 'address'))
    mc.parse()

    print 'cache update completed'

#-----------------------------------------------------------------------------
#def read_caches():
#    """
#    Read from caches and update module variables with information retrieved.
#    """
#    #   Populate IPv4 lookup.
#    ipv4 = ShelveReader(IANA_IPV4_PATH)
#    for prefix, data in ipv4.db.items():
#        cidr = CIDR(prefix)
#        EXT_LOOKUP['IPv4'][cidr] = data
#
#    #   Populate IPv6 lookup.
#    ipv6 = ShelveReader(IANA_IPV6_PATH)
#    for prefix, data in ipv6.db.items():
#        cidr = CIDR(prefix)
#        EXT_LOOKUP['IPv6'][cidr] = data
#
#    #   Populate IPv4 multicast lookup.
#    mcast = ShelveReader(IANA_MULTICAST_PATH)
#    for ip_lookup, data in mcast.db.items():
#        iprange = None
#        if '-' in ip_lookup:
#            (first, last) = ip_lookup.split('-')
#            iprange = IPRange(first, last)
#        else:
#            iprange = IPRange(ip_lookup, ip_lookup)
#        EXT_LOOKUP['multicast'][iprange] = data
#
#    #   Populate OUI lookup.
#    EXT_LOOKUP['OUI'] = ShelveReader(IEEE_OUI_PATH)
#
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    #   Only create and/or update shelve data when this file is run not when
    #   it is imported.
    update_caches()

#   On module import, read shelve data and populate module level lookups.
#read_caches()
