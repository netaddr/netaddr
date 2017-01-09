import os
import sys

import pytest

from netaddr.eui.ieee import OUIIndexParser, IABIndexParser, FileIndexer

if sys.version_info.major >= 3:
    from io import StringIO
else:
    from cStringIO import StringIO


SAMPLE_DIR = os.path.dirname(__file__)


def test_oui_parser():
    from io import StringIO
    outfile = StringIO()
    with open(os.path.join(SAMPLE_DIR, 'sample_oui.txt')) as infile:
        iab_parser = OUIIndexParser(infile)
        iab_parser.attach(FileIndexer(outfile))
        iab_parser.parse()
    assert outfile.getvalue() == '51966,1,138\n'


def test_oui_parser_handles_incorrect_encoding():
    from io import StringIO
    outfile = StringIO()
    with open(os.path.join(
            SAMPLE_DIR, 'sample_incorrect_encoded_oui.txt')) as infile:
        iab_parser = OUIIndexParser(infile)
        iab_parser.attach(FileIndexer(outfile))
        iab_parser.parse()
    assert outfile.getvalue() == (
        '8792,46,156\n'
        '8793,202,225\n'
        '8794,437,129\n'
        '9096,566,160\n'
        '9097,726,282\n'
        '9098,1018,148\n')


def test_iab_parser():
    from io import StringIO
    outfile = StringIO()
    with open(os.path.join(SAMPLE_DIR, 'sample_iab.txt')) as infile:
        iab_parser = IABIndexParser(infile)
        iab_parser.attach(FileIndexer(outfile))
        iab_parser.parse()
    assert outfile.getvalue() == '84683452,1,181\n'
