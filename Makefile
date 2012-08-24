#
# Build for netaddr
#
SHELL = /bin/bash

.PHONY = all clean build docs download

all:
	@echo 'default target does nothing. try clean'

clean:
	@echo 'cleaning up temporary files'
	rm -rf dist/
	rm -rf build/
	find . -name '*.pyc' -exec rm -f {} ';'
	find . -name '*.pyo' -exec rm -f {} ';'

build:
	@echo 'build netaddr release'
	python setup_egg.py develop
	python setup.py sdist --formats=gztar,zip
	python setup_egg.py bdist_egg

documentation:
	@echo 'building documentation'
	python setup_egg.py develop
	cd docs/ && $(MAKE) -f Makefile clean html
	cd docs/build/html && zip -r ../netaddr.zip *

download:
	@echo 'downloading latest IEEE data'
	cd netaddr/eui/ && wget -N http://standards.ieee.org/regauth/oui/oui.txt
	cd netaddr/eui/ && wget -N http://standards.ieee.org/regauth/oui/iab.txt
	@echo 'downloading latest IANA data'
	cd netaddr/ip/ && wget -N http://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xml
	cd netaddr/ip/ && wget -N http://www.iana.org/assignments/ipv6-address-space/ipv6-address-space.xml
	cd netaddr/ip/ && wget -N http://www.iana.org/assignments/multicast-addresses/multicast-addresses.xml
