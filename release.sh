#!/bin/bash
#
#   netaddr source release script
#
cd $(dirname $0)
rm docs/api/*
#   epydoc is required below - http://epydoc.sourceforge.net/
epydoc --config=docs/epydoc.cfg
cd docs/api/
zip ../netaddr.zip *
echo "upload your docs to PyPI with the release"
cd ../..
python setup.py sdist --no-defaults --formats=gztar,zip --dist-dir=../builds/
#   egg setup
python setup_egg.py bdist_egg --dist-dir=../builds/
