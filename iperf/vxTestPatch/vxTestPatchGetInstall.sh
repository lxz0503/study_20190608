#! /bin/bash
# Copyright 2016, 2018 Wind River Systems, Inc.
#
## USAGE: vxTestPatchGetInstall.sh [-windHome spinHomeDir] -gitPath gitHomeDir -b branchName [-notChkGit] [-update|-updateMakefile] [-tag tagName]
# "-windHome"
# "  The Spin installed directory"
# "-gitPath "
# "  The git home path "
# "-b "
# "  The branch name "
# "-update "
# "  If the VxWorks Release version less than or equal to SR0470(June 2016 Release), vxTest not a layer, MUST add this parameter"
# "-notChkGit "
# "  only used for the Execute script user name is not the same as git owner,then only collect the vxTest code, \
#    not case whether the git is up-to-date, the git code status must be confirmed by the current user."
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
# modification history
# 12dec18,zjl  update for installing parallel with tag
# 07dec18,zjl  added git checkout to the tag for the spin
# 27jun18,zjl  update for common use(such as vx653-42/SR05XX)
# 19jun18,zjl  update for SR0600 Black Oak Platform directory structure 
# 28mar18,zjl  use package name to replace the hard code vxworks-7
# 26jul16,zjl  generate tmp files to windHome instead of currnet path
# 25jul16,zjl  add windHome for vx7PatchInstall.sh
# 18jul16,zjl  adapt for vxTest as a sub-layer.
# 05jul16,zjl  Written.


sourcePath=$(cd $(dirname $0); pwd)

windHome=""
gitPath=""
branchName=""
updateMakefile=0
notChkGit=0
tagName=""

usage() {
    echo "usage:"
    echo "vxTestPatchGetInstall.sh [-windHome spinHomeDir] -gitPath gitHomeDir -b branchName [-notChkGit] [-tag tagName|spinName]"
    echo "-windHome"
    echo "  The Spin installed directory"
    echo "-gitPath "
    echo "  The git home path"
    echo "-b "
    echo "  The branch name"
    echo "-tag "
    echo "  The tag name"
    echo "-notChkGit "
    echo "  only used for the Execute script user name is not the same as git owner,then only collect the vxTest code, \
not care whether the git is up-to-date, the git code status must be confirmed by the current user."
}

while [ $# -gt 0 ]; do
    case $1 in
        -windHome) shift; windHome=$1 ;;
        -gitPath) shift; gitPath=$1 ;;
        -b|-branch) shift; branchName=$1 ;;
        -tag) shift; tagName=$1 ;;
        -notChkGit) notChkGit=1 ;;
        -help|-h|--help) usage;exit 1 ;;
        *) echo "invalid parameter '$1',See usage help." >&2; usage;exit 1;;
    esac
    shift
done

if [ -z "$gitPath" ]
then
    echo "ERROR: -gitPath switch is required. See usage."
    usage
    exit 1
elif [ ! -d $gitPath ]
then
    echo "ERROR: gitPath:$gitPath is not a folder, please check"
    exit 1
fi

if [ -z "$branchName" ]
then
    echo "ERROR: -b switch is required. See usage."
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

#------------------------ Main ------------------------
git=`which git`
if [ -z "$git" ]
then
    echo "no git command in your host,please check"
    exit 1
fi

cd $gitPath
if $git status |grep "fatal: Not a git repository" >/dev/null
then
    echo "ERROR: gitPath:$gitPath is not a git repository,please check"
    exit 1
fi

gitTag=""
isInTagEnv=0

if [ -n "$tagName" ];then
    if echo $tagName |grep ^vx >/dev/null;then
        tmpTag=${tagName/vx/}
    else
        tmpTag=$tagName
    fi

    if $git tag |grep -w $tmpTag;then
        echo "Found the git tag:$tmpTag"
        gitTag=$tmpTag
    else
        echo "Not found the tag you supplied"
    fi
fi

if [ -n "$gitTag" ];then
    if $git branch |grep "^*" |grep -w "$gitTag" >/dev/null;then
        echo "Already in git tag: $gitTag env"
        isInTagEnv=1
    fi
fi

if [ $isInTagEnv -ne 1 ];then
    if ! $git branch |grep "* ${branchName}$" >/dev/null
    then
        if [ $notChkGit -eq 1 ];then
            echo "The current branch name is not $branchName, please check. Exit"
            exit 1
        else
            echo "The current branch name is not $branchName, will checkout to $branchName"
            $git checkout $branchName
            if [ $? -ne 0 ]
            then
                echo "git checkout to $branchName failed, please check whether the branch name is correct or whether some conflicts found.Exit"
                exit 1
            fi

        fi
    fi

    if [ $notChkGit -ne 1 ];then
        if $git pull |egrep 'error:|Aborting'
        then
            echo "branch $branchName execute pull command failed, Error or conflicts found.Exit"
            exit 1
        fi

        if [ -n "$gitTag" ];then
            $git checkout $gitTag
            if [ $? -ne 0 ]
            then
                echo "git checkout to tag:$gitTag failed, please check whether the tag name is correct or whether some conflicts found.Exit"
                exit 1
            fi
        fi
    fi
fi

cd -

platformName=$(ls $gitPath |grep -Po "vxworks-([0-9]+)")

if [ -z "$platformName" ];then
    platformName=$(ls $gitPath/helix/guests |grep -Po "vxworks-([0-9]+)")

    if [ -n "$platformName" ];then
        cd $gitPath/helix/guests/$platformName/
    else
        echo "$gitPath/helix/guests/$platformName not exist,exit"
        exit 1
    fi
else
    cd $gitPath/$platformName
fi

find . -name vxTest|egrep -v 'workspace|samples' >$windHome/vxTest.patch.tmp$$
if [ -f connectivity/usb/common.vxconfig ];then
    echo "connectivity/usb/common.vxconfig" >>$windHome/vxTest.patch.tmp$$
fi

tm=`date +%Y%m%d`
[ -f $windHome/vx7-vxTest-patch_$tm.zip ] && rm -rf $windHome/vx7-vxTest-patch_$tm.zip
cat $windHome/vxTest.patch.tmp$$ | xargs zip -r $windHome/vx7-vxTest-patch_$tm.zip 2>&1 >/dev/null
zip -d $windHome/vx7-vxTest-patch_$tm.zip pkgs_v2/os/arch/ia/vxTest/user_src/fpuTest_rtp/\*
rm -rf $windHome/vxTest.patch.tmp$$

cd -

$sourcePath/vx7PatchInstall.sh -windHome $windHome -f $windHome/vx7-vxTest-patch_$tm.zip

rm -rf $windHome/vx7-vxTest-patch_$tm.zip

exit 0
