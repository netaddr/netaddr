#!/bin/bash
#
#   netaddr source release script
#
cd $(dirname $0)
rm docs/api/*
#   epydoc is required below - http://epydoc.sourceforge.net/
epydoc --html --output ./docs/api/ --name netaddr --no-private netaddr
python setup.py sdist --no-defaults --formats=gztar,zip --dist-dir=../builds/
