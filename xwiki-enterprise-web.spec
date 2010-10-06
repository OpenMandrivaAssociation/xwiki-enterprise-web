%define tomcatappsdir  %{_localstatedir}/lib/tomcat5/webapps
%define	appdir	%{tomcatappsdir}/xwiki

Name:		xwiki-enterprise-web
Version:	2.4
Release:	%mkrel 1
License:	LGPLv2.1
Group:		System/Servers
Summary:	A powerful and extensible open-source Wiki engine written in Java
URL:		http://xwiki.org/
Source0:	%{name}-%{version}.war
Source1:	xwiki-pgsql-init.sh
Patch0:		xwiki-enterprise-web-2.3.1-use-system-OOo-server.patch

Requires:	mod_jk mod_ssl tomcat5-webapps python-odconverter
Requires:	postgresql-jdbc
BuildRequires:	java-rpmbuild postgresql-jdbc
BuildArch:	noarch

%description
XWiki Enterprise is a professional wiki with enterprise features such as Blog,
strong rights management, LDAP authentication, PDF export, full skining and
more. It also includes an advanced Form and scripting engine making it a
development environment for data-based applications. It has powerful
extensibility features such as scripting in pages, plugins and a highly modular
architecture.

%prep
%setup -q -c
%patch0 -p1

%build
build-jar-repository WEB-INF/lib postgresql

tee xwiki.conf << EOH
<IfModule jk_module>

<IfModule mod_ssl.c>
  # Make sure that /xwiki is available through https as well
  JkMountCopy All
  # Force https, comment out if not desired
  <LocationMatch /xwiki>
    Options FollowSymLinks
    RewriteEngine on
    RewriteCond %{SERVER_PORT} !^443$
    RewriteRule ^.*$ https://%{SERVER_NAME}%{REQUEST_URI} [L,R]
  </LocationMatch>
</IfModule>

JkMount /xwiki balancer
JkMount /xwiki/* balancer

Alias /xwiki "%{appdir}"
<Directory "%{appdir}">
    Options Indexes FollowSymLinks
</Directory>

</IfModule>
EOH

%install
rm -rf %{buildroot}
install -d %{buildroot}%{appdir}
for i in */ redirect; do
	cp -a $i %{buildroot}%{appdir}
done
touch %{buildroot}%{appdir}/WEB-INF/xwiki.log

install -m644 xwiki.conf -D %{buildroot}%{_webappconfdir}/xwiki.conf
install -m755 %{SOURCE1} -D %{buildroot}%{_bindir}/xwiki-pgsql-install

%posttrans
function randkey () {
	head /dev/urandom|md5sum|cut -d\  -f1
}
VALIDATIONKEY=$(randkey)
ENCRYPTIONKEY=$(randkey)
sed	-e "s#\(xwiki.authentication.validationKey\)=totototototototototototototototo#\1=${VALIDATIONKEY}#g" \
	-e "s#\(xwiki.authentication.encryptionKey\)=titititititititititititititititi#\1=${ENCRYPTIONKEY}#g" \
	-i %{appdir}/WEB-INF/xwiki.cfg

service tomcat5 condrestart
%_post_webapp

%postun
service tomcat5 condrestart
%_postun_webapp

%clean
rm -rf %{buildroot}

%files
%defattr(-,tomcat,tomcat)
%{_bindir}/xwiki-pgsql-install
%config(noreplace) %{_webappconfdir}/xwiki.conf
%dir %{appdir}

%dir %{appdir}/META-INF
%{appdir}/META-INF/*

%{appdir}/redirect

%dir %{appdir}/resources
%{appdir}/resources/*

%dir %{appdir}/skins
%{appdir}/skins/*

%dir %{appdir}/templates
%{appdir}/templates/macros.txt
%{appdir}/templates/*.vm

%dir %{appdir}/WEB-INF
%config(noreplace) %{appdir}/WEB-INF/xwiki.cfg
%config(noreplace) %{appdir}/WEB-INF/*.properties
%config(noreplace) %{appdir}/WEB-INF/*.xml
%ghost %{appdir}/WEB-INF/xwiki.log
%{appdir}/WEB-INF/*.tld

%dir %{appdir}/WEB-INF/cache/ 
%dir %{appdir}/WEB-INF/cache/jbosscache
%config(noreplace) %{appdir}/WEB-INF/cache/jbosscache/*.xml
%dir %{appdir}/WEB-INF/cache/oscache
%config(noreplace) %{appdir}/WEB-INF/cache/oscache/*.properties

%dir %{appdir}/WEB-INF/classes
%{appdir}/WEB-INF/classes/*

%dir %{appdir}/WEB-INF/fonts
%{appdir}/WEB-INF/fonts/*

%dir %{appdir}/WEB-INF/lib
%{appdir}/WEB-INF/lib/*.jar

%dir %{appdir}/WEB-INF/observation
%dir %{appdir}/WEB-INF/observation/remote
%dir %{appdir}/WEB-INF/observation/remote/jgroups
%{appdir}/WEB-INF/observation/remote/jgroups/README.txt

