%define with_signmodules  0
%define with_kabichk 0

# Default without toolchain_clang
%bcond_with toolchain_clang

%if %{with toolchain_clang}
%global toolchain clang
%endif

%bcond_with clang_lto

%if %{with clang_lto} && "%{toolchain}" != "clang"
{error:clang_lto requires --with toolchain_clang}
%endif

%define modsign_cmd %{SOURCE10}

%if 0%{?openEuler_sign_rsa}
# Use the open-source signature when the EBS permission is insufficient.
# Now only the admin user in EBS can send the signature request. But the
# user triggering the acces control build task and the personal build
# task is non-admin. Inorder to avoid build failures caused by failed
# signing, use the open-source signature.
# The flag_openEuler_has_sign_perm used in the rpm execution phase
# The openEuler_has_sign_perm used in the rpm execution phase

%define openEuler_check_EBS_perm openEuler_has_sign_perm=0 \
echo "" >> test_openEuler_sign.ko \
sh /usr/lib/rpm/brp-ebs-sign --module test_openEuler_sign.ko || \
[ $? -ne 2 ] && openEuler_has_sign_perm=1 \
%global flag_openEuler_has_sign_perm $openEuler_has_sign_perm \
rm -f test_openEuler_sign.ko test_openEuler_sign.ko.sig
%endif

%global Arch $(echo %{_host_cpu} | sed -e s/i.86/x86/ -e s/x86_64/x86/ -e s/aarch64.*/arm64/ -e s/riscv.*/riscv/ -e s/powerpc64le/powerpc/ -e s/loongarch64/loongarch/)

%global KernelVer %{version}-%{release}.%{_target_cpu}
%global debuginfodir /usr/lib/debug

%global upstream_version    6.12
%global upstream_sublevel   13
%global devel_release       0
%global maintenance_release .0.0
%global pkg_release         .0

%global openeuler_lts       1
%global openeuler_major     2403
%global openeuler_minor     0

#
# Support input parameter to overwrite the preceding version numbers.
#

%bcond_with openeuler_version

%if %{with openeuler_version}
%global openeuler_lts       %{?_openeuler_lts}   %{?!_openeuler_lts: 0}
%global openeuler_major     %{?_openeuler_major} %{?!_openeuler_major: 0}
%global openeuler_minor     %{?_openeuler_minor} %{?!_openeuler_minor: 0}
%endif

%define with_debuginfo 1
# Do not recompute the build-id of vmlinux in find-debuginfo.sh
%global _missing_build_ids_terminate_build 1
%global _no_recompute_build_ids 1
%undefine _include_minidebuginfo
%undefine _include_gdb_index
%undefine _unique_build_ids

%define with_source 1

%define with_python2 0

# failed if there is new config options
%define listnewconfig_fail 0

%ifarch aarch64
%define with_64kb  %{?_with_64kb: 1} %{?!_with_64kb: 0}
%if %{with_64kb}
%global package64kb -64kb
%define with_kabichk 0
%endif
%else
%define with_64kb  0
%endif

#default is enabled. You can disable it with --without option
%define with_perf    %{?_without_perf: 0} %{?!_without_perf: 1}

Name:	 kernel%{?package64kb}
Version: %{upstream_version}.%{upstream_sublevel}
Release: %{devel_release}%{?maintenance_release}%{?pkg_release}
Summary: Linux Kernel
License: GPLv2
URL:	 http://www.kernel.org/
Source0: kernel.tar.gz
Source10: sign-modules
Source11: x509.genkey
Source12: extra_certificates

%if 0%{?openEuler_sign_rsa}
Source15: openeuler_kernel_cert.cer
Source16: sign-modules-openeuler
%endif

%if 0%{?with_kabichk}
Source18: check-kabi
Source20: Module.kabi_aarch64
Source21: Module.kabi_x86_64
Source22: Module.kabi_ext1_aarch64
Source23: Module.kabi_ext1_x86_64
Source24: Module.kabi_ext2_aarch64
Source25: Module.kabi_ext2_x86_64
%endif

Source200: mkgrub-menu-aarch64.sh

Source2000: cpupower.service
Source2001: cpupower.config

%if 0%{?with_patch}
Source9000: apply-patches
Source9001: guards
Source9002: series.conf
Source9998: patches.tar.bz2
%endif

#BuildRequires:
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, tar
BuildRequires: bzip2, xz, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: libcap-devel, libcap-ng-devel, rsync
BuildRequires: gcc >= 3.4.2, binutils >= 2.12
BuildRequires: hostname, net-tools, bc
BuildRequires: xmlto, asciidoc
BuildRequires: openssl-devel openssl
BuildRequires: hmaccalc
BuildRequires: ncurses-devel
#BuildRequires: pesign >= 0.109-4
BuildRequires: elfutils-libelf-devel
BuildRequires: rpm >= 4.14.2
#BuildRequires: sparse >= 0.4.1
%if 0%{?with_python2}
BuildRequires: python-devel
%endif

BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel perl(ExtUtils::Embed) bison
BuildRequires: audit-libs-devel libpfm-devel libtraceevent-devel
BuildRequires: pciutils-devel gettext
BuildRequires: rpm-build, elfutils
BuildRequires: numactl-devel python3-devel glibc-static python3-docutils
BuildRequires: perl-generators perl(Carp) libunwind-devel gtk2-devel libbabeltrace-devel java-1.8.0-openjdk java-1.8.0-openjdk-devel perl-devel

AutoReq: no
AutoProv: yes

Conflicts: device-mapper-libs < 1.02.63-2 e2fsprogs < 1.37-4 initscripts < 7.23 iptables < 1.3.2-1
Conflicts: ipw2200-firmware < 2.4 isdn4k-utils < 3.2-32 iwl4965-firmware < 228.57.2 jfsutils < 1.1.7-2
Conflicts: mdadm < 3.2.1-5 nfs-utils < 1.0.7-12 oprofile < 0.9.1-2 ppp < 2.4.3-3 procps < 3.2.5-6.3
Conflicts: reiserfs-utils < 3.6.19-2 selinux-policy-targeted < 1.25.3-14 squashfs-tools < 4.0
Conflicts: udev < 063-6 util-linux < 2.12 wireless-tools < 29-3 xfsprogs < 2.6.13-4

Provides: kernel-%{_target_cpu} = %{version}-%{release} kernel-drm = 4.3.0 kernel-drm-nouveau = 16 kernel-modeset = 1
Provides: kernel-uname-r = %{KernelVer} kernel=%{KernelVer}

Requires: dracut >= 001-7 grubby >= 8.28-2 initscripts >= 8.11.1-1 linux-firmware >= 20100806-2 module-init-tools >= 3.16-2

ExclusiveArch: noarch aarch64 i686 x86_64 riscv64 ppc64le loongarch64
ExclusiveOS: Linux

%if %{with_perf}
BuildRequires: flex xz-devel libzstd-devel
BuildRequires: java-devel
%ifarch aarch64
BuildRequires: OpenCSD
%endif
%endif

BuildRequires: dwarves
BuildRequires: clang >= 10.0.0
BuildRequires: llvm
BuildRequires: llvm-devel
%if %{with clang_lto}
BuildRequires: lld
%endif

%description
The Linux Kernel, the operating system core itself.

%package headers
Summary: Header files for the Linux kernel for use by glibc
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.


%package devel
Summary: Development package for building kernel modules to match the %{KernelVer} kernel
AutoReqProv: no
Provides: kernel-devel-uname-r = %{KernelVer}
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}
Requires: perl findutils

%description devel
This package provides kernel headers and makefiles sufficient to build modules
against the %{KernelVer} kernel package.

%package tools
Summary: Assortment of tools for the Linux kernel
Provides: %{name}-tools-libs
Obsoletes: %{name}-tools-libs
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
%description tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package tools-devel
Summary: Assortment of tools for the Linux kernel
Requires: %{name}-tools = %{version}-%{release}
Requires: %{name}-tools-libs = %{version}-%{release}
Provides: %{name}-tools-libs-devel = %{version}-%{release}
Obsoletes: %{name}-tools-libs-devel
%description tools-devel
This package contains the development files for the tools/ directory from
the kernel source.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%if 0%{?with_python2}
%package -n python2-perf
Provides: python-perf = %{version}-%{release}
Obsoletes: python-perf
Summary: Python bindings for apps which will manipulate perf events

%description -n python2-perf
A Python module that permits applications written in the Python programming
language to use the interface to manipulate perf events.
%endif

%package -n python3-perf
Summary: Python bindings for apps which will manipulate perf events
%description -n python3-perf
A Python module that permits applications written in the Python programming
language to use the interface to manipulate perf events.
# with_perf
%endif

%package -n bpftool
Summary: Inspection and simple manipulation of eBPF programs and maps
%description -n bpftool
This package contains the bpftool, which allows inspection and simple
manipulation of eBPF programs and maps.

%package source
Summary: the kernel source
%description source
This package contains vaious source files from the kernel.

%if 0%{?with_debuginfo}
%define _debuginfo_template %{nil}
%define _debuginfo_subpackages 0

%define debuginfo_template(n:) \
%package -n %{-n*}-debuginfo\
Summary: Debug information for package %{-n*}\
Group: Development/Debug\
AutoReq: 0\
AutoProv: 1\
%description -n %{-n*}-debuginfo\
This package provides debug information for package %{-n*}.\
Debug information is useful when developing applications that use this\
package or when debugging this package.\
%{nil}

%debuginfo_template -n kernel
%files -n kernel-debuginfo -f kernel-debugfiles.list -f debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} --keep-section '.BTF' -p '.*/%{KernelVer}/.*|.*/vmlinux|XXX' -o kernel-debugfiles.list}

%debuginfo_template -n bpftool
%files -n bpftool-debuginfo -f bpftool-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{_sbindir}/bpftool.*(\.debug)?|XXX' -o bpftool-debugfiles.list}

%debuginfo_template -n kernel-tools
%files -n kernel-tools-debuginfo -f kernel-tools-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{_bindir}/centrino-decode.*(\.debug)?|.*%{_bindir}/powernow-k8-decode.*(\.debug)?|.*%{_bindir}/cpupower.*(\.debug)?|.*%{_libdir}/libcpupower.*|.*%{_libdir}/libcpupower.*|.*%{_bindir}/turbostat.(\.debug)?|.*%{_bindir}/.*gpio.*(\.debug)?|.*%{_bindir}/.*iio.*(\.debug)?|.*%{_bindir}/tmon.*(.debug)?|XXX' -o kernel-tools-debugfiles.list}

%if %{with_perf}
%debuginfo_template -n perf
%files -n perf-debuginfo -f perf-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{_bindir}/perf.*(\.debug)?|.*%{_libexecdir}/perf-core/.*|.*%{_libdir}/traceevent/.*|XXX' -o perf-debugfiles.list}

%if 0%{?with_python2}
%debuginfo_template -n python2-perf
%files -n python2-perf-debuginfo -f python2-perf-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{python2_sitearch}/perf.*(.debug)?|XXX' -o python2-perf-debugfiles.list}
%endif

%debuginfo_template -n python3-perf
%files -n python3-perf-debuginfo -f python3-perf-debugfiles.list
%{expand:%%global _find_debuginfo_opts %{?_find_debuginfo_opts} -p '.*%{python3_sitearch}/perf.*(.debug)?|XXX' -o python3-perf-debugfiles.list}
#with_perf
%endif

%endif

%prep
%setup -q -n kernel-%{version} -c

%if 0%{?with_patch}
tar -xjf %{SOURCE9998}
%endif

mv kernel linux-%{KernelVer}
cd linux-%{KernelVer}

%if 0%{?with_patch}
cp %{SOURCE9000} .
cp %{SOURCE9001} .
cp %{SOURCE9002} .

if [ ! -d patches ];then
    mv ../patches .
fi

Applypatches()
{
    set -e
    set -o pipefail
    local SERIESCONF=$1
    local PATCH_DIR=$2
    sed -i '/^#/d'  $SERIESCONF
    sed -i '/^[\s]*$/d' $SERIESCONF
    (
        echo "trap 'echo \"*** patch \$_ failed ***\"' ERR"
        echo "set -ex"
        cat $SERIESCONF | \
        sed "s!^!patch -s -F0 -E -p1 --no-backup-if-mismatch -i $PATCH_DIR/!" \
    ) | sh
}

Applypatches series.conf %{_builddir}/kernel-%{version}/linux-%{KernelVer}
%endif

%if "%toolchain" == "clang"
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1
%endif

find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null
find . -name .gitignore -exec rm -f {} \; >/dev/null

%if 0%{?with_signmodules}
    cp %{SOURCE11} certs/.
%endif

%if 0%{?with_source}
# Copy directory backup for kernel-source
cp -a ../linux-%{KernelVer} ../linux-%{KernelVer}-source
find ../linux-%{KernelVer}-source -type f -name "\.*" -exec rm -rf {} \; >/dev/null
%endif

cp -a tools/perf tools/python3-perf

%build
cd linux-%{KernelVer}

perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}/" Makefile
perl -p -i -e "s/^OPENEULER_LTS.*/OPENEULER_LTS = %{openeuler_lts}/" Makefile.oever
perl -p -i -e "s/^OPENEULER_MAJOR.*/OPENEULER_MAJOR = %{openeuler_major}/" Makefile.oever
perl -p -i -e "s/^OPENEULER_MINOR.*/OPENEULER_MINOR = %{openeuler_minor}/" Makefile.oever
perl -p -i -e "s/^OPENEULER_RELEASE.*/OPENEULER_RELEASE = \"%{release}\"/" Makefile.oever

## make linux
make mrproper %{_smp_mflags}

%if %{with_64kb}
sed -i arch/arm64/configs/sophgo_sg2044_openeuler_defconfig -e 's/^CONFIG_ARM64_4K_PAGES.*/CONFIG_ARM64_64K_PAGES=y/'
sed -i arch/arm64/configs/sophgo_sg2044_openeuler_defconfig -e 's/^CONFIG_ARM64_PA_BITS=.*/CONFIG_ARM64_PA_BITS=52/'
sed -i arch/arm64/configs/sophgo_sg2044_openeuler_defconfig -e 's/^CONFIG_ARM64_PA_BITS_.*/CONFIG_ARM64_PA_BITS_52=y/'
sed -i arch/arm64/configs/sophgo_sg2044_openeuler_defconfig -e 's/^CONFIG_ARM64_VA_BITS=.*/CONFIG_ARM64_VA_BITS=52/'
sed -i arch/arm64/configs/sophgo_sg2044_openeuler_defconfig -e 's/^CONFIG_ARM64_VA_BITS_.*/CONFIG_ARM64_VA_BITS_52=y/'
%endif

%if "%toolchain" == "clang"

%ifarch s390x ppc64le
%global llvm_ias 0
%else
%global llvm_ias 1
%endif

%global clang_make_opts HOSTCC=clang CC=clang LLVM_IAS=%{llvm_ias}

%if %{with clang_lto}
%global clang_make_opts %{clang_make_opts} HOSTLD=ld.lld LD=ld.lld AR=llvm-ar NM=llvm-nm HOSTAR=llvm-ar HOSTNM=llvm-nm
%endif

%endif

%global make %{__make} %{?clang_make_opts} HOSTCFLAGS="%{?build_cflags}" HOSTLDFLAGS="%{?build_ldflags}"

%ifarch loongarch64

%if 0%{with_signmodules}
echo "CONFIG_MODULE_SIG=y" >>arch/loongarch/configs/loongson3_defconfig
%endif

%if 0%{with_debuginfo}
echo "CONFIG_DEBUG_INFO=y" >>arch/loongarch/configs/loongson3_defconfig
%endif

make ARCH=%{Arch} loongson3_defconfig

%else
%{make} ARCH=%{Arch} sophgo_sg2044_openeuler_defconfig
%endif

%if %{with clang_lto}
scripts/config -e LTO_CLANG_FULL
sed -i 's/# CONFIG_LTO_CLANG_FULL is not set/CONFIG_LTO_CLANG_FULL=y/' .config
sed -i 's/CONFIG_LTO_NONE=y/# CONFIG_LTO_NONE is not set/' .config
%endif

%if 0%{?openEuler_sign_rsa}
    %{openEuler_check_EBS_perm}
    if [ $openEuler_has_sign_perm -eq 1 ]; then
        cp %{SOURCE15} ./certs/openeuler-cert.pem
    # close kernel native signature
        sed -i 's/CONFIG_MODULE_SIG_KEY=.*$/CONFIG_MODULE_SIG_KEY=""/g' .config
        sed -i 's/CONFIG_SYSTEM_TRUSTED_KEYS=.*$/CONFIG_SYSTEM_TRUSTED_KEYS="certs\/openeuler-cert.pem"/g' .config
        sed -i 's/CONFIG_MODULE_SIG_ALL=y$/CONFIG_MODULE_SIG_ALL=n/g' .config
    fi
%endif

TargetImage=$(basename $(make -s image_name))

%{make} ARCH=%{Arch} $TargetImage %{?_smp_mflags}
%{make} ARCH=%{Arch} modules %{?_smp_mflags}

%if 0%{?with_kabichk}
    chmod 0755 %{SOURCE18}
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu} ]; then
        %{SOURCE18} -k $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu} -s Module.symvers || exit 1
        %{SOURCE18} -k $RPM_SOURCE_DIR/Module.kabi_ext1_%{_target_cpu} -s Module.symvers || exit 1
        %{SOURCE18} -k $RPM_SOURCE_DIR/Module.kabi_ext2_%{_target_cpu} -s Module.symvers || exit 1
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif

## make tools
%if %{with_perf}
# perf
%ifarch aarch64
# aarch64 make perf with CORESIGHT=1
%global perf_make \
    make %{?clang_make_opts} EXTRA_LDFLAGS="%[ "%{toolchain}" == "clang" ? "-z now" : "" ]" EXTRA_CFLAGS="%[ "%{toolchain}" == "clang" ? "" : "-Wl,-z,now" ] -g -Wall -fstack-protector-strong -fPIC" EXTRA_PERFLIBS="-fpie -pie" %{?_smp_mflags} -s V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_LIBNUMA=1 NO_STRLCPY=1 CORESIGHT=1 prefix=%{_prefix}
%else
%global perf_make \
    make %{?clang_make_opts} EXTRA_LDFLAGS="%[ "%{toolchain}" == "clang" ? "-z now" : "" ]" EXTRA_CFLAGS="%[ "%{toolchain}" == "clang" ? "" : "" ] -g -Wall -fstack-protector-strong" EXTRA_PERFLIBS="" %{?_smp_mflags} -s V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_LIBNUMA=1 NO_STRLCPY=1 prefix=%{_prefix}
%endif
%if 0%{?with_python2}
%global perf_python2 -C tools/perf PYTHON=%{__python2}
%global perf_python3 -C tools/python3-perf PYTHON=%{__python3}
%else
%global perf_python3 -C tools/perf PYTHON=%{__python3}
%endif

chmod +x tools/perf/check-headers.sh
# perf
%if 0%{?with_python2}
%{perf_make} %{perf_python2} all
%endif

# make sure check-headers.sh is executable
chmod +x tools/python3-perf/check-headers.sh
%{perf_make} %{perf_python3} all

pushd tools/perf/Documentation/
%{make} %{?_smp_mflags} man
popd
%endif

# bpftool
pushd tools/bpf/bpftool
%{make} %{?_smp_mflags}
popd

# cpupower
chmod +x tools/power/cpupower/utils/version-gen.sh
%{make} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    %{make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    %{make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch %{ix86} x86_64
    pushd tools/power/x86/x86_energy_perf_policy/
    %{make}
    popd
    pushd tools/power/x86/turbostat
    %{make}
    popd
%endif
# thermal
pushd tools/thermal/tmon/
%{make}
popd
# iio
pushd tools/iio/
%{make}
popd
# gpio
pushd tools/gpio/
%{make}
popd
# kvm
pushd tools/kvm/kvm_stat/
%{make} %{?_smp_mflags} man
popd
# libbpf.a and bpf_helper_defs.h
pushd tools/lib/bpf
%{make}
popd

%install
%if 0%{?with_source}
    %define _python_bytecompile_errors_terminate_build 0
    mkdir -p $RPM_BUILD_ROOT/usr/src/
    mv linux-%{KernelVer}-source $RPM_BUILD_ROOT/usr/src/linux-%{KernelVer}
    cp linux-%{KernelVer}/.config $RPM_BUILD_ROOT/usr/src/linux-%{KernelVer}/
%endif

cd linux-%{KernelVer}

## install linux

# deal with kernel-source, now we don't need kernel-source
#mkdir $RPM_BUILD_ROOT/usr/src/linux-%{KernelVer}
#tar cf - --exclude SCCS --exclude BitKeeper --exclude .svn --exclude CVS --exclude .pc --exclude .hg --exclude .git --exclude=.tmp_versions --exclude=*vmlinux* --exclude=*.o --exclude=*.ko --exclude=*.cmd --exclude=Documentation --exclude=.config.old --exclude=.missing-syscalls.d --exclude=patches . | tar xf - -C %{buildroot}/usr/src/linux-%{KernelVer}

mkdir -p $RPM_BUILD_ROOT/boot
dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-%{KernelVer}.img bs=1M count=20

%ifarch loongarch64
strip -s vmlinux -o vmlinux.elf
install -m 755 vmlinux.elf $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}
%else
install -m 755 $(make -s image_name) $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}
%endif

%if 0%{?openEuler_sign_rsa}
    %{openEuler_check_EBS_perm}
    if [ $openEuler_has_sign_perm -eq 1 ]; then
        echo "start sign"
        %ifarch %arm aarch64
	    gunzip -c $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}>$RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi
	    sh /usr/lib/rpm/brp-ebs-sign --efi $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi.sig $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip.efi $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip
	    gzip -c $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip>$RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}
	    rm -f $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.unzip
        %endif
        %ifarch x86_64
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer} $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi
	    sh /usr/lib/rpm/brp-ebs-sign --efi $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi.sig $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi
	    mv $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}.efi $RPM_BUILD_ROOT/boot/vmlinuz-%{KernelVer}
        %endif
    fi
%endif

pushd $RPM_BUILD_ROOT/boot
sha512hmac ./vmlinuz-%{KernelVer} >./.vmlinuz-%{KernelVer}.hmac
popd

install -m 644 .config $RPM_BUILD_ROOT/boot/config-%{KernelVer}
install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-%{KernelVer}

gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-%{KernelVer}.gz

mkdir -p $RPM_BUILD_ROOT%{_sbindir}


%if 0%{?with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/%{KernelVer}
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/%{KernelVer}
%endif

# deal with module, if not kdump
%{make} ARCH=%{Arch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=%{KernelVer} mod-fw=
######## to collect ko to module.filelist about netwoking. block. drm. modesetting ###############
pushd $RPM_BUILD_ROOT/lib/modules/%{KernelVer}
find -type f -name "*.ko" >modnames

# mark modules executable so that strip-to-file can strip them
xargs --no-run-if-empty chmod u+x < modnames

# Generate a list of modules for block and networking.

grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

collect_modules_list()
{
    sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
    LC_ALL=C sort -u > modules.$1
    if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i modules.$1
    fi
}

collect_modules_list networking \
			 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt2x00(pci|usb)_probe|register_netdevice'
collect_modules_list block \
		 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size|ahci_platform_get_resources' 'pktcdvd.ko|dm-mod.ko'
collect_modules_list drm \
			 'drm_open|drm_init'
collect_modules_list modesetting \
			 'drm_crtc_init'

# detect missing or incorrect license tags
rm -f modinfo
while read i
do
    echo -n "$i " >> modinfo
    /sbin/modinfo -l $i >> modinfo
done < modnames

grep -E -v \
	  'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
  modinfo && exit 1

rm -f modinfo modnames drivers.undef

for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
do
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
done
popd
# modsign module ko;need after find-debuginfo,strip
%define __modsign_install_post \
    if [ "%{with_signmodules}" -eq "1" ];then \
        cp certs/signing_key.pem . \
        cp certs/signing_key.x509 . \
        chmod 0755 %{modsign_cmd} \
        %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KernelVer} || exit 1 \
    fi \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs -n1 -P`nproc --all` xz; \
%{nil}

%if 0%{?openEuler_sign_rsa}
%define __modsign_install_post \
    if [ "%{with_signmodules}" -eq "1" ];then \
        if [ %flag_openEuler_has_sign_perm -eq 1 ]; then \
            sh %{SOURCE16} $RPM_BUILD_ROOT/lib/modules/%{KernelVer} || exit 1 \
        else \
            cp certs/signing_key.pem . \
            cp certs/signing_key.x509 . \
            chmod 0755 %{modsign_cmd} \
            %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KernelVer} || exit 1 \
        fi \
    fi \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs -n1 -P`nproc --all` xz; \
%{nil}
%endif

# deal with header
%{make} ARCH=%{Arch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr KBUILD_SRC= headers_install
find $RPM_BUILD_ROOT/usr/include -name "\.*"  -exec rm -rf {} \;

# deal with vdso
%ifnarch ppc64le
%{make} -s ARCH=%{Arch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=%{KernelVer}
%endif
if [ ! -s ldconfig-kernel.conf ]; then
    echo "# Placeholder file, no vDSO hwcap entries used in this kernel." >ldconfig-kernel.conf
fi
install -D -m 444 ldconfig-kernel.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-%{KernelVer}.conf

# deal with /lib/module/ path- sub path: build source kernel
rm -f $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build
rm -f $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/source
mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build
mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/extra
mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/updates
mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/weak-updates
############ to do collect devel file  #########
# 1. Makefile And Kconfig, .config sysmbol
# 2. scrpits dir
# 3. .h file
find -type f \( -name "Makefile*" -o -name "Kconfig*" \) -exec cp --parents {} $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build \;
for f in Module.symvers System.map Module.markers .config;do
    test -f $f || continue
    cp $f $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build
done

cp -a scripts $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build
if [ -d arch/%{Arch}/scripts ]; then
    cp -a arch/%{Arch}/scripts $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/arch/%{_arch} || :
fi
if [ -f arch/%{Arch}/*lds ]; then
    cp -a arch/%{Arch}/*lds $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/arch/%{_arch}/ || :
fi
find $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/scripts/ -name "*.o" -exec rm -rf {} \;

if [ -d arch/%{Arch}/include ]; then
    cp -a --parents arch/%{Arch}/include $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/
fi
cp -a include $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include

if [ -f arch/%{Arch}/kernel/module.lds ]; then
    cp -a --parents arch/%{Arch}/kernel/module.lds $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/
fi

# module.lds is moved to scripts by commit 596b0474d3d9 in linux 5.10.
if [ -f scripts/module.lds ]; then
    cp -a --parents scripts/module.lds $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/
fi

%ifarch aarch64
    cp -a --parents arch/arm/include/asm $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/
%endif

# copy objtool for kernel-devel (needed for building external modules)
if grep -q CONFIG_OBJTOOL=y .config; then
    mkdir -p $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/tools/objtool
    cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/tools/objtool
fi

# Make sure the Makefile and version.h have a matching timestamp so that
# external modules can be built
touch -r $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include/generated/uapi/linux/version.h
touch -r $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/.config $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include/generated/autoconf.h
# for make prepare
if [ ! -f $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include/config/auto.conf ];then
    cp .config $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build/include/config/auto.conf
fi

mkdir -p %{buildroot}/usr/src/kernels
mv $RPM_BUILD_ROOT/lib/modules/%{KernelVer}/build $RPM_BUILD_ROOT/usr/src/kernels/%{KernelVer}

find $RPM_BUILD_ROOT/usr/src/kernels/%{KernelVer} -name ".*.cmd" -exec rm -f {} \;

pushd $RPM_BUILD_ROOT/lib/modules/%{KernelVer}
ln -sf /usr/src/kernels/%{KernelVer} build
ln -sf build source
popd


# deal with doc , now we don't need


# deal with kernel abi whitelists. now we don't need


## install tools
%if %{with_perf}
# perf
# perf tool binary and supporting scripts/binaries
%if 0%{?with_python2}
%{perf_make} %{perf_python2} DESTDIR=%{buildroot} lib=%{_lib} install-bin
%else
%{perf_make} %{perf_python3} DESTDIR=%{buildroot} lib=%{_lib} install-bin
%endif
# remove the 'trace' symlink.
rm -f %{buildroot}%{_bindir}/trace

# remove examples
rm -rf %{buildroot}/usr/lib/perf/examples
# remove the stray header file that somehow got packaged in examples
rm -rf %{buildroot}/usr/lib/perf/include/bpf/

# python-perf extension
%{perf_make} %{perf_python3} DESTDIR=%{buildroot} install-python_ext
%if 0%{?with_python2}
%{perf_make} %{perf_python2} DESTDIR=%{buildroot} install-python_ext
%endif

# perf man pages (note: implicit rpm magic compresses them later)
install -d %{buildroot}/%{_mandir}/man1
install -pm0644 tools/kvm/kvm_stat/kvm_stat.1 %{buildroot}/%{_mandir}/man1/
install -pm0644 tools/perf/Documentation/*.1 %{buildroot}/%{_mandir}/man1/
%endif

# bpftool
pushd tools/bpf/bpftool
%{make} DESTDIR=%{buildroot} prefix=%{_prefix} bash_compdir=%{_sysconfdir}/bash_completion.d/ mandir=%{_mandir} install doc-install
popd

# resolve_btfids
mkdir -p %{buildroot}/usr/src/kernels/%{KernelVer}/tools/bpf/resolve_btfids
cp tools/bpf/resolve_btfids/resolve_btfids %{buildroot}/usr/src/kernels/%{KernelVer}/tools/bpf/resolve_btfids

# cpupower
%{make} -C tools/power/cpupower DESTDIR=%{buildroot} libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
    mkdir -p %{buildroot}%{_mandir}/man8
    pushd tools/power/x86/x86_energy_perf_policy
    %{make} DESTDIR=%{buildroot} install
    popd
    pushd tools/power/x86/turbostat
    %{make} DESTDIR=%{buildroot} install
    popd
%endif
# thermal
pushd tools/thermal/tmon
%{make} INSTALL_ROOT=%{buildroot} install
popd
# iio
pushd tools/iio
%{make} DESTDIR=%{buildroot} install
popd
# gpio
pushd tools/gpio
%{make} DESTDIR=%{buildroot} install
popd
# kvm
pushd tools/kvm/kvm_stat
%{make} INSTALL_ROOT=%{buildroot} install-tools
popd

%define __spec_install_post\
%{?__debug_package:%{__debug_install_post}}\
%{__arch_install_post}\
%{__os_install_post}\
%{__modsign_install_post}\
%{nil}

%post
%{_sbindir}/new-kernel-pkg --package kernel --install %{KernelVer} || exit $?

%preun
if [ `uname -i` == "aarch64" ] &&
        [ -f /boot/EFI/grub2/grub.cfg ]; then
    /usr/bin/sh  %{_sbindir}/mkgrub-menu-%{version}-%{devel_release}%{?maintenance_release}%{?pkg_release}.sh %{version}-%{release}.aarch64  /boot/EFI/grub2/grub.cfg  remove
fi

%postun
%{_sbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{KernelVer} || exit $?
if [ -x %{_sbindir}/weak-modules ]
then
    %{_sbindir}/weak-modules --remove-kernel %{KernelVer} || exit $?
fi

# remove empty directory
if [ -d /lib/modules/%{KernelVer} ] && [ "`ls -A  /lib/modules/%{KernelVer}`" = "" ]; then
    rm -rf /lib/modules/%{KernelVer}
fi
if [ `uname -i` == "loongarch64" ] || [ `uname -i` == "riscv64" ] ;then
	[ -f /etc/grub2.cfg ] && GRUB_CFG=`readlink -f /etc/grub2.cfg`
	[ "x${GRUB_CFG}" == "x" ] && [ -f /etc/grub2-efi.cfg ] && GRUB_CFG=`readlink -f /etc/grub2-efi.cfg`
	[ "x${GRUB_CFG}" == "x" ] && [ -f /boot/efi/EFI/openEuler/grub.cfg ] && GRUB_CFG=/boot/efi/EFI/openEuler/grub.cfg
	[ "x${GRUB_CFG}" != "x" ] && grub2-mkconfig -o ${GRUB_CFG}
fi

%posttrans
%{_sbindir}/new-kernel-pkg --package kernel --mkinitrd --dracut --depmod --update %{KernelVer} || exit $?
%{_sbindir}/new-kernel-pkg --package kernel --rpmposttrans %{KernelVer} || exit $?
if [ `uname -i` == "aarch64" ] &&
        [ -f /boot/EFI/grub2/grub.cfg ]; then
	/usr/bin/sh %{_sbindir}/mkgrub-menu-%{version}-%{devel_release}%{?maintenance_release}%{?pkg_release}.sh %{version}-%{release}.aarch64  /boot/EFI/grub2/grub.cfg  update
fi
if [ `uname -i` == "loongarch64" ] || [ `uname -i` == "riscv64" ] ;then
	[ -f /etc/grub2.cfg ] && GRUB_CFG=`readlink -f /etc/grub2.cfg`
	[ "x${GRUB_CFG}" == "x" ] && [ -f /etc/grub2-efi.cfg ] && GRUB_CFG=`readlink -f /etc/grub2-efi.cfg`
	[ "x${GRUB_CFG}" == "x" ] && [ -f /boot/efi/EFI/openEuler/grub.cfg ] && GRUB_CFG=/boot/efi/EFI/openEuler/grub.cfg
	[ "x${GRUB_CFG}" != "x" ] && grub2-mkconfig -o ${GRUB_CFG}
	grubby --set-default=/boot/vmlinuz-%{KernelVer}
fi
if [ -x %{_sbindir}/weak-modules ]
then
    %{_sbindir}/weak-modules --add-kernel %{KernelVer} || exit $?
fi
%{_sbindir}/new-kernel-pkg --package kernel --mkinitrd --dracut --depmod --update %{KernelVer} || exit $?
%{_sbindir}/new-kernel-pkg --package kernel --rpmposttrans %{KernelVer} || exit $?

%post devel
if [ -f /etc/sysconfig/kernel ]
then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]
then
    (cd /usr/src/kernels/%{KernelVer} &&
     /usr/bin/find . -type f | while read f; do
       hardlink -c /usr/src/kernels/*.oe*.*/$f $f
     done)
fi

%post -n %{name}-tools
/sbin/ldconfig
%systemd_post cpupower.service

%preun -n %{name}-tools
%systemd_preun cpupower.service

%postun -n %{name}-tools
/sbin/ldconfig
%systemd_postun cpupower.service

%files
%defattr (-, root, root)
%doc
/boot/config-*
/boot/symvers-*
/boot/System.map-*
/boot/vmlinuz-*
%ghost /boot/initramfs-%{KernelVer}.img
/boot/.vmlinuz-*.hmac
/etc/ld.so.conf.d/*
/lib/modules/%{KernelVer}/
%exclude /lib/modules/%{KernelVer}/source
%exclude /lib/modules/%{KernelVer}/build

%files devel
%defattr (-, root, root)
%doc
/lib/modules/%{KernelVer}/source
/lib/modules/%{KernelVer}/build
/usr/src/kernels/%{KernelVer}

%files headers
%defattr (-, root, root)
/usr/include/*
%exclude %{_includedir}/cpufreq.h
%exclude %{_includedir}/cpuidle.h

%if %{with_perf}
%files -n perf
%{_bindir}/perf
%{_libdir}/libperf-jvmti.so
%{_libexecdir}/perf-core
%{_datadir}/perf-core/
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%doc linux-%{KernelVer}/tools/perf/Documentation/examples.txt
%dir %{_datadir}/doc/perf-tip
%{_datadir}/doc/perf-tip/*
%license linux-%{KernelVer}/COPYING

%if 0%{?with_python2}
%files -n python2-perf
%license linux-%{KernelVer}/COPYING
%{python2_sitearch}/*
%endif

%files -n python3-perf
%license linux-%{KernelVer}/COPYING
%{python3_sitearch}/*
%endif

%files -n %{name}-tools -f cpupower.lang
%{_bindir}/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_datadir}/bash-completion/completions/cpupower
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%{_bindir}/tmon
%{_bindir}/iio_event_monitor
%{_bindir}/iio_generic_buffer
%{_bindir}/lsiio
%{_bindir}/lsgpio
%{_bindir}/gpio-hammer
%{_bindir}/gpio-event-mon
%{_bindir}/gpio-watch
%{_mandir}/man1/kvm_stat*
%{_bindir}/kvm_stat
%{_libdir}/libcpupower.so.1
%{_libdir}/libcpupower.so.0.0.1
%license linux-%{KernelVer}/COPYING

%files -n %{name}-tools-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%{_includedir}/cpuidle.h

%files -n bpftool
%{_sbindir}/bpftool
%{_sysconfdir}/bash_completion.d/bpftool
%{_mandir}/man8/bpftool-cgroup.8.gz
%{_mandir}/man8/bpftool-map.8.gz
%{_mandir}/man8/bpftool-prog.8.gz
%{_mandir}/man8/bpftool-perf.8.gz
%{_mandir}/man8/bpftool.8.gz
%{_mandir}/man8/bpftool-btf.8.gz
%{_mandir}/man8/bpftool-feature.8.gz
%{_mandir}/man8/bpftool-gen.8.gz
%{_mandir}/man8/bpftool-iter.8.gz
%{_mandir}/man8/bpftool-link.8.gz
%{_mandir}/man8/bpftool-net.8.gz
%{_mandir}/man8/bpftool-struct_ops.8.gz
%license linux-%{KernelVer}/COPYING

%if 0%{?with_source}
%files source
%defattr(-,root,root)
/usr/src/linux-%{KernelVer}/*
/usr/src/linux-%{KernelVer}/.config
%endif

%changelog
* Mon Jan 06 2025 ZhangPeng <zhangpeng362@huawei.com> - 6.6.0-73.0.0.77
- !14618  drm: zynqmp_kms: Unplug DRM device before removal
