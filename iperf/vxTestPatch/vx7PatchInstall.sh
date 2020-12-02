#! /bin/bash

# Copyright 2015-2016, 2018 Wind River Systems, Inc.
#
## USAGE: vx7PatchInstall.sh [-windHome spinHomeDir] -f xxx.zip [-update]
# "-windHome"
# "  The Spin installed directory"
# "-f "
# "  The patch path "
    
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
# modification history
# 29aug18,zjl  update for helix spin patch installation
# 27jun18,zjl  update for common use(such as vx653-42/SR05XX)
# 19jun18,zjl  update for SR0600 Black Oak Platform directory structure 
# 28mar18,zjl  use package name to replace the hard code vxworks-7
# 26jul16,zjl  generate tmp files to windHome instead of currnet path
# 18jul16,zjl  adapt for vxTest as a sub-layer.
# 05jul16,zjl  fix fs core common fail issue
# 28mar16,zjl  fix spell error
# 25feb15,zjl  update for container with version
# 05feb16,zjl  remove copy rules.vxTest.mk
# 01jul15,zjl  Fix get layer fail issue(ls instead of ls -al)
# 01jul15,zjl  Add update Makefile function
# 30jun15,zjl  Written.


sourcePath=$(cd $(dirname $0); pwd)

windHome=""
patchPath=""
platformName=""

usage() {
    echo "usage:"
    echo "vx7PatchInstall.sh [-windHome spinHomeDir] -f xxx.zip"
    echo "-windHome"
    echo "  The Spin installed directory"
    echo "-f "
    echo "  The patch path"
}

while [ $# -gt 0 ]; do
    case $1 in
        -windHome) shift; windHome=$1 ;;
        -f) shift; patchPath=$1 ;;
        -help|-h|--help) usage;exit 1 ;;
        *) echo "invalid parameter '$1',See usage help." >&2; usage;exit 1;;
    esac
    shift
done

if [ -z "$patchPath" ]
then
    echo "ERROR: -f switch is required. See usage."
    usage
    exit 1    
fi

if [ -z "$windHome" ];then
    windHome=$WIND_HOME
    if [ -z "$windHome" ];then
        echo "ERROR: Please set the env firstly or with -windHome parameter . See usage."
        usage
        exit 1
    fi
fi

[ -d $windHome/vxTestPatch ] || mkdir -p $windHome/vxTestPatch
chmod 777 $windHome/vxTestPatch

filename=$(basename $patchPath)
ext="${filename##*.}"

if [ "$ext" != "zip" ];then
    echo "ERROR: Please give a zip patch. See usage."
    [ -d $windHome/patch ] && rm -rf $windHome/vxTestPatch
    exit 1
fi

windBase=$WIND_BASE
platformName=$(ls $windHome |grep -Po "vxworks-([0-9]+)")
if [ -z "$windBase" ];then
    windBase=$windHome/helix/guests/vxworks-7
    if [ ! -d "$windBase" ];then
        if [ -n "$platformName" ];then
            windBase=$windHome/$platformName
        else
            windBase=$windHome/vxworks-7
        fi
    fi
fi

unzip -q $patchPath -d $windHome/vxTestPatch

cd $windHome/vxTestPatch

echo "Begin copy vxTest to respective layer......"
for path in `find . -name vxTest`
do
    dirPath=$(dirname $(dirname $path))
    layername=$(basename $(dirname $path))
    containerDir=$(dirname $dirPath)
    containerName=$(basename $dirPath)
    containerDirFolder=$(dirname $containerDir)
    containerDirName=$(basename $containerDir)

    for containerDirVer in `ls $windBase/$containerDirFolder |grep $containerDirName`
    do
        for container in `ls $windBase/$containerDirFolder/$containerDirVer|grep $containerName`
        do
            if ! ls $windBase/$containerDirFolder/$containerDirVer/$container |grep $layername >/dev/null;then
                continue
            fi
            #echo "-$layername"

            for layer in `ls $windBase/$containerDirFolder/$containerDirVer/$container |grep -w "$layername"`
            do
                echo "+$containerDirFolder/$containerDirVer/$container/$layer"
                if ls $windBase/$containerDirFolder/$containerDirVer/$container/$layer |grep vxTest >/dev/null
                then
                    for vxTestVer in `ls $windBase/$containerDirFolder/$containerDirVer/$container/$layer |grep vxTest`
                    do
                        cp -rf $windHome/vxTestPatch/$path/* $windBase/$containerDirFolder/$containerDirVer/$container/$layer/$vxTestVer/
                    done    
                else
                    cp -rf $windHome/vxTestPatch/$path $windBase/$containerDirFolder/$containerDirVer/$container/$layer/
                fi
            done
        done
    done
done

pkgDirName=$WIND_PKGS_DIR_NAME
if [ -z "$pkgDirName" ];then
    pkgDirName=pkgs_v2
fi

if  [ -f $windHome/vxTestPatch/$pkgDirName/connectivity/usb/common.vxconfig ];then
    echo "+$pkgDirName/connectivity/usb/common.vxconfig"
    for usb in `ls $windBase/$pkgDirName/connectivity |grep usb`
    do
        cp -f $windHome/vxTestPatch/$pkgDirName/connectivity/usb/common.vxconfig $windBase/$pkgDirName/connectivity/$usb/
    done
fi

echo "End copy vxTest to layers......"

cd -

[ -d $windHome/vxTestPatch ] && rm -rf $windHome/vxTestPatch

exit 0
