#-----------------------------------------------------------------------------
#   Copyright (c) 2008 by David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
#
# netaddr library build script
#
SHELL = /bin/bash

.PHONY = default clean dist doc download test

default:
	@echo 'Please select a build target.'

clean:
	@echo 'cleaning up temporary files'
	rm -rf dist/
	rm -rf build/
	rm -rf docs/build/
	rm -rf netaddr.egg-info/
	find . -name '*.pyc' -exec rm -f {} ';'
	find . -name '*.pyo' -exec rm -f {} ';'

dist: clean doc
	@echo 'building netaddr release'
	python setup.py develop
	@echo 'building source distributions'
	python setup.py sdist --formats=gztar,zip
	@echo 'building wheel package'
	pip install --upgrade pip
	pip install wheel
	python setup.py bdist_wheel --universal

doc:
	@echo 'building documentation'
	pip install sphinx
	python setup.py develop
	cd docs/ && $(MAKE) -f Makefile clean html
	cd docs/build/html && zip -r ../netaddr.zip *

download:
	@echo 'downloading latest IEEE data'
	cd netaddr/eui/ && wget http://standards-oui.ieee.org/oui/oui.txt
	cd netaddr/eui/ && wget http://standards-oui.ieee.org/iab/iab.txt
	@echo 'rebuilding IEEE data file indices'
	python netaddr/eui/ieee.py
	@echo 'downloading latest IANA data'
	cd netaddr/ip/ && wget https://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xml
	cd netaddr/ip/ && wget https://www.iana.org/assignments/ipv6-address-space/ipv6-address-space.xml
	cd netaddr/ip/ && wget https://www.iana.org/assignments/multicast-addresses/multicast-addresses.xml
	cd netaddr/ip/ && wget https://www.iana.org/assignments/ipv6-unicast-address-assignments/ipv6-unicast-address-assignments.xml

register:
	@echo 'releasing netaddr'
	python setup_egg.py register

push_tags:
	@echo 'syncing tags'
	git push --tags

ci: test_with_junitxml lint

lint: setup_check

setup_check:
	python setup.py check

test: clean
	@echo 'running test suite'
	pip install -r requirements.txt
	py.test netaddr/tests
	@echo 'running doc tests (tutorials)'
	python tutorials/run_doctests.py

test_with_junitxml: clean
	@echo 'running test suite with JUnit XML output'
	py.test -vv --junitxml=junit.xml
