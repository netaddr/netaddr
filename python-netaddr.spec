%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-netaddr
Version:        0.5.2
Release:        1%{?dist}
Summary:        Network address manipulation, done Pythonically

Group:          Development/Libraries
License:        BSD
URL:            http://code.google.com/p/netaddr/
Source0:        http://netaddr.googlecode.com/files/netaddr-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools

%description
netaddr is a network address manipulation library written in pure Python.

It supports the Pythonic manipulation of several common network address
notations and standards, including :-

- IP version 4
- IP version 6
- CIDR (Classless Inter-Domain Routing)
- IEEE EUI-48 and EUI-64
- MAC (Media Access Control)

%prep
%setup -q -n netaddr-%{version}
chmod 644 tests/*


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
chmod 755 $RPM_BUILD_ROOT%{python_sitelib}/netaddr/__init__.py
chmod 755 $RPM_BUILD_ROOT%{python_sitelib}/netaddr/strategy.py
chmod 755 $RPM_BUILD_ROOT%{python_sitelib}/netaddr/address.py


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc GLOSSARY INSTALL LICENSE PKG-INFO README docs/api/ tests
%{python_sitelib}/*


%changelog
* Fri Oct 10 2008 John Eckersberg <jeckersb@redhat.com> - 0.5.2-1
- New upstream version, bug fixes for 0.5.1

* Tue Sep 23 2008 John Eckersberg <jeckersb@redhat.com> - 0.5.1-1
- New upstream version, bug fixes for 0.5

* Sun Sep 21 2008 John Eckersberg <jeckersb@redhat.com> - 0.5-1
- New upstream version

* Mon Aug 11 2008 John Eckersberg <jeckersb@redhat.com> - 0.4-1
- Initial packaging for Fedora

