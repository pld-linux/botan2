# TODO: fix sphinx docs build (sphinx-build hangs?)
#
# Conditional build:
%bcond_without	tests		# unit tests
%bcond_with	apidocs		# Sphinx based HTML documentation [hangs, FIXME]
%bcond_without	static_libs	# static library
%bcond_without	python		# Python bindings
%bcond_without	python2		# CPython 2.x binding
%bcond_without	python3		# CPython 3.x binding
%bcond_with	openssl		# OpenSSL provider

%if %{without python}
%undefine	with_python2
%undefine	with_python3
%endif
Summary:	Crypto library written in C++
Summary(pl.UTF-8):	Biblioteka kryptograficzna napisana w C++
Name:		botan2
Version:	2.18.1
Release:	1
License:	BSD
Group:		Libraries
Source0:	https://botan.randombit.net/releases/Botan-%{version}.tar.xz
# Source0-md5:	77c558179f276273e0bf39ef941d36c5
URL:		https://botan.randombit.net/
BuildRequires:	bzip2-devel
BuildRequires:	libstdc++-devel
%{?with_openssl:BuildRequires:	openssl-devel}
BuildRequires:	python >= 1:2.7
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
%{?with_apidocs:BuildRequires:	sphinx-pdg}
BuildRequires:	zlib-devel
%if %{with python2}
BuildRequires:	python-devel >= 1:2.7
%endif
%if %{with python3}
BuildRequires:	python3-devel >= 1:3.4
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Botan is a BSD-licensed crypto library written in C++. It provides a
wide variety of basic cryptographic algorithms, X.509 certificates and
CRLs, PKCS#10 certificate requests, a filter/pipe message processing
system, and a wide variety of other features, all written in portable
C++. The API reference, tutorial, and examples may help impart the
flavor of the library.

%description -l pl.UTF-8
Botan to biblioteka kryptograficzna na licencji BSD, napisana w C++.
Zapewnia szeroki zakres algorytmów kryptograficznych, certyfikaty
X.509 oraz CRL, żądania certyfikatów PKCS#10, system przetwarzania
komunikatów z filtrowaniem/potokami i wiele innych funkcji, wszystko
napisane w przenośnym C++. Dodatkowe udogodnienia to dokumentacja API,
wprowadzenie oraz przykłady.

%package devel
Summary:	Header files for Botan library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki Botan
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	bzip2-devel
Requires:	gmp-devel
%{?with_openssl:Requires:	openssl-devel}
Requires:	zlib-devel

%description devel
This package contains the header files for developing applications
that use Botan.

%description devel -l pl.UTF-8
Ten pakiet zawiera pliki nagłówkowe do tworzenia aplikacji
wykorzystujących bibliotekę Botan.

%package static
Summary:	Static Botan library
Summary(pl.UTF-8):	Statyczna biblioteka Botan
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static Botan library.

%description static -l pl.UTF-8
Statyczna biblioteka Botan.

%package apidocs
Summary:	Botan API documentation
Summary(pl.UTF-8):	Dokumentacja API biblioteki Botan
Group:		Documentation
BuildArch:	noarch

%description apidocs
API and internal documentation for Botan library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki Botan.

%package -n python-botan
Summary:	Python 2.x binding for Botan library
Summary(pl.UTF-8):	Wiązanie Pythona 2.x do biblioteki Botan
Group:		Libraries/Python
Requires:	%{name} = %{version}-%{release}

%description -n python-botan
Python 2.x binding for Botan library.

%description -n python-botan -l pl.UTF-8
Wiązanie Pythona 2.x do biblioteki Botan.

%package -n python3-botan
Summary:	Python 3.x binding for Botan library
Summary(pl.UTF-8):	Wiązanie Pythona 3.x do biblioteki Botan
Group:		Libraries/Python
Requires:	%{name} = %{version}-%{release}

%description -n python3-botan
Python 3.x binding for Botan library.

%description -n python3-botan -l pl.UTF-8
Wiązanie Pythona 3.x do biblioteki Botan.

%prep
%setup -q -n Botan-%{version}

# kill shebang, nothing to execute directly
%{__sed} -i -e '1d' src/python/botan2.py

%build
# we have the necessary prerequisites, so enable optional modules
%define enable_modules bzip2,lzma,zlib,%{?with_openssl:openssl},sqlite3,tpm,pkcs11

# fixme: maybe disable unix_procs, very slow.
%define disable_modules %{nil}

./configure.py \
	--prefix=%{_prefix} \
	--libdir=%{_lib} \
	--cc=gcc \
	--os=linux \
	--cpu=%{_arch} \
	--enable-modules=%{enable_modules} \
	--disable-modules=%{disable_modules} \
%if %{with python2}
	--with-python-version=%{py_ver} \
%endif
	%{!?with_apidocs:--without-sphinx}

# (ab)using CXX as an easy way to inject our CXXFLAGS
%{__make} \
	CXX="%{__cxx} -pthread" \
	CXXFLAGS="%{rpmcxxflags}"

%if %{with apidocs}
%{__make} docs
%endif

%if %{with tests}
# certstor_system test is trying tp look up expired certs
# os_utils fail on builders
LD_LIBRARY_PATH=. ./botan-test --skip-tests=certstor_system,os_utils
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	INSTALL_CMD_EXEC="install -p -m 755" \
	INSTALL_CMD_DATA="install -p -m 644" \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with python2}
%py_comp $RPM_BUILD_ROOT%{py_sitedir}
%py_ocomp $RPM_BUILD_ROOT%{py_sitedir}
%py_postclean
%endif

%if %{with python3}
install -d $RPM_BUILD_ROOT%{py3_sitedir}
cp -p src/python/botan2.py $RPM_BUILD_ROOT%{py3_sitedir}
%py3_comp $RPM_BUILD_ROOT%{py3_sitedir}
%py3_ocomp $RPM_BUILD_ROOT%{py3_sitedir}
%endif

# packaged as %doc
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/botan-%{version}

%if %{with apidocs}
install -d $RPM_BUILD_ROOT%{_examplesdir}
cp -pr doc/examples $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc license.txt news.rst readme.rst doc/{authors.txt,credits.rst,security.rst}
%attr(755,root,root) %{_bindir}/botan
%attr(755,root,root) %{_libdir}/libbotan-2.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libbotan-2.so.18
%{_mandir}/man1/botan.1*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libbotan-2.so
%{_includedir}/botan-2
%{_pkgconfigdir}/botan-2.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libbotan-2.a
%endif

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
# FIXME: update path after fixing sphinx build
%doc _doc/manual/{_static,*.html,*.js}
%{_examplesdir}/%{name}-%{version}
%endif

%if %{with python2}
%files -n python-botan
%defattr(644,root,root,755)
%{py_sitedir}/botan2.py[co]
%endif

%if %{with python3}
%files -n python3-botan
%defattr(644,root,root,755)
%{py3_sitedir}/botan2.py
%{py3_sitedir}/__pycache__/botan2.cpython-*.py[co]
%endif
