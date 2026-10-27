#############################################################################
#
# Copyright (c) 2006-2013 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

IPNTP = yes

#############################################################################
# PATHS
#############################################################################

# obj root:
IPNTP_OBJROOT	*= $(IPOBJDIR)$/ipntp


#############################################################################
# IPDEFINE
#############################################################################

IPDEFINE 	+= -IPNTP -NTP_VXWORKS_6
IPDEFINE 	+= -SYS_VXWORKS -HAVE_CONFIG_H
#IPDEFINE 	+= -NTP_DEBUG
IPDEFINE 	+= -HAVE_STRUCT_SOCKADDR_STORAGE -HAVE_STRUCT_IN6_ADDR -HAVE_MKTIME
IPDEFINE 	+= -HAVE_ADDRINFO -HAVE_STRUCT_S6_ADDR -HAVE_SOCKADDR_IN6
#IPDEFINE 	+= -OPENSSL


#############################################################################
# IPOBJECTS
#############################################################################

# config files
IPOBJECTS	+= ipntp_config.o

# Interpeak NTP
# libisc objects
IPNTP_UOBJ	+= assertions.o
IPNTP_UOBJ	+= interfaceiter.o
IPNTP_UOBJ	+= isc_error.o
IPNTP_UOBJ	+= isc_inet_ntop.o
IPNTP_UOBJ	+= isc_inet_pton.o
IPNTP_UOBJ	+= isc_lib.o
IPNTP_UOBJ	+= isc_mem.o
IPNTP_UOBJ	+= isc_strerror.o
IPNTP_UOBJ	+= msgcat.o
IPNTP_UOBJ	+= net.o
IPNTP_UOBJ	+= netaddr.o
IPNTP_UOBJ	+= sockaddr.o

# libntp objects
IPNTP_UOBJ	+= a_md5encrypt.o
IPNTP_UOBJ	+= adjtime.o
IPNTP_UOBJ	+= atoint.o
IPNTP_UOBJ	+= atolfp.o
IPNTP_UOBJ	+= atouint.o
IPNTP_UOBJ	+= audio.o
IPNTP_UOBJ	+= authkeys.o
IPNTP_UOBJ	+= authreadkeys.o
IPNTP_UOBJ	+= authusekey.o
IPNTP_UOBJ	+= buftvtots.o
IPNTP_UOBJ	+= caljulian.o
IPNTP_UOBJ	+= caltontp.o
IPNTP_UOBJ	+= calyearstart.o
IPNTP_UOBJ	+= clocktime.o
IPNTP_UOBJ	+= clocktypes.o
IPNTP_UOBJ	+= decodenetnum.o
IPNTP_UOBJ	+= dofptoa.o
IPNTP_UOBJ	+= dolfptoa.o
IPNTP_UOBJ	+= findconfig.o
IPNTP_UOBJ	+= fptoa.o
IPNTP_UOBJ	+= fptoms.o
IPNTP_UOBJ	+= hextoint.o
IPNTP_UOBJ	+= hextolfp.o
IPNTP_UOBJ	+= humandate.o
IPNTP_UOBJ	+= inttoa.o
IPNTP_UOBJ	+= iosignal.o
IPNTP_UOBJ	+= lib_strbuf.o
IPNTP_UOBJ	+= machines.o
IPNTP_UOBJ	+= md5c.o
IPNTP_UOBJ	+= mfptoa.o
IPNTP_UOBJ	+= mfptoms.o
IPNTP_UOBJ	+= modetoa.o
IPNTP_UOBJ	+= mstolfp.o
IPNTP_UOBJ	+= msutotsf.o
IPNTP_UOBJ	+= msyslog.o
IPNTP_UOBJ	+= netof.o
IPNTP_UOBJ	+= ntp_getopt.o
#IPNTP_UOBJ	+= ntp_memmove.o
IPNTP_UOBJ	+= ntp_mktime.o
IPNTP_UOBJ	+= ntp_random.o
IPNTP_UOBJ	+= ntp_rfc2553.o
IPNTP_UOBJ	+= ntp_snprintf.o
IPNTP_UOBJ	+= ntp_strdup.o
IPNTP_UOBJ	+= ntp_strstr.o
IPNTP_UOBJ	+= numtoa.o
IPNTP_UOBJ	+= numtohost.o
IPNTP_UOBJ	+= octtoint.o
IPNTP_UOBJ	+= prettydate.o
IPNTP_UOBJ	+= recvbuff.o
IPNTP_UOBJ	+= refnumtoa.o
IPNTP_UOBJ	+= socktoa.o
IPNTP_UOBJ	+= socktohost.o
IPNTP_UOBJ	+= statestr.o
IPNTP_UOBJ	+= syssignal.o
IPNTP_UOBJ	+= systime.o
IPNTP_UOBJ	+= tsftomsu.o
IPNTP_UOBJ	+= tstotv.o
IPNTP_UOBJ	+= tvtoa.o
IPNTP_UOBJ	+= tvtots.o
IPNTP_UOBJ	+= uglydate.o
IPNTP_UOBJ	+= uinttoa.o
IPNTP_UOBJ	+= utvtoa.o
IPNTP_UOBJ	+= ymd2yd.o

# ntpd objects
#IPNTP_UOBJ	+= cmd_args.o
IPNTP_UOBJ	+= cmd_args_old.o
IPNTP_UOBJ	+= ipntp.o
IPNTP_UOBJ	+= ipntp_cmd_ntp.o
IPNTP_UOBJ	+= ntp_config.o
IPNTP_UOBJ	+= ntp_control.o
IPNTP_UOBJ	+= ntp_crypto.o
IPNTP_UOBJ	+= ntp_filegen.o
IPNTP_UOBJ	+= ntp_intres.o
IPNTP_UOBJ	+= ntp_io.o
IPNTP_UOBJ	+= ntp_loopfilter.o
IPNTP_UOBJ	+= ntp_mem.o
IPNTP_UOBJ	+= ntp_monitor.o
IPNTP_UOBJ	+= ntp_peer.o
IPNTP_UOBJ	+= ntp_proto.o
IPNTP_UOBJ	+= ntp_refclock.o
IPNTP_UOBJ	+= ntp_request.o
IPNTP_UOBJ	+= ntp_restrict.o
IPNTP_UOBJ	+= ntp_timer.o
IPNTP_UOBJ	+= ntp_util.o
IPNTP_UOBJ	+= ntp_version.o
IPNTP_UOBJ	+= ntpd.o
IPNTP_UOBJ	+= refclock_conf.o
IPNTP_UOBJ	+= refclock_local.o

# ntpdc objects
IPNTP_UOBJ	+= ntpdc.o
IPNTP_UOBJ	+= ntpdc_ops.o

# ntpq objects
IPNTP_UOBJ	+= ntpq.o
IPNTP_UOBJ	+= ntpq-subs.o

# util objects
IPNTP_UOBJ	+= ntp-keygen.o  


_IPNTP_UOBJ = $(foreach,i,$(IPNTP_UOBJ) $(IPNTP_OBJROOT)$/$i)


#############################################################################
# IPINCLUDE
#############################################################################

IPINCLUDE	+= $(IPNTP_ROOT)$/config
IPINCLUDE	+= $(IPNTP_ROOT)$/include
IPINCLUDE	+= $(IPNTP_ROOT)$/src

IPNTP_INCLUDE += $(IPXINC_ROOT)$/include $(IPINCLUDE)

#############################################################################
# LIB
#############################################################################

# library name:
IPNTP_ULIB 	= $(IPLIBDIR)$/$(IPLIBPREFIX)ipntp_ulib$(IPLIBSUFFIX)
IPNTP_LIBS	= $(IPNTP_ULIB)
IPLIBRARIES    += $(IPNTP_LIBS)

# dependencies:
"$(IPNTP_ULIB)":	$(_IPNTP_UOBJ)
	$(IPAR) $(IPAROUT)$(IPNTP_ULIB) $(_IPNTP_UOBJ)

"$(IPNTP_OBJROOT)$/%.o": $(IPNTP_ROOT)$/src$/%.c
	$(IPCC) $(IPCFLAGS) $(_IPDEFINE) $(_IPINCLUDE) $(IPCCOUT) $<

"$(IPOBJDIR)$/ipntp_config.o": $(IPNTP_ROOT)$/config$/ipntp_config.c
	$(IPCC) $(IPCFLAGS) $(_IPDEFINE) $(_IPINCLUDE) $(IPCCOUT) $<


#############################################################################
# DEPENDENCIES
#############################################################################

IPLIBS	+= ipntp_libs

ipntp_libs:	ipntp_dirs $(IPNTP_LIBS)

ipntp_dirs:	ipcom_dirs $(IPNTP_OBJROOT)

"$(IPNTP_OBJROOT)":
	$(IPMKDIR) $(IPNTP_OBJROOT)

ipntp_clean:
	$(IPRMDIR) $(IPNTP_OBJROOT)

ipntp_vclean:	ipntp_clean
	$(IPRM) $(IPNTP_LIBS)


#############################################################################
# LINT
###########################################################################

IPNTP_SRC	= $(foreach,i,$(IPNTP_UOBJ) $(subst,.o,.c $i))
_IPNTP_SRC	= $(foreach,i,$(IPNTP_SRC) $(IPNTP_ROOT)$/src$/$i)
_IPNTP_SRC	+= $(IPNTP_ROOT)$/config$/ipntp_config.c

ipntp_lint .PHONY:
	$(IPLINT) $(_IPDEFINE) $(_IPINCLUDE) $(_IPNTP_SRC)


###########################################################################
# END OF IPNTP.MK
#############################################################################
