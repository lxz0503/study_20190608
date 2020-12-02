#! /bin/bash

# Copyright 2015-2016 Wind River Systems, Inc.
#
## USAGE: updateVxtestBuild.sh [-homeBase gitBranchHomeDir(SpinHome)]
# "-homeBase"
# "  The Spin or git installed directory"
    
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
# modification history
# --------------------
# 05jul16,zjl  fix fs core common fail issue
# 31may16,zjl  add dsi_kernel
# 12apr16,zjl  fix V7SP-1199
# 04mar16,zjl  fix spell error
# 03mar16,zjl  fix update os/drv/vxbus/drv/Makefile issue(V7TST-199)
# 25feb16,zjl  update for container with version
# 03feb16,zjl  remove libc Makefile update
# 01feb16,zjl  only update the Makefile without VXTEST_BUILD
# 30dec15,zjl  remove vxdbg Makefile update
# 20nov15,zjl  add ui testcase
# 14oct15,luk  add drv testcase
# 13oct15,zjl  add safety testcase
# 17jul15,zjl  Fix one layer multi versions issue.
# 13jul15,zjl  Fix no env but using $WIND_HOME without throwing exception issue.
# 29jun15,zjl  add usb/can Makefile handler and update usage.
# 16jun15,zjl  Fix tmp file tmpVxtestBuild Permission denied issue.
# 09apr15,zjl  Written.

homeBase=""

usage() {
    echo "usage:"
    echo "method1: Set the env firstly and execute the script $0 without parameter:$0"
    echo "method2: $0 -homeBase gitBranchHomeDir(SpinHome) without setting the env"
}

if [ $# -eq 0 ];then
    if [ "$WIND_HOME" == "" ] || echo $WIND_HOME >/dev/null |grep "Undefined variable" 
    then
        echo "Please set the env firstly and execute the script $0 without parameter"
        usage
        exit 1
    else
        homeBase=$WIND_HOME
    fi	
else
    while [ $# -gt 0 ]; do
        case $1 in
            -homeBase) shift; homeBase=$1;;
            -help|-h|--help) usage;exit 1;;
                    *) echo "invalid parameter '$1',See usage help." >&2; usage;exit 1;;
        esac
        shift
    done
fi

if [ ! -d $homeBase -o -z "$homeBase" ];then
    echo "WIND_HOME:$homeBase is not exist,please check! or set the env and execute the script $0 without parameter"
    exit 1
fi

#if cat $homeBase/vxworks-7/${WIND_PKGS_DIR_NAME}/os/core/kernel*/Makefile |grep _WRS_CONFIG_VXTEST_BUILD >/dev/null;then
#	echo "You already update the Makefile for testing Done! exit"
#	exit 0
#fi

######################################################################################
mainEntry () {
    local tmpFile=$1
    local suite=$2
    local tmpVxtestBuild=/tmp/tmpVxtestBuild$$	
    
    if [ -f $homeBase/$tmpFile ];then
        if cat $homeBase/$tmpFile|grep "VXTEST_BUILD" >/dev/null;then
            return
        fi

        echo "######### update $tmpFile ......"
        lastLine=`cat -n $homeBase/$tmpFile |grep include |tail -n1 |awk '{print $1}'`
        lastLine=`expr $lastLine - 1`
        [ -f $tmpVxtestBuild ] && rm -rf $tmpVxtestBuild
        sed -n "1,$lastLine"p $homeBase/$tmpFile >$tmpVxtestBuild
        if [ "$suite" == "suite1" ];then
            addVxtestBuild1 $tmpVxtestBuild
        elif [ "$suite" == "suite2" ];then
            addVxtestBuild2 $tmpVxtestBuild
        elif [ "$suite" == "suite3" ];then
            addVxtestBuild3 $tmpVxtestBuild
        elif [ "$suite" == "suite4" ];then
            addVxtestBuild4 $tmpVxtestBuild
        elif [ "$suite" == "suite5" ];then
            addVxtestBuild5 $tmpVxtestBuild
        elif [ "$suite" == "suite6" ];then
            addVxtestBuild6 $tmpVxtestBuild
        fi
		
        echo $(cat $homeBase/$tmpFile |grep include |tail -n1) >>$tmpVxtestBuild    
        chmod 777 $tmpVxtestBuild	
        mv -f $tmpVxtestBuild $homeBase/$tmpFile
    else
        echo "****** $homeBase/$tmpFile not exist"
    fi
}

suitesCaller () {
    suites=$1
    suiteType=$2
    
    for path in  $suites
    do
        dirPath=$(dirname $path)
        layername=$(basename $path)
        containerDir=$(dirname $dirPath)
        containerName=$(basename $dirPath)
        containerDirFolder=$(dirname $containerDir)
        containerDirName=$(basename $containerDir)

        for containerDirVer in `ls $homeBase/$containerDirFolder |grep $containerDirName`
        do
            for container in `ls $homeBase/$containerDirFolder/$containerDirVer |grep -w "$containerName"`
            do
                if ! ls $homeBase/$containerDirFolder/$containerDirVer/$container |grep $layername >/dev/null;then
                    continue
                fi

                for layer in `ls $homeBase/$containerDirFolder/$containerDirVer/$container |grep -w "$layername"`
                do
                    mainEntry $containerDirFolder/$containerDirVer/$container/$layer/Makefile $suiteType
                done
            done
        done
    done
}

######################################################################################
addVxtestBuild1 () { #io/rtp/syscalls
    local tmpFile=$1
    
    echo ""  >>$tmpFile
    echo "include \$(WIND_KRNL_MK)/defs.layers.mk" >>$tmpFile
    echo ""  >>$tmpFile
    echo "ifdef _WRS_CONFIG_VXTEST_BUILD" >>$tmpFile
    echo "BUILD_DIRS += vxTest" >>$tmpFile
    echo "POST_NOBUILD_CDFDIRS += vxTest/cdf" >>$tmpFile
    echo "POSTBUILD_RTP_DIRS = vxTest" >>$tmpFile
    echo "endif" >>$tmpFile
    echo ""  >>$tmpFile
}

#io/rtp/syscalls
suites="vxworks-7/${WIND_PKGS_DIR_NAME}/os/core/io 
                vxworks-7/${WIND_PKGS_DIR_NAME}/os/core/rtp
                vxworks-7/${WIND_PKGS_DIR_NAME}/os/core/syscalls
                vxworks-7/${WIND_PKGS_DIR_NAME}/ipc/dsi/dsi_kernel
                vxworks-7/${WIND_PKGS_DIR_NAME}/os/drv/vxbus/drv"

suitesCaller "$suites" suite1

######################################################################################
addVxtestBuild2 () { #vxbus-core/vxbus-subsystem/vxbus_legacy/util-shell/util-boardlib
    local tmpFile=$1
    echo ""  >>$tmpFile
    echo "include \$(WIND_KRNL_MK)/defs.layers.mk" >>$tmpFile
    echo ""  >>$tmpFile
    echo "ifdef _WRS_CONFIG_VXTEST_BUILD" >>$tmpFile
    echo "BUILD_DIRS += vxTest" >>$tmpFile
    echo "POST_NOBUILD_CDFDIRS += vxTest/cdf" >>$tmpFile
    echo "endif" >>$tmpFile
    echo ""  >>$tmpFile
}

#vxbus-core/vxbus-subsystem/vxbus_legacy/util-shell/util-boardlib/ui
suites="vxworks-7/${WIND_PKGS_DIR_NAME}/os/drv/vxbus/core
                vxworks-7/${WIND_PKGS_DIR_NAME}/os/drv/vxbus/subsystem
                vxworks-7/${WIND_PKGS_DIR_NAME}/os/drv/vxbus_legacy
                vxworks-7/${WIND_PKGS_DIR_NAME}/os/utils/shell
                vxworks-7/${WIND_PKGS_DIR_NAME}/os/utils/boardlib
                vxworks-7/${WIND_PKGS_DIR_NAME}/ui/audio/lib
                vxworks-7/${WIND_PKGS_DIR_NAME}/ui/evdev/lib"

suitesCaller "$suites" suite2

######################################################################################
addVxtestBuild3 () { #fs
    local tmpFile=$1
    echo ""  >>$tmpFile
    echo "include \$(WIND_KRNL_MK)/defs.layers.mk" >>$tmpFile
    echo ""  >>$tmpFile
    echo "ifdef _WRS_CONFIG_VXTEST_BUILD" >>$tmpFile
    echo "BUILD_DIRS += vxTest" >>$tmpFile
    echo "PRE_NOBUILD_SHAREH_DIRS += vxTest/h" >>$tmpFile
    echo "POST_NOBUILD_CDFDIRS += vxTest/cdf" >>$tmpFile
    echo "POST_NOBUILD_CFGDIRS += vxTest/configlette" >>$tmpFile
    echo "endif" >>$tmpFile
    echo ""  >>$tmpFile
}

#fs/can/usb
suites="vxworks-7/${WIND_PKGS_DIR_NAME}/storage/fs/core/common
        vxworks-7/${WIND_PKGS_DIR_NAME}/connectivity/usb
        vxworks-7/${WIND_PKGS_DIR_NAME}/connectivity/can"

suitesCaller "$suites" suite3


######################################################################################

addVxtestBuild4 () { #kernel
    local tmpFile=$1
    echo ""  >>$tmpFile
    echo "include \$(WIND_KRNL_MK)/defs.layers.mk" >>$tmpFile
    echo ""  >>$tmpFile
    echo "ifdef _WRS_CONFIG_VXTEST_BUILD" >>$tmpFile
    echo "BUILD_DIRS += vxTest" >>$tmpFile
    echo "BUILD_USER_DIRS = vxTest/utils" >>$tmpFile
    echo "BUILD_USER_DIRS += vxTest/user_src/helper/shlStress/lib" >>$tmpFile
    echo "POSTBUILD_RTP_DIRS = vxTest" >>$tmpFile
    echo "PRE_NOBUILD_SHAREH_DIRS += vxTest/h" >>$tmpFile
    echo "POST_NOBUILD_CDFDIRS += vxTest/cdf" >>$tmpFile
    echo "POST_NOBUILD_CFGDIRS += vxTest/configlette" >>$tmpFile
    echo "endif" >>$tmpFile
    echo ""  >>$tmpFile
}


suites="vxworks-7/${WIND_PKGS_DIR_NAME}/os/core/kernel"

suitesCaller "$suites" suite4

######################################################################################

addVxtestBuild5 () { #safety
    local tmpFile=$1
    echo ""  >>$tmpFile
    echo "include \$(WIND_KRNL_MK)/defs.layers.mk" >>$tmpFile
    echo ""  >>$tmpFile
    echo "ifdef _WRS_CONFIG_VXTEST_BUILD" >>$tmpFile
    echo "KERNEL_PUBLIC_H_DIRS += vxTest/h" >>$tmpFile
    echo "BUILD_DIRS += vxTest" >>$tmpFile
    echo "POSTBUILD_RTP_DIRS = vxTest" >>$tmpFile
    echo "POST_NOBUILD_CDFDIRS += vxTest/cdf" >>$tmpFile
    echo "POST_NOBUILD_CFGDIRS += vxTest/configlette" >>$tmpFile
    echo "endif" >>$tmpFile
    echo ""  >>$tmpFile
}


suites="vxworks-7/${WIND_PKGS_DIR_NAME}/os/core/safety"

suitesCaller "$suites" suite5

######################################################################################

addVxtestBuild6 () { #arm 
    local tmpFile=$1
    echo ""  >>$tmpFile
    echo "include \$(WIND_KRNL_MK)/defs.layers.mk" >>$tmpFile
    echo ""  >>$tmpFile
    echo "ifdef _WRS_CONFIG_VXTEST_BUILD" >>$tmpFile
    echo "BUILD_DIRS += vxTest" >>$tmpFile
    echo "POST_NOBUILD_CDFDIRS += vxTest/cdf" >>$tmpFile
    echo "endif" >>$tmpFile
    echo ""  >>$tmpFile
}

#arm
suites="vxworks-7/${WIND_PKGS_DIR_NAME}/os/arch/arm"

suitesCaller "$suites" suite6

######################################################################################
#vxworks-7/build/misc/common.vxglobalconfig

vxglobalconfig=$homeBase/vxworks-7/build/misc/common.vxglobalconfig

if [ -f $vxglobalconfig ];then
    if cat $vxglobalconfig|grep "VXTEST_BUILD" >/dev/null;then
        exit
    fi
    
    echo "######### update vxworks-7/build/misc/common.vxglobalconfig ......"
    
    echo "" >>$vxglobalconfig
    
    echo "config VXTEST_BUILD" >>$vxglobalconfig
    echo "        bool \"Enable VxWorks Test Code Building\"" >>$vxglobalconfig
    echo "        default n" >>$vxglobalconfig
    echo "        help" >>$vxglobalconfig
    echo "            This feature enables VxWorks Test Code Building" >>$vxglobalconfig 
fi
