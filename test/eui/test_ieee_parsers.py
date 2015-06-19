from io import StringIO

from netaddr.eui.ieee import OUIIndexParser, IABIndexParser, FileIndexer


def test_oui_parser():
    infile = StringIO()
    outfile = StringIO()
    infile.write("""
00-CA-FE   (hex)        ACME CORPORATION
00CAFE     (base 16)        ACME CORPORATION
				1 MAIN STREET
				SPRINGFIELD
				UNITED STATES
""")

    infile.seek(0)
    iab_parser = OUIIndexParser(infile)
    iab_parser.attach(FileIndexer(outfile))
    iab_parser.parse()
    assert outfile.getvalue() == '51966,1,138\n'


def test_iab_parser():
    infile = StringIO()
    outfile = StringIO()
    infile.write("""
00-50-C2   (hex)        ACME CORPORATION
ABC000-ABCFFF     (base 16)        ACME CORPORATION
                1 MAIN STREET
                SPRINGFIELD
                UNITED STATES
""")

    infile.seek(0)
    iab_parser = IABIndexParser(infile)
    iab_parser.attach(FileIndexer(outfile))
    iab_parser.parse()
    assert outfile.getvalue() == '84683452,1,181\n'
