Summary: The GNU core utilities: a set of tools commonly used in shell scripts
Name:    coreutils
Version: 5.2.1
Release: 49
License: GPL
Group:   System Environment/Base
Url:     http://www.gnu.org/software/coreutils/
BuildRequires: libselinux-devel

Source0: ftp://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.bz2
Source101:	DIR_COLORS
Source102:	DIR_COLORS.xterm
Source105:  colorls.sh
Source106:  colorls.csh
Source200:  su.pamd

# fileutils
Patch107: fileutils-4.1.10-timestyle.patch
Patch108: fileutils-4.1.5-afs.patch
Patch116: fileutils-4.1-dircolors_c.patch
Patch153: fileutils-4.1.10-utmp.patch
Patch182: coreutils-acl.patch

# sh-utils
Patch703: sh-utils-2.0.11-dateman.patch
Patch704: sh-utils-1.16-paths.patch
# RMS will never accept the PAM patch because it removes his historical
# rant about Twenex and the wheel group, so we'll continue to maintain
# it here indefinitely.
Patch706: coreutils-pam.patch
Patch713: coreutils-4.5.3-langinfo.patch
Patch714: coreutils-4.5.3-printf-ll.patch
Patch715: coreutils-4.5.3-sysinfo.patch

# (sb) lin18nux/lsb compliance
Patch800: coreutils-i18n.patch

Patch904: coreutils-5.0-allow_old_options.patch
Patch905: coreutils-jday.patch
Patch906: coreutils-fchown.patch
Patch907: coreutils-5.2.1-runuser.patch
Patch908: coreutils-getgrouplist.patch
Patch909: coreutils-zh_CN.patch
Patch910: coreutils-gcc4.patch
Patch911: coreutils-brokentest.patch
Patch912: coreutils-overflow.patch

# From upstream
Patch920: coreutils-dateseconds.patch
Patch921: coreutils-chown.patch
Patch922: coreutils-rmaccess.patch
Patch923: coreutils-copy.patch
Patch924: coreutils-stale-utmp.patch

#SELINUX Patch
Patch950: coreutils-selinux.patch

BuildRoot: %_tmppath/%{name}-root
BuildRequires:	gettext libtermcap-devel bison
%{?!nopam:BuildRequires: pam-devel}
BuildRequires:	texinfo >= 4.3
BuildRequires: autoconf >= 2.58, automake >= 1.8
Prereq:		/sbin/install-info
%{?!nopam:Requires: pam >= 0.66-12}
Prereq: grep, findutils

# Require a C library that doesn't put LC_TIME files in our way.
Conflicts: glibc < 2.2

Provides:	fileutils = %version, sh-utils = %version, stat, textutils = %version
Obsoletes:	fileutils sh-utils stat textutils

# readlink(1) moved here from tetex.
Conflicts:  tetex < 1.0.7-66

%description
These are the GNU core utilities.  This package is the combination of
the old GNU fileutils, sh-utils, and textutils packages.

%prep
%setup -q

# fileutils
%patch107 -p1 -b .timestyle
%patch108 -p1 -b .afs
%patch116 -p1
%patch153 -p1
%patch182 -p1 -b .acl

# sh-utils
%patch703 -p1 -b .dateman
%patch704 -p1 -b .paths
%patch706 -p1 -b .pam
%patch713 -p1 -b .langinfo
%patch714 -p1 -b .printf-ll
%patch715 -p1 -b .sysinfo

# li18nux/lsb
%patch800 -p1 -b .i18n

# Coreutils
%patch904 -p1 -b .allow_old_options
%patch905 -p1 -b .jday
%patch906 -p1 -b .fchown
%patch907 -p1 -b .runuser
%patch908 -p1 -b .getgrouplist
%patch909 -p1 -b .zh_CN
%patch910 -p1 -b .gcc4
%patch911 -p1 -b .brokentest
%patch912 -p1 -b .overflow

# From upstream
%patch920 -p1 -b .dateseconds
%patch921 -p1 -b .chown
%patch922 -p1 -b .rmaccess
%patch923 -p1 -b .copy
%patch924 -p1 -b .stale-utmp

#SELinux
%patch950 -p1 -b .selinux

# Don't run basic-1 test, since it breaks when run in the background
# (bug #102033).
perl -pi -e 's/basic-1//g' tests/stty/Makefile*

chmod a+x tests/sort/sort-mb-tests

%build
%ifarch s390 s390x
export CFLAGS="$RPM_OPT_FLAGS -fPIC"
%else
export CFLAGS="$RPM_OPT_FLAGS -fpic"
%endif
%{expand:%%global optflags %{optflags} -D_GNU_SOURCE=1}
touch aclocal.m4 configure config.hin Makefile.in */Makefile.in */*/Makefile.in
aclocal -I m4
autoconf --force
automake --copy --force
%configure --enable-largefile --with-afs %{?!nopam:--enable-pam} \
--enable-selinux \
|| :
make all %{?_smp_mflags} \
	%{?!nopam:CPPFLAGS="-DUSE_PAM"} \
	su_LDFLAGS="-pie %{?!nopam:-lpam -lpam_misc}"

[[ -f ChangeLog && -f ChangeLog.bz2  ]] || bzip2 -9f ChangeLog

# Run the test suite.
make check

# XXX docs should say /var/run/[uw]tmp not /etc/[uw]tmp
perl -pi -e 's,/etc/utmp,/var/run/utmp,g;s,/etc/wtmp,/var/run/wtmp,g' doc/coreutils.texi


%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

# man pages are not installed with make install
make mandir=$RPM_BUILD_ROOT%{_mandir} install-man

# fix japanese catalog file
if [ -d $RPM_BUILD_ROOT/%{_datadir}/locale/ja_JP.EUC/LC_MESSAGES ]; then
   mkdir -p $RPM_BUILD_ROOT/%{_datadir}/locale/ja/LC_MESSAGES
   mv $RPM_BUILD_ROOT/%{_datadir}/locale/ja_JP.EUC/LC_MESSAGES/*mo \
		$RPM_BUILD_ROOT/%{_datadir}/locale/ja/LC_MESSAGES
   rm -rf $RPM_BUILD_ROOT/%{_datadir}/locale/ja_JP.EUC
fi

# let be compatible with old fileutils, sh-utils and textutils packages :
mkdir -p $RPM_BUILD_ROOT{/bin,%_bindir,%_sbindir,/sbin}
%{?!nopam:mkdir -p $RPM_BUILD_ROOT%_sysconfdir/pam.d}
for f in basename cat chgrp chmod chown cp cut date dd df echo env false link ln ls mkdir mknod mv nice pwd rm rmdir sleep sort stty sync touch true uname unlink
do
	mv $RPM_BUILD_ROOT/{%_bindir,bin}/$f 
done

# chroot was in /usr/sbin :
mv $RPM_BUILD_ROOT/{%_bindir,%_sbindir}/chroot
# {cat,sort,cut} were previously moved from bin to /usr/bin and linked into 
for i in env cut; do ln -sf ../../bin/$i $RPM_BUILD_ROOT/usr/bin; done

mkdir -p $RPM_BUILD_ROOT/etc/profile.d
install -c -m644 %SOURCE101 $RPM_BUILD_ROOT/etc/
install -c -m644 %SOURCE102 $RPM_BUILD_ROOT/etc/
install -c -m755 %SOURCE105 $RPM_BUILD_ROOT/etc/profile.d
install -c -m755 %SOURCE106 $RPM_BUILD_ROOT/etc/profile.d

# su
install -m 4755 src/su $RPM_BUILD_ROOT/bin
install -m 755 src/runuser $RPM_BUILD_ROOT/sbin

# These come from util-linux and/or procps.
for i in hostname uptime kill ; do
	rm -f $RPM_BUILD_ROOT{%_bindir/$i,%_mandir/man1/$i.1}
done

%{?!nopam:install -m 644 %SOURCE200 $RPM_BUILD_ROOT%_sysconfdir/pam.d/su}

bzip2 -f9 old/*/C* || :

%find_lang %name

# (sb) Deal with Installed (but unpackaged) file(s) found
rm -f $RPM_BUILD_ROOT%{_datadir}/info/dir

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Remove these old glibc files on upgrade (bug #84090).
for file in $(find /usr/share/locale -type f -name LC_TIME); do
	[ -x /bin/rm ] && /bin/rm -f "$file"
done

# We must desinstall theses info files since they're merged in
# coreutils.info. else their postun'll be runned too last
# and install-info'll faill badly because of doubles
for file in sh-utils.info textutils.info fileutils.info; do
	if [ -f /usr/share/info/$file.bz2 ]; then
		/sbin/install-info /usr/share/info/$file.bz2 --dir=/usr/share/info/dir --remove &> /dev/null
	fi
done

%preun
if [ $1 = 0 ]; then
    [ -f %{_infodir}/%{name}.info.gz ] && \
      /sbin/install-info --delete %{_infodir}/%{name}.info.gz \
	%{_infodir}/dir || :
fi

%post
/bin/grep -v '(sh-utils)\|(fileutils)\|(textutils)' %{_infodir}/dir > \
  %{_infodir}/dir.rpmmodify || exit 0
    /bin/mv -f %{_infodir}/dir.rpmmodify %{_infodir}/dir
[ -f %{_infodir}/%{name}.info.gz ] && \
  /sbin/install-info %{_infodir}/%{name}.info.gz %{_infodir}/dir || :

%files -f %{name}.lang
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/DIR_COLORS*
%config(noreplace) %{_sysconfdir}/profile.d/*
%{?!nopam:%config(noreplace) /etc/pam.d/su}
%doc ABOUT-NLS ChangeLog.bz2 NEWS README THANKS TODO old/*
/bin/*
%_bindir/*
%_infodir/coreutils*
%_mandir/man*/*
%_sbindir/chroot
/sbin/runuser

%changelog
* Tue May 31 2005 Dan Walsh <dwalsh@redhat.com> 5.2.1-49
- Eliminate bogus "can not preserve context" message when moving files.

* Wed May 25 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-48
- Prevent buffer overflow in who(1) (bug #158405).

* Fri May 20 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-47
- Better error checking in the pam patch (bug #158189).

* Mon May 16 2005 Dan Walsh <dwalsh@redhat.com> 5.2.1-46
- Fix SELinux patch to better handle MLS integration

* Mon May 16 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-45
- Applied Russell Coker's selinux changes (bug #157856).

* Fri Apr  8 2005 Tim Waugh <twaugh@redhat.com>
- Fixed pam patch from Steve Grubb (bug #154946).
- Use better upstream patch for "stale utmp".

* Tue Mar 29 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-44
- Added "stale utmp" patch from upstream.

* Thu Mar 24 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-43
- Removed patch that adds -C option to install(1).

* Wed Mar 14 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-42
- Fixed pam patch.
- Fixed broken configure test.
- Fixed build with GCC 4 (bug #151045).

* Wed Feb  9 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-41
- Jakub Jelinek's sort -t multibyte fixes (bug #147567).

* Sat Feb  5 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-40
- Undo last change (bug #145266).

* Fri Feb  4 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-38
- Special case for ia32e in uname (bug #145266).

* Thu Jan 13 2005 Tim Waugh <twaugh@redhat.com> 5.2.1-37
- Fixed zh_CN translation (bug #144845).  Patch from Mitrophan Chin.

* Mon Dec 28 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-36
- Fix to only setdefaultfilecon if not overridden by command line

* Mon Dec 27 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-35
- Change install to restorecon if it can

* Wed Dec 15 2004 Tim Waugh <twaugh@redhat.com>
- Fixed small bug in i18n patch.

* Mon Dec  6 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-34
- Don't set fs uid until after pam_open_session (bug #77791).

* Thu Nov 25 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-33
- Fixed colorls.csh (bug #139988).  Patch from Miloslav Trmac.

* Mon Nov  8 2004 Tim Waugh <twaugh@redhat.com>
- Updated URL (bug #138279).

* Mon Oct 25 2004 Steve Grubb <sgrubb@redhat.com> 5.2.1-32
- Handle the return code of function calls in runcon.

* Mon Oct 18 2004 Tim Waugh <twaugh@redhat.com>
- Prevent compiler warning in coreutils-i18n.patch (bug #136090).

* Tue Oct  5 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-31
- getgrouplist() patch from Ulrich Drepper.
- The selinux patch should be applied last.

* Mon Oct  4 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-30
- Mv runuser to /sbin

* Mon Oct  4 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-28
- Fix runuser man page.

* Mon Oct  4 2004 Tim Waugh <twaugh@redhat.com>
- Fixed build.

* Fri Sep 24 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-26
- Add runuser as similar to su, but only runable by root

* Fri Sep 24 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-25
- chown(1) patch from Ulrich Drepper.

* Tue Sep 14 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-24
- SELinux patch fix: don't display '(null)' if getfilecon() fails
  (bug #131196).

* Fri Aug 20 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-23
- Fixed colorls.csh quoting (bug #102412).
- Fixed another join LSB test failure (bug #121153).

* Mon Aug 16 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-22
- Fixed sort -t LSB test failure (bug #121154).
- Fixed join LSB test failure (bug #121153).

* Wed Aug 11 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-21
- Apply upstream patch to fix 'cp -a' onto multiply-linked files (bug #128874).
- SELinux patch fix: don't error out if lgetfilecon() returns ENODATA.

* Tue Aug 10 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-20
- Added 'konsole' TERM to DIR_COLORS (bug #129544).

* Wed Aug  4 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-19
- Added 'gnome' TERM to DIR_COLORS (bug #129112).
- Worked around a bash bug #129128.
- Fixed an i18n patch bug in cut (bug #129114).

* Tue Aug  3 2004 Tim Waugh <twaugh@redhat.com>
- Fixed colorls.{sh,csh} so that the l. and ll aliases are always defined
  (bug #128948).

* Tue Jul 13 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-18
- Fixed field extraction in sort (bug #127694).

* Fri Jun 25 2004 Tim Waugh <twaugh@redhat.com>
- Added 'TERM screen.linux' to DIR_COLORS (bug #78816).

* Wed Jun 23 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-17
- Move pam-xauth to after pam-selinux

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jun  7 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-15
- Fix ls -Z (bug #125447).

* Fri Jun  4 2004 Tim Waugh <twaugh@redhat.com>
- Build requires bison (bug #125290).

* Fri Jun  4 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-14
- Fix selinux patch causing problems with ls --format=... (bug #125238).

* Thu Jun 3 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-13
- Change su to use pam_selinux open and pam_selinux close

* Wed Jun  2 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-12
- Don't call access() on symlinks about to be removed (bug #124699).

* Wed Jun  2 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-11
- Fix ja translation (bug #124862).

* Tue May 18 2004 Jeremy Katz <katzj@redhat.com> 5.2.1-10
- rebuild

* Mon May 17 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-9
- Mention pam in the info for su (bug #122592).
- Remove wheel group rant again (bug #122886).
- Change default behaviour for chgrp/chown (bug #123263).  Patch from
  upstream.

* Mon May 17 2004 Thomas Woerner <twoerner@redhat.com> 5.2.1-8
- compiling su PIE

* Wed May 12 2004 Tim Waugh <twaugh@redhat.com>
- Build requires new versions of autoconf and automake (bug #123098).

* Tue May  4 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-7
- Fix join -t (bug #122435).

* Tue Apr 20 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-6
- Fix 'ls -Z' displaying users/groups if stat() failed (bug #121292).

* Fri Apr 9 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-5
- Add ls -LZ fix
- Fix chcon to handle "."

* Wed Mar 17 2004 Tim Waugh <twaugh@redhat.com>
- Apply upstream fix for non-zero seconds for --date="10:00 +0100".

* Tue Mar 16 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-3
- If preserve fails, report as warning unless user requires preserve

* Tue Mar 16 2004 Dan Walsh <dwalsh@redhat.com> 5.2.1-2
- Make mv default to preserve on context

* Sat Mar 13 2004 Tim Waugh <twaugh@redhat.com> 5.2.1-1
- 5.2.1.

* Fri Mar 12 2004 Tim Waugh <twaugh@redhat.com> 5.2.0-9
- Add '-Z' to 'ls --help' output (bug #118108).

* Fri Mar  5 2004 Tim Waugh <twaugh@redhat.com>
- Fix deref-args test case for rebuilding under SELinux (bug #117556).

* Wed Feb 25 2004 Tim Waugh <twaugh@redhat.com> 5.2.0-8
- kill(1) offloaded to util-linux altogether.

* Tue Feb 24 2004 Tim Waugh <twaugh@redhat.com> 5.2.0-7
- Ship the real '[', not a symlink.

* Mon Feb 23 2004 Tim Waugh <twaugh@redhat.com> 5.2.0-6
- Apply Paul Eggert's chown patch (bug #116536).
- Merged chdir patch into pam patch where it belongs.

* Mon Feb 23 2004 Tim Waugh <twaugh@redhat.com> 5.2.0-5
- Fixed i18n patch bug causing sort -M not to work (bug #116575).

* Sat Feb 21 2004 Tim Waugh <twaugh@redhat.com> 5.2.0-4
- Reinstate kill binary, just not its man page (bug #116463).

* Sat Feb 21 2004 Tim Waugh <twaugh@redhat.com> 5.2.0-3
- Updated ls-stat patch.

* Fri Feb 20 2004 Dan Walsh <dwalsh@redhat.com> 5.2.0-2
- fix chcon to ignore . and .. directories for recursing

* Fri Feb 20 2004 Tim Waugh <twaugh@redhat.com> 5.2.0-1
- Patch ls so that failed stat() is handled gracefully (Ulrich Drepper).
- 5.2.0.

* Thu Feb 19 2004 Tim Waugh <twaugh@redhat.com>
- More AFS patch tidying.

* Wed Feb 18 2004 Dan Walsh <dwalsh@redhat.com> 5.1.3-0.2
- fix chcon to handle -h qualifier properly, eliminate potential crash 

* Wed Feb 18 2004 Tim Waugh <twaugh@redhat.com>
- Stop 'sort -g' leaking memory (i18n patch bug #115620).
- Don't ship kill, since util-linux already does.
- Tidy AFS patch.

* Mon Feb 16 2004 Tim Waugh <twaugh@redhat.com> 5.1.3-0.1
- 5.1.3.
- Patches ported forward or removed.

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com> 5.0-40
- rebuilt

* Tue Jan  20 2004 Dan Walsh <dwalsh@redhat.com> 5.0-39
- Change /etc/pam.d/su to remove preservuser and add multiple

* Tue Jan  20 2004 Dan Walsh <dwalsh@redhat.com> 5.0-38
- Change is_selinux_enabled to is_selinux_enabled > 0

* Tue Jan  20 2004 Dan Walsh <dwalsh@redhat.com> 5.0-37
- Add pam_selinux to pam file to allow switching of roles within selinux

* Fri Jan 16 2004 Tim Waugh <twaugh@redhat.com>
- The textutils-2.0.17-mem.patch is no longer needed.

* Thu Jan 15 2004 Tim Waugh <twaugh@redhat.com> 5.0-36
- Fixed autoconf test causing builds to fail.

* Tue Dec  9 2003 Dan Walsh <dwalsh@redhat.com> 5.0-35
- Fix copying to non xattr files

* Thu Dec  4 2003 Tim Waugh <twaugh@redhat.com> 5.0-34.sel
- Fix column widths problems in ls.

* Tue Dec  2 2003 Tim Waugh <twaugh@redhat.com> 5.0-33.sel
- Speed up md5sum by disabling speed-up asm.

* Wed Nov 19 2003 Dan Walsh <dwalsh@redhat.com> 5.0-32.sel
- Try again

* Wed Nov 19 2003 Dan Walsh <dwalsh@redhat.com> 5.0-31.sel
- Fix move on non SELinux kernels

* Fri Nov 14 2003 Tim Waugh <twaugh@redhat.com> 5.0-30.sel
- Fixed useless acl dependencies (bug #106141).

* Fri Oct 24 2003 Dan Walsh <dwalsh@redhat.com> 5.0-29.sel
- Fix id -Z

* Tue Oct 21 2003 Dan Walsh <dwalsh@redhat.com> 5.0-28.sel
- Turn on SELinux
- Fix chcon error handling

* Wed Oct 15 2003 Dan Walsh <dwalsh@redhat.com> 5.0-28
- Turn off SELinux

* Mon Oct 13 2003 Dan Walsh <dwalsh@redhat.com> 5.0-27.sel
- Turn on SELinux

* Mon Oct 13 2003 Dan Walsh <dwalsh@redhat.com> 5.0-27
- Turn off SELinux

* Mon Oct 13 2003 Dan Walsh <dwalsh@redhat.com> 5.0-26.sel
- Turn on SELinux

* Sun Oct 12 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- allow compiling without pam support

* Fri Oct 10 2003 Tim Waugh <twaugh@redhat.com> 5.0-23
- Make split(1) handle large files (bug #106700).

* Thu Oct  9 2003 Dan Walsh <dwalsh@redhat.com> 5.0-22
- Turn off SELinux

* Wed Oct  8 2003 Dan Walsh <dwalsh@redhat.com> 5.0-21.sel
- Cleanup SELinux patch

* Fri Oct  3 2003 Tim Waugh <twaugh@redhat.com> 5.0-20
- Restrict ACL support to only those programs needing it (bug #106141).
- Fix default PATH for LSB (bug #102567).

* Thu Sep 11 2003 Dan Walsh <dwalsh@redhat.com> 5.0-19
- Turn off SELinux

* Wed Sep 10 2003 Dan Walsh <dwalsh@redhat.com> 5.0-18.sel
- Turn on SELinux

* Fri Sep 5 2003 Dan Walsh <dwalsh@redhat.com> 5.0-17
- Turn off SELinux

* Tue Sep 2 2003 Dan Walsh <dwalsh@redhat.com> 5.0-16.sel
- Only call getfilecon if the user requested it.
- build with selinux

* Wed Aug 20 2003 Tim Waugh <twaugh@redhat.com> 5.0-14
- Documentation fix (bug #102697).

* Tue Aug 12 2003 Tim Waugh <twaugh@redhat.com> 5.0-13
- Made su use pam again (oops).
- Fixed another i18n bug causing sort --month-sort to fail.
- Don't run dubious stty test, since it fails when backgrounded
  (bug #102033).
- Re-enable make check.

* Fri Aug  8 2003 Tim Waugh <twaugh@redhat.com> 5.0-12
- Don't run 'make check' for this build (build environment problem).
- Another uninitialized variable in i18n (from bug #98683).

* Wed Aug 6 2003 Dan Walsh <dwalsh@redhat.com> 5.0-11
- Internationalize runcon
- Update latest chcon from NSA

* Wed Jul 30 2003 Tim Waugh <twaugh@redhat.com>
- Re-enable make check.

* Wed Jul 30 2003 Tim Waugh <twaugh@redhat.com> 5.0-9
- Don't run 'make check' for this build (build environment problem).

* Mon Jul 28 2003 Tim Waugh <twaugh@redhat.com> 5.0-8
- Actually use the ACL patch (bug #100519).

* Wed Jul 18 2003 Dan Walsh <dwalsh@redhat.com> 5.0-7
- Convert to SELinux

* Mon Jun  9 2003 Tim Waugh <twaugh@redhat.com>
- Removed samefile patch.  Now the test suite passes.

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May 28 2003 Tim Waugh <twaugh@redhat.com> 5.0-5
- Both kon and kterm support colours (bug #83701).
- Fix 'ls -l' alignment in zh_CN locale (bug #88346).

* Mon May 12 2003 Tim Waugh <twaugh@redhat.com> 5.0-4
- Prevent file descriptor leakage in du (bug #90563).
- Build requires recent texinfo (bug #90439).

* Wed Apr 30 2003 Tim Waugh <twaugh@redhat.com> 5.0-3
- Allow obsolete options unless POSIXLY_CORRECT is set.

* Sat Apr 12 2003 Tim Waugh <twaugh@redhat.com>
- Fold bug was introduced by i18n patch; fixed there instead.

* Fri Apr 11 2003 Matt Wilson <msw@redhat.com> 5.0-2
- fix segfault in fold (#88683)

* Sat Apr  5 2003 Tim Waugh <twaugh@redhat.com> 5.0-1
- 5.0.

* Mon Mar 24 2003 Tim Waugh <twaugh@redhat.com>
- Use _smp_mflags.

* Mon Mar 24 2003 Tim Waugh <twaugh@redhat.com> 4.5.11-2
- Remove overwrite patch.
- No longer seem to need nolibrt, errno patches.

* Thu Mar 20 2003 Tim Waugh <twaugh@redhat.com>
- No longer seem to need danglinglink, prompt, lug, touch_errno patches.

* Thu Mar 20 2003 Tim Waugh <twaugh@redhat.com> 4.5.11-1
- 4.5.11.
- Use packaged readlink.

* Wed Mar 19 2003 Tim Waugh <twaugh@redhat.com> 4.5.10-1
- 4.5.10.
- Update lug, touch_errno, acl, utmp, printf-ll, i18n, test-bugs patches.
- Drop fr_fix, LC_TIME, preserve, regex patches.

* Wed Mar 12 2003 Tim Waugh <twaugh@redhat.com> 4.5.3-21
- Fixed another i18n patch bug (bug #82032).

* Tue Mar 11 2003 Tim Waugh <twaugh@redhat.com> 4.5.3-20
- Fix sort(1) efficiency in multibyte encoding (bug #82032).

* Tue Feb 18 2003 Tim Waugh <twaugh@redhat.com> 4.5.3-19
- Ship readlink(1) (bug #84200).

* Thu Feb 13 2003 Tim Waugh <twaugh@redhat.com> 4.5.3-18
- Deal with glibc < 2.2 in %%pre scriplet (bug #84090).

* Wed Feb 12 2003 Tim Waugh <twaugh@redhat.com> 4.5.3-16
- Require glibc >= 2.2 (bug #84090).

* Tue Feb 11 2003 Bill Nottingham <notting@redhat.com> 4.5.3-15
- fix group (#84095)

* Wed Jan 22 2003 Tim Powers <timp@redhat.com> 4.5.3-14
- rebuilt

* Thu Jan 16 2003 Tim Waugh <twaugh@redhat.com>
- Fix rm(1) man page.

* Thu Jan 16 2003 Tim Waugh <twaugh@redhat.com> 4.5.3-13
- Fix re_compile_pattern check.
- Fix su hang (bug #81653).

* Tue Jan 14 2003 Tim Waugh <twaugh@redhat.com> 4.5.3-11
- Fix memory size calculation.

* Tue Dec 17 2002 Tim Waugh <twaugh@redhat.com> 4.5.3-10
- Fix mv error message (bug #79809).

* Mon Dec 16 2002 Tim Powers <timp@redhat.com> 4.5.3-9
- added PreReq on grep

* Fri Dec 13 2002 Tim Waugh <twaugh@redhat.com>
- Fix cp --preserve with multiple arguments.

* Thu Dec 12 2002 Tim Waugh <twaugh@redhat.com> 4.5.3-8
- Turn on colorls for screen (bug #78816).

* Mon Dec  9 2002 Tim Waugh <twaugh@redhat.com> 4.5.3-7
- Fix mv (bug #79283).
- Add patch27 (nogetline).

* Sun Dec  1 2002 Tim Powers <timp@redhat.com> 4.5.3-6
- use the su.pamd from sh-utils since it works properly with multilib systems

* Fri Nov 29 2002 Tim Waugh <twaugh@redhat.com> 4.5.3-5
- Fix test suite quoting problems.

* Fri Nov 29 2002 Tim Waugh <twaugh@redhat.com> 4.5.3-4
- Fix scriplets.
- Fix i18n patch so it doesn't break uniq.
- Fix several other patches to either make the test suite pass or
  not run the relevant tests.
- Run 'make check'.
- Fix file list.

* Thu Nov 28 2002 Tim Waugh <twaugh@redhat.com> 4.5.3-3
- Adapted for Red Hat Linux.
- Self-host for help2man.
- Don't ship readlink just yet (maybe later).
- Merge patches from fileutils and sh-utils (textutils ones are already
  merged it seems).
- Keep the binaries where the used to be (in particular, id and stat).

* Sun Nov 17 2002 Stew Benedict <sbenedict@mandrakesoft.com> 4.5.3-2mdk
- LI18NUX/LSB compliance (patch800)
- Installed (but unpackaged) file(s) - /usr/share/info/dir

* Thu Oct 31 2002 Thierry Vignaud <tvignaud@mandrakesoft.com> 4.5.3-1mdk
- new release
- rediff patch 180
- merge patch 150 into 180

* Mon Oct 14 2002 Thierry Vignaud <tvignaud@mandrakesoft.com> 4.5.2-6mdk
- move su back to /bin

* Mon Oct 14 2002 Thierry Vignaud <tvignaud@mandrakesoft.com> 4.5.2-5mdk
- patch 0 : lg locale is illegal and must be renamed lug (pablo)

* Mon Oct 14 2002 Thierry Vignaud <tvignaud@mandrakesoft.com> 4.5.2-4mdk
- fix conflict with procps

* Mon Oct 14 2002 Thierry Vignaud <tvignaud@mandrakesoft.com> 4.5.2-3mdk
- patch 105 : fix install -s

* Mon Oct 14 2002 Thierry Vignaud <tvignaud@mandrakesoft.com> 4.5.2-2mdk
- fix build
- don't chmode two times su
- build with large file support
- fix description
- various spec cleanups
- fix chroot installation
- fix missing /bin/env
- add old fileutils, sh-utils & textutils ChangeLogs

* Fri Oct 11 2002 Thierry Vignaud <tvignaud@mandrakesoft.com> 4.5.2-1mdk
- initial release (merge fileutils, sh-utils & textutils)
- obsoletes/provides: sh-utils/fileutils/textutils
- fileutils stuff go in 1xx range
- sh-utils stuff go in 7xx range
- textutils stuff go in 5xx range
- drop obsoletes patches 1, 2, 10 (somes files're gone but we didn't ship
  most of them)
- rediff patches 103, 105, 111, 113, 180, 706
- temporary disable patch 3 & 4
- fix fileutils url
