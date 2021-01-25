#!/usr/bin/env python
#############################################################################
#
# Copyright (c) 2006-2020 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#
#modification history
#--------------------
#16jul20,yyl fix bug when adding files into vip (VXWEXEC-50345)
#01jun20,ply add test case for sftp .(VXWEXEC-50358)
#03mar20,yyl  Add directly connected board support. (VXWEXEC-47902)
#03dec18,rjq  Add IPv6 support in RTNET socktest. (F10020)
#04sep18,jxy  Replace _WRS_CONFIG_OPENSSL with _WRS_CONFIG_OPENSSL_CRYPTO due to
#             merge the two layers OPENSSL and HASH into one (V7SEC-682)
#12jul18,lan add OPENSSL_FIPS KONG test support. (F10643)
#09jul18,lan support to add files to VIP. (V7NET-1686)
#21dec17,ply add test case for user_management_ldap.(F9804)
#18sep17,ply add test case for user_management.(V7SEC-490)
#11jun14,h_s exclude TCF from vsb to avoid the TCF packet impact NAT testing, V7NET-347.
#20may14,h_s add user ipssh for ssh test suite, V7NET-343.
#29apr14,h_s adapt test script for vx7, US35892.
#

from __future__ import with_statement
import pdb
from runtestsuite_common import *
from runtestsuite_conf import *
import os
import sys
import re
import time
from commands import getoutput
import multiprocessing

wrtool_lock = '/tmp/wrtool_lock'

class BuildException(Exception):
    pass
    
def get_bsp_name(board):
    n = board.count('_')
    if n == 5:
        b = board.split('_')
        return b[0] + '_' + b[1]
    else:
        return board

def get_layer_file(prj_path):
    rets = []
    for parent_dir, sub_dirs, files in os.walk(prj_path, topdown=True):
        for the_file in files:
            if the_file == 'layer.vsbl':
                rets.append(os.path.join(parent_dir, the_file)) 
    return rets
    
def vxworks(conf,
            cflags, log, board, installpath, cvsbuild, logpath,
            wrenv, smp, m64bit, speed, shell, debug, ipv4only,
            ipv6only, target, tool,
            edr,bridgeports,
            scratchdir = '/tmp/buildunions/'):
    if 'vxconf' in conf and 'RTNET' in conf['vxconf']:
        # build RTNET
        return  vxworks_rtnet(conf,
                cflags, log, board, installpath, cvsbuild, logpath,
                wrenv, smp, m64bit, speed, shell, debug, ipv4only,
                ipv6only, target, tool,
                edr,bridgeports,
                scratchdir = '/tmp/buildunions/')
    else:
        return vxworks_ipnet(conf,
                cflags, log, board, installpath, cvsbuild, logpath,
                wrenv, smp, m64bit, speed, shell, debug, ipv4only,
                ipv6only, target, tool,
                edr,bridgeports,
                scratchdir = '/tmp/buildunions/')


def work_around_1(pkgs_path):
    # set up 2+ telnet sessions for RTNet Kong
    print '=== work_around_1'
    telnet_config = get_dvd_fullpath(pkgs_path, '/net/rtnet/configlette/usrRtnet.c')
    sudo('cp -f %s %s.orig' % (telnet_config, telnet_config))
    __replace(telnet_config, 'if (telnetdInit (1, TRUE) == OK)', 'if (telnetdInit (2, TRUE) == OK)')
    

def work_around_2(pkgs_path):
    # avoid build demo failure (V7NET-1483) by commenting IPNET_SOCK_SHOW
    print '=== work_around_2'
    ipnet_sock = get_dvd_fullpath(pkgs_path, '/net/ipnet/coreip/src/ipnet2/src/ipnet_sock.c')
    sudo('cp -f %s %s.orig' % (ipnet_sock, ipnet_sock))
    __replace(ipnet_sock, '#define IPNET_SOCK_SHOW', '/* #define IPNET_SOCK_SHOW */')
            

def __replace(file_name, old_str, new_str):
    with open(file_name, 'r') as fd:
        content = fd.read()
        if content.find(new_str) != -1:
            print '=== already there at %s' % file_name
            return
        if content.find(old_str) != -1:
            print '=== replacing at %s' % file_name
            content = content.replace(old_str, new_str)
        else:
            raise BaseException('cannot find %s at %s' % (old_str, file_name))
    
    with open(file_name, 'w') as fdw:
        fdw.write(content)
    

def work_around_3(wrenv_cmd, pkgs_path, prj_path, conf, board, tool, smp, m64bit):
    # build multiple images with different mac addresses
    def run_cmd(x):
        print(">>>>>> " + wrenv_cmd + x)
        lines = sudo(wrenv_cmd + x + " 2>&1")
        for line in lines: print line

    print '=== work_around_3'
    vip_path = prj_path + '/%s_vip' % board
    
    if board == 'fsl_imx6':
        vip_num = 2
    elif board == 'itl_generic':
        vip_num = 1
    else:
        raise BuildException('board %s not supported at work_around_3' % board)
                        
    for i in xrange(vip_num):
        print sudo('rm -fr %s' % vip_path)
        if board == 'fsl_imx6':
            change_mac_address(pkgs_path, vlmTargets[board]['dts'], i)
        vxprj = 'vxprj create -vsb %s_vsb %s %s %s_vip' % (board, board, tool, board)
        if smp:
            vxprj += ' -smp'
        if m64bit:
            vxprj += ' -lp64'
        for c in conf['vxprj']:
            vxprj += " -c INCLUDE_" + c.upper()
        if board == 'fsl_imx6':
            vxprj += ' -c INCLUDE_FSL_IMX6Q_SABRELITE'
        if 'vxparam' in conf:
            for c in conf['vxparam']:
                vxprj += " -p " + c
        
        os.chdir(prj_path)
        run_cmd(vxprj)
        os.chdir("%s_vip" % board)        
    
        run_cmd('vxprj component remove INCLUDE_IPNET')
        
        #add file for the vip
        if 'vxfile' in conf:
            for file in conf['vxfile']:
                filePath = get_dvd_fullpath(pkgs_path, file)
                vxprj = 'vxprj file add %s' % (filePath)
                run_cmd(vxprj)
        
        if board == 'itl_generic':
            run_cmd('vxprj component add INCLUDE_GEI825XX_VXB_END INCLUDE_ROMFS INCLUDE_SHELL INCLUDE_SHELL_INTERP_C INCLUDE_SHELL_INTERP_CMD INCLUDE_RTP_SHELL_CMD INCLUDE_DISK_UTIL_SHELL_CMD INCLUDE_NETWORK INCLUDE_END')
            run_cmd('vxprj component add INCLUDE_FAST_REBOOT INCLUDE_USB_XHCI_HCD_INIT INCLUDE_USB_GEN2_SER_FTDI232 INCLUDE_USB_GEN2_SER_PL2303 INCLUDE_USB_GEN2_SERIAL_PCCONSOLE_INIT')
            run_cmd('vxprj parameter set CONSOLE_TTY 1')
        
        run_cmd("vxprj build")
        os.chdir(prj_path)
        
        # cp uVxWorks and imx6q-sabrelite.dtb to _image/tN directory
        image_path = prj_path + '/%s_image' % board
        if not os.path.exists(image_path):
            print sudo('mkdir -p %s' % image_path)
        target_path = image_path + '/t%s' % i
        if not os.path.exists(target_path):
            print sudo('mkdir -p %s' % target_path)
        print sudo('cp -f %s %s' % (vip_path + '/default/%s' % vlmTargets[board]['image'], target_path))
        print sudo('cp -f %s %s' % (vip_path + '/default/%s' % vlmTargets[board]['dtb'], target_path))
        print sudo('cp -f %s %s' % (vip_path + '/default/vxWorks.bin', target_path))


def restore_work_around_file(pkgs_path):        
    # restore modified source files
    def findOrigFile(findPath):
        retFiles = []
        for parentDir, subDirs, files in os.walk(findPath, topdown=True):
            for f in files:
                if f.endswith('.orig'):
                    retFiles.append(parentDir + '/' + f)
        return retFiles
    
    origFiles = findOrigFile(pkgs_path)
    print '=== find original files at %s' % pkgs_path
    print '=== origFiles', origFiles
    
    for f in origFiles:
        if os.path.basename(f).replace('.orig', '') in ('usrRtnet.c', 'ipnet_sock.c', 'imx6q-sabrelite.dts'):
            print sudo('cp -f %s %s' % (f, f.replace('.orig', '')))
            print sudo('rm -f %s' % f)
               

def change_mac_address(pkgs_path, dts_file, num):
    dts_file = get_dvd_fullpath(pkgs_path, dts_file)
    mac, new_mac = '', ''
    with open(dts_file, 'r') as fd:
        content = fd.read()
        ptn = '(?s)local-mac-address = \[(.*?)\];'
        found = re.search(ptn, content)
        if found is not None:
            mac = found.groups()[0].strip()
            new_mac = increase_mac_address(mac, num)
            print '=== new_mac:', new_mac
        else:
            raise BaseException('cannot find mac address at %s' % dts_file)
    
    sudo('cp %s %s.orig' % (dts_file, dts_file))
    with open(dts_file, 'w') as fdw:
        content = content.replace(mac, new_mac)
        fdw.write(content)
    

def increase_mac_address(mac, num):
    last = mac.split(' ')[-1]
    new_last_int = ord(last.decode('hex')) + num
    new_last = hex(new_last_int).upper().replace('0X', '')
    new_mac = ' '.join(mac.split(' ')[:-1] + [new_last])
    return new_mac

    
def vxworks_rtnet(conf,
                cflags, log, board, installpath, cvsbuild, logpath,
                wrenv, smp, m64bit, speed, shell, debug, ipv4only,
                ipv6only, target, tool,
                edr,bridgeports,
                scratchdir = '/tmp/buildunions/'):
    pkgs_path, wrenv_prefix = get_vxworks_env(installpath)
    wrenv_cmd = "%s LM_LICENSE_FILE=27000@ala-lic4.wrs.com " % wrenv_prefix

    def run_cmd(x):
        print(">>>>>> " + wrenv_cmd + x)
        lines = sudo(wrenv_cmd + x + " 2>&1")
        for line in lines: print line

    if not ipv4only:
        inet6 = " -inet6"
    else:
        inet6 = ""
    
    if m64bit:
        flag64bit = '-lp64'
    else:
        flag64bit = ''
    
    if smp:
        flag_smp = '-smp'
    else:
        flag_smp = ''
            
    debugopts = ''

    #work_around_1(pkgs_path)
    #work_around_2(pkgs_path)
    
    prj_path = os.getcwd()

    # Create VSB
    vsb_create_cmd = "vxprj vsb create -force -bsp %s -S %s %s %s_vsb" % (board, flag64bit, flag_smp, board)
    if target == 'NEHALEM':
        vsb_create_cmd += ' -cpu NEHALEM'
    if 'vxmake' in conf:
        for c in conf['vxmake']: 
            vsb_create_cmd += ' -add _WRS_CONFIG_COMPONENT_%s=y' % c.upper()    
    run_cmd(vsb_create_cmd)        

    os.chdir("%s_vsb" % board)
    # Add VSB configuration
    if 'vxconf' in conf:
        for c in conf['vxconf']:
            run_cmd("vxprj vsb config -o -add _WRS_CONFIG_%s=y" % c.upper())

    # Add CFLAGS
    vsb_config_cmd = 'vxprj vsb config -s'
    cflags = []
    if 'extra_build_cflags' in conf and conf['extra_build_cflags']:
        for f in conf['extra_build_cflags']:
            cflags.append(f)
        extra_defines = " ".join(cflags)
        vsb_config_cmd += ' -add _WRS_CONFIG_ADDEDCFLAGS="%s"' % extra_defines
        run_cmd(vsb_config_cmd)

    cflags = []
    if 'extra_build_user_cflags' in conf and conf['extra_build_user_cflags']:
        for f in conf['extra_build_user_cflags']:
            cflags.append(f)
        extra_defines = " ".join(cflags)
        vsb_config_cmd += ' -add _WRS_CONFIG_ADDEDUSERCFLAGS="%s"' % extra_defines
        run_cmd(vsb_config_cmd)
    
    # specific for the target 25096 which uses USB as serial console
    #if board == 'itl_generic':    
    #    run_cmd("vxprj vsb add USB")

    run_cmd("make -j %s" % multiprocessing.cpu_count())

    vip_num = len(vlmTargetJsons[board])
    vip_path = prj_path + '/%s_vip' % board
    vsb_path = prj_path + '/%s_vsb' % board
    
    for i in xrange(vip_num):
        print sudo('rm -fr %s' % vip_path)
        vxprj = 'vxprj create -vsb %s_vsb %s %s %s' % (board, board, tool, vip_path)
        for c in conf['vxprj']:
            vxprj += " -c INCLUDE_" + c.upper()
        if board == 'fsl_imx6':
            vxprj += ' -c INCLUDE_FSL_IMX6Q_SABRELITE'
        if 'vxparam' in conf:
            for c in conf['vxparam']:
                if c.find('RTNET_JSON_FILE') != -1:
                    continue
                else:
                    vxprj += " -p " + c
        
        os.chdir(prj_path)
        run_cmd(vxprj)
        os.chdir("%s_vip" % board)        
    
        # for 25096 which use USB for console
        #if board == 'itl_generic':
        #    run_cmd('vxprj component add INCLUDE_GEI825XX_VXB_END INCLUDE_ROMFS INCLUDE_SHELL INCLUDE_SHELL_INTERP_C INCLUDE_SHELL_INTERP_CMD INCLUDE_RTP_SHELL_CMD INCLUDE_DISK_UTIL_SHELL_CMD INCLUDE_NETWORK INCLUDE_END')
        #    run_cmd('vxprj component add INCLUDE_FAST_REBOOT INCLUDE_USB_XHCI_HCD_INIT INCLUDE_USB_GEN2_SER_FTDI232 INCLUDE_USB_GEN2_SER_PL2303 INCLUDE_USB_GEN2_SERIAL_PCCONSOLE_INIT')
        #    run_cmd('vxprj parameter set CONSOLE_TTY 1')
    
        if 'vxprj_remove' in conf:
            for c in conf['vxprj_remove']:    
                run_cmd('vxprj component remove INCLUDE_%s' % c)
        
        #add file for the vip
        if 'vxfile' in conf:
            for file in conf['vxfile']:
                filePath = get_dvd_fullpath(pkgs_path, file)
                vxprj = 'vxprj file add %s' % (filePath)
                run_cmd(vxprj)
        
        #add extra_define for the vip
        if 'vx_extra_define' in conf:
            for adddefines in conf['vx_extra_define']:
                # get EXTRA_DEFINE first to avoid replacing existing EXTRA_DEFINE
                lines = sudo(wrenv_cmd + ' vxprj buildmacro get %s_vip.wpj EXTRA_DEFINE' % board)
                print '=== existing EXTRA_DEFINE:', ' '.join(lines)
                extra_defines = "\'" + ' '.join(lines).replace('\n', ' ') + ' ' + adddefines + "\'"
                run_cmd("vxprj buildmacro set EXTRA_DEFINE %s" % extra_defines)
                
        #add json configuration file for the vip
        if 'jsonfile' in conf:
            if not os.path.exists('./romfs'):
                run_cmd("mkdir romfs")
            for json_file in conf['jsonfile']:
                filePath = get_dvd_fullpath(pkgs_path, json_file)
                run_cmd("cp %s ./romfs/" % filePath)
        
        if 'rtpvxe' in conf and conf['rtpvxe']:
            for rtp in conf['rtpvxe']:
                run_cmd("cp %s/%s ./romfs/" % (vsb_path, rtp))
            
        if 'vxconf' in conf and 'RTNET_RTP' not in conf['vxconf']: 
            run_cmd('vxprj parameter setstring RTNET_JSON_FILE "/romfs/%s"' % vlmTargetJsons[board][i])
        
        run_cmd("vxprj build")
        os.chdir(prj_path)

        # cp uVxWorks and imx6q-sabrelite.dtb to _image/tN directory
        if board in vlmTargets:
            image_path = prj_path + '/%s_image' % board
            if not os.path.exists(image_path):
                print sudo('mkdir -p %s' % image_path)
            target_path = image_path + '/t%s' % i
            if not os.path.exists(target_path):
                print sudo('mkdir -p %s' % target_path)
            print sudo('cp -f %s %s' % (vip_path + '/default/%s' % vlmTargets[board]['image'], target_path))
            if board != 'itl_generic':
                print sudo('cp -f %s %s' % (vip_path + '/default/%s' % vlmTargets[board]['dtb'], target_path))
                print sudo('cp -f %s %s' % (vip_path + '/default/vxWorks.bin', target_path))
    
    restore_work_around_file(pkgs_path)
    return
     
def vxworks_rtp (board, conf, prj_path, wrenv_cmd, pkgs_path):
    def run_cmd(x):
        print(">>>>>> " + wrenv_cmd + x)
        lines = sudo(wrenv_cmd + x + " 2>&1")
        for line in lines: print line
        return lines
        
    os.chdir(prj_path)
    rtpCmd = "wrtool -data %s prj rtp create -vsb %s_vsb %s_rtp" % (prj_path, board, board)
    run_cmd (rtpCmd)
    os.chdir("%s_rtp" % board)
    
    print getoutput("sudo rm -fr rtp.c")
    
    for file in conf['rtpfile']:
        filePath = get_dvd_fullpath(pkgs_path, file)
        rtpCmd = 'wrtool -data %s prj file add %s' % (prj_path,filePath)
        run_cmd(rtpCmd)  
    
    #add libraries
    if 'rtplib' in conf:
        for lib in conf['rtplib']:
            rtpCmd = 'wrtool -data %s prj lib add %s' % (prj_path,lib)
            run_cmd(rtpCmd)  
            
    #prj build
    rtpCmd = 'wrtool -data %s prj build' % (prj_path)
    run_cmd(rtpCmd)  
    
    rtpCmd = 'wrtool -data %s prj buildtarget listpath' % (prj_path)
    ret = run_cmd(rtpCmd)
    
    return ret[0].strip('\n'); #get the rtp path
        
def vxworks_ipnet(conf,
            cflags, log, board, installpath, cvsbuild, logpath,
            wrenv, smp, m64bit, speed, shell, debug, ipv4only,
            ipv6only, target, tool,
            edr,bridgeports,
            scratchdir = '/tmp/buildunions/'):

    pkgs_path, wrenv_prefix = get_vxworks_env(installpath)
    wrenv_cmd = "%s LM_LICENSE_FILE=27000@ala-lic4.wrs.com " % wrenv_prefix
    #wrenv_cmd = "%s/wrenv.linux -p vxworks-%s LM_LICENSE_FILE=/net/pek-cdftp/pek-cdftp1/ftp/r1/license/WRSLicense.lic " % (installpath, wrenv)
    def run_cmd(x):
        print(">>>>>> " + wrenv_cmd + x)
        lines = sudo(wrenv_cmd + x + " 2>&1")
        for line in lines: print line

    if not ipv4only:
        inet6 = " -inet6"
    else:
        inet6 = ""
    debugopts = ''

    prj_path = os.getcwd()

    # Create default VSB
    [os.remove(x) for x in get_layer_file(prj_path)]
    
    run_cmd("vxprj vsb create -force -bsp %s -S %s_vsb" % (get_bsp_name(board), board))
    os.system("cp %s_vsb/vsb.config %s/vsb.config.tem" % (board, prj_path))
    s = open(os.path.join(prj_path, "vsb.config.tem")).read()
    s += "\n\n\n\n"

    # Add VSB configuration
    if 'vxmake' in conf:
        for c in conf['vxmake']: #[]
            s += "_WRS_CONFIG_COMPONENT_" + c.upper() + "=y\n"
    if 'vxconf' in conf:
        for c in conf['vxconf']: #[]
            s += "_WRS_CONFIG_" + c.upper() + "=y\n"

    # Add CFLAGS
    cflags.append('-DIPCOM_RAM_DISK_NO_BLOCK=4096 -DIP_USE_TRADITIONAL_STRERROR -DIPTESTENGINE')
    extra_defines = " ".join(cflags)
    s += '_WRS_CONFIG_ADDEDCFLAGS="%s"\n' % extra_defines
    s += '_WRS_CONFIG_ADDEDCFLAGS2="%s"\n' % extra_defines
    s += '_WRS_CONFIG_ADDEDCFLAGS_APP="%s"\n' % extra_defines

    # Disable USR libraries
    s += "_WRS_CONFIG_FEATURE_USR=n\n"

    # Disable OpenSSL
    #s += "_WRS_CONFIG_OPENSSL_CRYPTO=n\n"
    s += "_WRS_CONFIG_DEBUG_AGENT=n\n"
    s += "_WRS_CONFIG_SEC_CRYPTO=y\n"

    # Simics board requires adding end driver when configuring the target at run time
    if board in simicsTargets:
        s += "_WRS_CONFIG_END_LIB=y\n"
        
    # Debug mode
    if not speed:
        print "------------------ DEBUG BUILD ---------------------------"
        s += "_WRS_CONFIG_BUILD_MODE_debug=y\n"
        s += "_WRS_CONFIG_DEBUG_FLAG=y\n"

    s = s.replace('-DIPCOM_USE_SHELL=IPCOM_SHELL_IPCOM', '')   # 3/19/2015 remove this IPCOM_SHELL to avoid build error
    f = open("%s/vsb.config.tem" % prj_path, "w")
    f.write(s)
    f.close()
    
    print '=== output vsb.config.tem'
    print getoutput("sudo cat %s/vsb.config.tem" % prj_path)

    # Create customized VSB
    run_cmd("vxprj vsb create -force -bsp %s -D vsb.config.tem %s_vsb" % (board, board))
    if smp:
        run_cmd("vxprj vsb config -s -add _WRS_CONFIG_SMP=y")
    else:
        run_cmd("vxprj vsb config -s -add _WRS_CONFIG_SMP=n")
    os.chdir("%s_vsb" % board)
    run_cmd("make -j %s" % multiprocessing.cpu_count())

    vxprj = 'vxprj create -vsb %s_vsb %s -c INCLUDE_NETSMP_CMD -c INCLUDE_ERRNOS_CMD -c INCLUDE_KEYADM_CMD -c INCLUDE_USER_DATABASE -c INCLUDE_SECURITY -c INCLUDE_HRFS -c INCLUDE_HRFS_FORMAT -c INCLUDE_RAM_DISK -c INCLUDE_DISK_UTIL -c INCLUDE_IPCOM_USE_RAM_DISK -c INCLUDE_DISK_UTIL_SHELL_CMD -c INCLUDE_IPQUEUE_CONFIG_CMD -c INCLUDE_IPSYSCTL_CMD -c INCLUDE_IPCOM_USE_TIME_CMD -c INCLUDE_IPCOM_SYSLOGD_CMD -c INCLUDE_IPCOM_SYSLOGD_USE_LOG_FILE -c INCLUDE_IPIFCONFIG_CMD -c INCLUDE_IPROUTE_CMD -c INCLUDE_HOST_TBL -c INCLUDE_IPCOM_SYSVAR_CMD -c INCLUDE_IPTCP_TEST_CMD -c INCLUDE_IPARP_CMD -c INCLUDE_IPVERSION_CMD -c INCLUDE_IPD_CMD -c INCLUDE_IPECHO_CLIENT_CMD -c INCLUDE_IPECHO_SERVER_CMD -c INCLUDE_IPSOCKTEST_CMD -c INCLUDE_IPPING_CMD -c INCLUDE_IPNET_PCAP_CMD -c INCLUDE_IPTELNETS -c INCLUDE_IPNET_IFCONFIG_1 -c INCLUDE_SHELL %s %s %s_vip -p IFCONFIG_1=\'"ifname eth0","devname driver","inet driver", "gateway driver"\' -p IPCOM_TELNET_PORT=\'"2323"\' -p IPRIP_IFCONFIG_1=\'"eth9 broadcast"\' -p NUM_FILES=1000 -p RTP_FD_NUM_MAX=100 -p SHELL_DEFAULT_CONFIG=\'"INTERPRETER=,LINE_EDIT_MODE=,LINE_LENGTH=4096,STRING_FREE=manual,VXE_PATH=.;/romfs"\' %s' % (board, inet6, board, tool, board, debugopts)
    if board == 'qsp_arm':
        vxprj += ' -profile PROFILE_DEVELOPMENT -c DRV_SIO_FDT_QSP'
    elif board == 'fsl_imx6':
        vxprj += ' -c INCLUDE_FSL_IMX6Q_SABRELITE'
    
    if not ipv4only:
        vxprj += " -c INCLUDE_IPNDP_CMD -c INCLUDE_IPPING6_CMD -c INCLUDE_IPRADVD_CMD"
        if 'vxprj6' in conf:
            for c in conf['vxprj6']:
                print "****"
                vxprj += " -c INCLUDE_" + c.upper()

    # Configure the bridge to come up at boot time
    if bridgeports:
        vxprj += ' -p BRIDGE_PORTS=\'"%s"\'' % bridgeports

    if smp:
        vxprj += ' -smp'
    if m64bit:
        vxprj += ' -lp64'
    for c in conf['vxprj']:
        # markus print "****"
        vxprj += " -c INCLUDE_" + c.upper()
    if 'vxparam' in conf:
        for c in conf['vxparam']:
            vxprj += " -p " + c
    os.chdir(prj_path)
    
    vxprj = vxprj.replace('-c INCLUDE_USE_IPCOM_SHELL', '') # 3/19/2015 remove this IPCOM_SHELL to avoid build error
    run_cmd(vxprj)
        
    # create a RTP application
    rtpApp = None
    if 'rtpfile' in conf and conf['rtpfile']:
        from filelock import FileLock
        with FileLock(wrtool_lock):
            print '=== lock rtp build'
            rtpApp = vxworks_rtp (board, conf, prj_path, wrenv_cmd, pkgs_path)
            time.sleep(30)  # need at least 20 seconds or the error "aborted" appears up
            print '=== unlock rtp build'
        os.chdir(prj_path)
            
    os.chdir("%s_vip" % board)

    # Create a user database with ftp:interpeak in ROMFS (Hash key as below)
    if 'vxconf' in conf and 'USER_MANAGEMENT' in conf['vxconf']:
        run_cmd("vxprj component add INCLUDE_ROMFS")
        os.system('sudo sh -c "mkdir romfs"')
       
        # udb v3 with ftp as normal account
        #os.system('sudo sh -c "echo 003 00000003 0004 J5k8hELcvnzoEjLERH1QvgXXHNYLNCNOBrg2rNtm+Uw= > romfs/udb"')        
        #os.system('sudo sh -c "echo 2 100 ftp w68+Ijdm2zU= wmepVE2M8teM+CCG2NuE04FX+cVXw03u8eJGz+olcSo= 0 0 0 0 0 1 0 >> romfs/udb"')
        #os.system('sudo sh -c "echo 3 100 ipssh EsUNoP0OncA= FJ7Pf51Q8j7/1xCE0Df/OuwYrejOC6Faug+0Hv9NmNY= 0 0 0 0 0 1 0 >> romfs/udb"')
        #os.system('sudo sh -c "echo 4 100 user567890123456789012345678901234567890 8LgC4vWC3AA= 7Ouv6WpSQz9nL6oJ7MLPKNn3y7zYfGI7Nl1PUsEIVGE= 0 0 0 0 0 1 0 >> romfs/udb"')

        # udb v3 with ftp as root account
        os.system('sudo sh -c "echo 003 00000003 0003 u533pOu660p6RzYRlmX3KBTEE8XhuwZUV2Zk2ETWVFQ= > romfs/udb"')        
        os.system('sudo sh -c "echo 1 1 ftp GP1nHTdm2zU= HuDJNP1SoaaOfdi3wORLK+yqxzgvXdEXzEmFNOIGFT0= 0 0 0 0 0 1 0 >> romfs/udb"')
        os.system('sudo sh -c "echo 2 100 ipssh mgGPjEES6ps= qMADTKzBogADqc/wl/CS5Fo9Ck6XSMxJ2F/ktXx3acw= 0 0 0 0 0 1 0 >> romfs/udb"')
        os.system('sudo sh -c "echo 3 100 user567890123456789012345678901234567890 1stMiVAZNQg= NKZERFsfS+gDmfTn24Uj5YIpPQOGUveHzOb6BpEwJ6Y= 0 0 0 0 0 1 0 >> romfs/udb"')
    
        # Set path to user database
        run_cmd("vxprj parameter setstring UDB_STORAGE_PATH /romfs/udb")
        # Set hash key for user database
        run_cmd("vxprj parameter setstring UDB_HASH_KEY \\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F\\\\x00\\\\x01\\\\x02\\\\x03\\\\x04\\\\x05\\\\x06\\\\x07\\\\x08\\\\x09\\\\x0A\\\\x0B\\\\x0C\\\\x0D\\\\x0E\\\\x0F")

    if 'vxprj' in conf and 'SSH' in conf['vxprj']:
        print '=== copy keys to /romfs'
        # support spin        
        ipnet_path = get_dvd_path(pkgs_path + '/net/ipnet')
        ssh_path = get_dvd_path(ipnet_path + '/ssh')
        keypath = ssh_path + '/test/keys'
        print getoutput('mkdir -p ./romfs')
        print getoutput('sudo cp %s %s' % (keypath + '/*', './romfs'))

    if conf['testengine_name'] == ['ipssh']:
        print '=== copy larger files to /romfs'
        # support spin
        file_path = get_dvd_path(ssh_path + '/test/sftp/largerfile')
        print getoutput('sudo cp %s %s' % (file_path, './romfs'))
        
    if conf['testengine_name'] == ['ipuserdb'] and 'overrided_usrAppInit' in conf:
        run_cmd("vxprj parameter setstring UDB_STORAGE_PATH /ram/udb")
        script_path = get_dvd_fullpath(pkgs_path, conf['overrided_usrAppInit'])
        cmd = 'sudo cp %s %s' % (script_path, 'usrAppInit.c')
        print '=== copy usrAppInit.c cmd:', cmd
        print getoutput(cmd)    

    if conf['testengine_name'] == ['userauthldap'] and 'config_file' in conf:
        script_path = get_dvd_fullpath(pkgs_path, conf['config_file'])
        cmd = 'sudo cp %s %s' % (script_path, './romfs/ldap_test.conf')
        run_cmd("vxprj parameter setstring AD_LDAP_CONFIGURATION_FILE /romfs/ldap_test.conf")
        print '=== copy ldap_test.conf cmd:', cmd
        print getoutput(cmd)    

    if conf['testengine_name'] == ['ipnat']:
        run_cmd("vxprj component remove INCLUDE_DEBUG_AGENT_START")

           
    # get EXTRA_DEFINE first to avoid replacing existing EXTRA_DEFINE
    lines = sudo(wrenv_cmd + ' vxprj buildmacro get %s_vip.wpj EXTRA_DEFINE' % board)
    print '=== existing EXTRA_DEFINE:', ' '.join(lines)
    extra_defines = "\'" + ' '.join(lines).replace('\n', ' ') + "".join(extra_defines)  + "\'"
    extra_defines = extra_defines.replace('-DIPCOM_USE_SHELL=IPCOM_SHELL_IPCOM', '')    # 3/19/2015 remove this IPCOM_SHELL to avoid build error
    run_cmd("vxprj buildmacro set EXTRA_DEFINE %s" % extra_defines)
    run_cmd("vxprj parameter setstring SEC_VAULT_KEY_ENCRYPTING_PW donald_duck")

    #add file for the vip
    if 'vxfile' in conf and conf['vxfile']:
        for file in conf['vxfile']:
            filePath = get_dvd_fullpath(pkgs_path, file)
            vxprj = 'vxprj file add %s' % (filePath)
            run_cmd(vxprj)

    # add rtp application to romfs
    if rtpApp is not None:
        print getoutput('sudo mkdir -p ./romfs')
        cmd = 'sudo cp %s %s' % (rtpApp, './romfs/rtp.vxe')
        print cmd
        print getoutput('sudo cp %s %s' % (rtpApp, './romfs/rtp.vxe'))
    
    # Build the VIP
    run_cmd("vxprj build")
    os.chdir(prj_path)
    
    # build dependent component, currently for SNTP_SERVER
    if 'depend' in conf:
        for component in conf['depend']:
            conf = testable_packages[component]
            cflags = conf['extra_build_cflags']

            # checkout source code 
            modules = testable_packages[component]['vc'] + ['iptestengine']
            dirname = pkgs_path + '/net/ipnet'
            dirname = get_dvd_path(dirname)  # support spin
            
            new_prj_path = prj_path + '/../' + component
            dependent_img = new_prj_path + '/vxsim_linux_vip/default/vxWorks'
            
            # handle the concurrency case
            if os.path.exists(new_prj_path):
                if os.path.exists(dependent_img):
                    os.system('sudo rm -fr %s' % new_prj_path)
                else:
                    counter = 0
                    while True:
                        if counter >= 720:
                            raise BuildException('failed to wait dependent component %s to get build completed' % component)
                            break
                        time.sleep(10)
                        print 'waiting the dependent component %s to get build completed' % component
                        counter += 1
                        if os.path.exists(dependent_img):
                            os.system('sudo rm -fr %s' % new_prj_path)
                            break
            
            os.system('mkdir -p %s' % new_prj_path)
            os.system('mkdir -p %s' % new_prj_path + '/cvs')
            for mod in modules:
                ret = walk_dir_to_copy(dirname, mod, new_prj_path + '/cvs')
                if ret != 2:
                    print '=== walk_dir_to_copy failed, mod is %s, return code is %s' % (mod, ret)

            # build dependent image
            os.chdir(new_prj_path)
            vxworks(conf,
                    cflags, log, board, installpath, cvsbuild, logpath,
                    wrenv, smp, m64bit, speed, shell, debug, ipv4only,
                    ipv6only, target, tool,
                    edr,bridgeports)
    return


# function copied from runtestsuite.py
def walk_dir_to_copy(dirname, mod_name, vdir='cvs'):
    elems = sorted( os.listdir(dirname) )
    for e in elems:
        if e == ".":
            continue
        if e == "..":
            continue
        if os.path.isfile(dirname + "/" + e):
            continue
        full_path = dirname + "/" + e
        if mod_name == 'ntp' and full_path.find("sntp") != -1:
            continue # Special case. There is a directory called ntp in the sntp component
        if mod_name == 'radius' and full_path.find("ike") != -1: 
            continue 
        if e == mod_name or e.startswith(mod_name + '-'): # support both git and spin
            if os.path.isdir(full_path + "/test"):
                print(" >>>>>>>>>>>>>>>>> copy directory " + full_path)
                #print("=== module:%s, directory:%s" % (mod_name, full_path.replace(dirname, '')))
                os.popen('cp -fr %s %s' % (full_path, vdir))
                # support spin
                git_full_path = remove_path_version(full_path)
                if git_full_path != full_path:
                    os.renames(vdir + '/' + os.path.basename(full_path), 
                               vdir + '/' + os.path.basename(git_full_path))                
                return 2
            else:
                if mod_name == "ipcrypto":
                    ret = walk_dir_to_copy(full_path, mod_name, vdir)
                    if ret > 0:
                        return ret
                print(" >>>>>>>>>>>>>>>>> failed copy directory " + full_path)
                return 1
        if os.path.isdir(full_path):
            #if mod_name == "ipcrypto":
            #    print ("!!!!!!!!!! full %s" % full_path)
            ret = walk_dir_to_copy(full_path, mod_name, vdir)
            if ret > 0:
                return ret
    return 0


def remove_path_version(the_path):
    tokens = filter(lambda x: x.strip() != '', the_path.split('/'))
    new_tokens = list(tokens)
    
    for i in xrange(len(tokens)):
        found = re.search('(.*?)-\d+.\d+.\d+.\d+', tokens[i])
        if found is not None:
            new_tokens[i] = found.groups()[0]
    if the_path[0] == '/':
        return '/' + '/'.join(new_tokens)
    else:
        return '/'.join(new_tokens)


def get_dvd_path(ipnet_dir):
    parent_dir = os.path.dirname(ipnet_dir)
    base_name = os.path.basename(ipnet_dir)
    for e in os.listdir(parent_dir):
        if e == base_name or e.startswith(base_name + '-'):
            return parent_dir + '/' + e
    raise BuildException('cannot find %s' % ipnet_dir)
    return ''


def get_dvd_fullpath(dvd_path, git_relative_path):
    new_path = dvd_path
    for d in [x for x in git_relative_path.split('/') if x.strip()]:
        new_path = get_dvd_path(new_path + '/' + d)
    return new_path

        
def main(args):
    import optparse
    p = optparse.OptionParser()
    p.add_option('--cflags', default = '', help = "defaults to '' (none)")
    p.add_option('--scratchdir', default = '/tmp/buildunions/', help = 'union mount will write here')
    p.add_option('--cvsbuild', help = 'replace components/ip_net2-6.6/ip* with cvs', action="store_true", default = False)
    p.add_option('--logpath', help = 'log files go where? (also puts project files here atm. fix!)')
    p.add_option('--workdir', default = 'IPNET') #!!! bad
    p.add_option('--shell', default = 'ipcom', help = 'ipcom or native')
    p.add_option('--debug', default = None, help = "tty or serial (or left out)")
    p.add_option('--ipv4only', default = False, action="store_true")
    p.add_option('--target', default = 'simlinux', help = 'eg. simlinux')
    p.add_option('--tool', default = 'gnu', help = 'eg. diab, gnu')
    p.add_option('--noedr', action="store_false", default = True, dest = 'edr')
    p.add_option('-t', help = 'what to test (IPAPPL, IPNET, etc from runtestsuite_conf.py')

    group = optparse.OptionGroup(p, "Required options")
    group.add_option('--board', default = "linux", help = 'avail: linux')
    group.add_option('--installpath', help = 'vxworks installation path, e.g. /usr/local/VxWorks6.6_VX36.07FA_MSP') # future: default will try to find one for you
    p.add_option_group(group)

    (o,_) = p.parse_args(args)
    o.cflags = [o.cflags]
    if not o.board:
        print "--board required"
        return
    if not o.installpath:
        print "--installpath required"
        return
    if not o.t:
        print "-t required"
        return
    import runtestsuite_conf
    if o.t not in runtestsuite_conf.testable_packages:
        print o.t + 'is not in runtestsuite_conf.py: "testable_packages"'
        return

    if o.debug:
        o.debug = {'mode': o.debug}

    def log(s):
        print s


    try:
        os.mkdir(o.t)
    except OSError:
        pass

    conf = runtestsuite_conf.testable_packages[o.t]
    if not o.logpath:
        o.logpath = os.path.join(os.getcwd(), o.t, 'vx_' + o.board)
    vxworks(conf,
            o.cflags, log, o.board,
            o.installpath, o.cvsbuild, o.logpath, "6.8", False, False,
            o.shell, o.debug, o.ipv4only,
            o.target, o.tool,
            o.edr, o.scratchdir)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
