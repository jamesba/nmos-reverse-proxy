Name: nmosreverseproxy
Version: 0.1.0
Release: 2%{?dist}
License: Apache 2
Summary: Common reverse proxy config for IP Studio web services

Source0: nmosreverseproxy-%{version}.tar.gz
Source1: nmos-reverseproxy-common.conf
Source2: nmos-reverse-proxy.service
Source3: nmos-reverse-proxy.conf

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:      noarch

BuildRequires:	python2-devel
BuildRequires:  python-setuptools
BuildRequires:  httpd-devel
BuildRequires:  python-ipppython
BuildRequires:  systemd

Requires:       python
Requires:       python-setuptools
Requires:       httpd
Requires:       httpd-devel
Requires:       mod_proxy_html
Requires:       libxml2-devel
Requires:       nmoscommon
%{?systemd_requires}

%description
%{summary}

%prep
%setup

%build
%{py2_build}

%install
%{py2_install}

mkdir -p %{buildroot}/%{_sysconfdir}/httpd/conf.d
mkdir -p %{buildroot}/%{_sysconfdir}/httpd/conf.d/nmos-apis
cp %{SOURCE1} %{buildroot}/%{_sysconfdir}/httpd/conf.d/nmos-reverseproxy-common.conf

mkdir -p %{buildroot}/%{_unitdir}
cp %{SOURCE2} %{buildroot}/%{_unitdir}/nmos-reverse-proxy.service

mkdir -p %{buildroot}/%{_sysconfdir}/init
cp %{SOURCE3} %{buildroot}/%{_sysconfdir}/init/nmos-reverse-proxy.conf

%post
systemctl daemon-reload
systemctl restart nmos-reverse-proxy || true
systemctl restart httpd || true

%preun
systemctl stop nmos-reverse-proxy || true

%clean
rm -rf %{buildroot}

%files
%{_bindir}/

%{python2_sitelib}/nmosreverseproxy
%{python2_sitelib}/nmosreverseproxy-%{version}*.egg-info

%config %{_sysconfdir}/httpd/conf.d/nmos-reverseproxy-common.conf
%config %{_sysconfdir}/httpd/conf.d/nmos-apis
%config %{_sysconfdir}/init/nmos-reverse-proxy.conf

%{_unitdir}/nmos-reverse-proxy.service

%changelog
* Mon Nov 13 2017 Simon Rankine <simon.rankine@bbc.co.uk> - 0.1.0-3
- Transition to open source NMOS version

* Thu Apr 27 2017 Sam Nicholson <sam.nicholson@bbc.co.uk> - 0.1.0-2
- Fix problem with proxylisting service using Ubuntu directories

* Thu Apr 13 2017 Sam Nicholson <sam.nicholson@bbc.co.uk> - 0.1.0-1
- Initial specfile
