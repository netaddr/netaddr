#!/bin/bash
#
#   netaddr source release script
#
# get latest .spec file
wget http://cvs.fedoraproject.org/viewvc/devel/python-netaddr/python-netaddr.spec?view=co

#   clean up
cd $(dirname $0)
rm docs/api/*
rm ./docs/netaddr.zip

#   build API documentation using epydoc
epydoc --config=docs/epydoc.cfg

#   build source releases
cd docs/api/
zip ../netaddr.zip *
cd ../..
python setup.py sdist --no-defaults --formats=gztar,zip --dist-dir=../builds/
