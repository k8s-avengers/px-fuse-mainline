%global debug_package %{nil}

# Enable building from outside build system
%{!?pxrelease:%define pxrelease 0.0}
%{!?release:%define release 0}
%{!?rpmdescription: %define rpmdescription This package contains %summary.}

Name: %name
Version: %pxrelease
Release: %release
Summary: %summary
Group: PX Runtime Environment
License: Proprietary
Source: %{name}-%{version}-%{release}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Obsoletes: %name
autoreqprov: no

# From mainline linux's mkspec, to convince rpmbuild to not strip the module (and avoid breaking BTF info, if any, and signature, if any)
%define __spec_install_post /usr/lib/rpm/brp-compress || :
%define debug_package %{nil}

%if 0%{?required:1}
Requires: %required
%endif

%if 0%{?required_rpms:1}
BuildRequires: %required_rpms
%endif

%description
  %rpmdescription

%prep
%setup -n %specsrcdir

%build

%if 0%{?kernelpath:1}
export KERNELPATH="%kernelpath"
%endif

%if 0%{?kernelother:1}
export KERNELOTHER="%kernelother"
%endif

autoreconf
./configure
make clean all 

%install
rm -rf $RPM_BUILD_ROOT
INSTALL_MOD_PATH=$RPM_BUILD_ROOT make install

echo "Starting rpm install with KVERSION=${KVERSION}" &>2
LOC=`pwd`
cd $RPM_BUILD_ROOT
# Create file list for rpm install
find . -name px.ko -exec echo \"{}\" \; | sed 's/^"\./"/' > $LOC/%{name}.files
cp -a $LOC/%{name}.files .
echo /%{name}.files >> $LOC/%{name}.files
MDIR=$(cat $LOC/%{name}.files | /bin/egrep px.ko | /bin/sed -e 's/\/extra\/.*//' -e 's/"//g' -e 's/^\/lib/lib/' | /usr/bin/tr -d '[:space:]')
[ -d "${MDIR}" ] && for fl in $(ls ${MDIR}/*); do [ ! -d ${fl} ] && /bin/rm -f ${fl}; done
cd -

%check

%clean
/bin/rm -rf $RPM_BUILD_ROOT

%files -f %{name}.files
%defattr(-,root,root,0755)

%pre

%post

if [ -e /%{name}.files ]; then
   TARGET_KERNEL_MODULES_DIR=$(cat "/%{name}.files" | grep "\/lib\/modules" | head -1 | cut -d '"' -f 2 | cut -d "/" -f 4) # ewww...
   echo "Running depmod against '${TARGET_KERNEL_MODULES_DIR}' for px module..."
   depmod "${TARGET_KERNEL_MODULES_DIR}" || echo "depmod failed for px module against '${TARGET_KERNEL_MODULES_DIR}'" &>2 
fi

%postun
echo 'post uninstall for px module, doing nothing.' &>2

%preun
echo 'pre uninstall for px module, doing nothing.' &>2


%changelog
* Sat Jan 16 2016 jvinod
- Initial spec file creation
