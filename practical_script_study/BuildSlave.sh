#!/bin/bash -x

# build image at each Jenkins slave
# and move the built image to ${IMAGEPATH}/${BSP}/${MODULE}

# function to decide which is pkg path
GetPkgsPath() {
    if [ -e $1/vxworks ]; then
        envstr=`ls $1/vxworks`
        PKGSPATH=`$1/wrenv.linux -p vxworks/$envstr env | grep WIND_PKGS= | sed 's/WIND_PKGS=//g'`
    elif [ -f $1/vxworks-7/pkgs_v2/net/ipnet*/coreip*/src/ipcom/util/scripts/runtestsuite.py ]; then
        PKGSPATH=$1/vxworks-7/pkgs_v2
    elif [ -f $1/helix/guests/vxworks-7/pkgs_v2/net/ipnet*/coreip*/src/ipcom/util/scripts/runtestsuite.py ]; then
        PKGSPATH=$1/helix/guests/vxworks-7/pkgs_v2
    elif [ -f $1/vxworks-653/pkgs/net/ipnet*/coreip*/src/ipcom/util/scripts/runtestsuite.py ]; then
        PKGSPATH=$1/vxworks-653/pkgs
    elif [ -f $1/vxworks-7/pkgs/net/ipnet*/coreip*/src/ipcom/util/scripts/runtestsuite.py ]; then
        PKGSPATH=$1/vxworks-7/pkgs    
    else
        echo "pkgs_v2 or pkgs path not found, check your 1 setting"
        exit 1
    fi
    echo $PKGSPATH
}

CheckBsp() {
    if [[ "$1" =~ ^(vxsim_linux|fsl_imx6|itl_generic)$ ]]; then
        echo "BSP=$1"
    else
        echo "$1 not supported"
        exit 1
    fi
}

date
id
hostname

echo $BRANCH
echo $NEWCOMMIT
echo $BSP
pwd

BSP=$BSP
CheckBsp $BSP

MODULE=$MODULE

TOOL=llvm
SMP=--smp
#SMP=--up

LIBOPATH=/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3

export PYTHONPATH=/folk/lchen3/try/workspace/PdvTool/vx7tool/new

CURRENTHOST=`hostname`
if [ "$CURRENTHOST" == "pek-vx-nwk1" ]; then
    export PATH=//usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin:/sbin:/usr/atria/bin:/folk/cm/bin:/folk/qms/tools:/folk/vlm/commandline:/folk/vlm/bin:/usr/X11R6/bin
elif [ "$CURRENTHOST" == "pek-vx-nightly3" ]; then
    export PATH=/folk/lchen3/bin:/usr/local/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/opt/rational/clearcase/linux_x86/bin:.
elif [ "$CURRENTHOST" == "pek-sec-kong-02" ]; then
    export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin:/sbin:/usr/atria/bin:/folk/cm/bin:/folk/qms/tools:/folk/vlm/commandline:/folk/vlm/bin:/usr/X11R6/bin
elif [ "$CURRENTHOST" == "pek-cc-pb02l" ]; then
    export PATH=/folk/lchen3/package/opt/bin:$PATH
    export LD_LIBRARY_PATH=/folk/lchen3/package/opt/lib:$LD_LIBRARY_PATH
else
    echo "$CURRENTHOST is not supported, exit"
    exit 1
fi

env | sort

# $IMAGEHOST should be the same for both /images and /*SPIN
IMAGEHOST=`python -c "import KongConfig; print KongConfig.GetImageServer()"`
IMAGEPATH=`python -c "import KongConfig; print KongConfig.GetImageDir()"`
GITPATH=`python -c "import KongConfig; print KongConfig.GetGitDir(\"$CURRENTHOST\")"`

if [[ $NEWCOMMIT == "653SPIN" ]]; then
    vxversion=653
    TOOL=gnu
else
    vxversion=7
fi

sudo rm -fr *

if [[ $BRANCH == "SPIN:"* ]]; then
    # handle spin
    # now pek-sec-kong-02.wrs.com is the server which installs with the spin to test
    if [[ $CURRENTHOST == $IMAGEHOST ]]; then
        spinPath=${BRANCH/SPIN:}
    else
        spinPath=/net/$IMAGEHOST/${BRANCH/SPIN:}
    fi

    PKGSPATH=$(GetPkgsPath $spinPath)
    searchPath=$PKGSPATH/net
    
    # search runtestsuite.py since the path has version info
    rtn=`find $searchPath -name runtestsuite.py`
    if [ "$rtn" = "" ]; then
        echo "cannot find runtestsuite.py at the spin"
        exit 1
    else
        SCRIPTPATH=`dirname $rtn`
    fi

    if [ "$BSP" = "vxsim_linux" ]; then            
        $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --vxworks="board=$BSP,target=simlinux,version=7,wrenv=$vxversion,path=$spinPath" --toolchain=$TOOL --speed $SMP -c $MODULE --buildonly  
    elif [ "$BSP" = "fsl_imx6" ]; then
        TARGET=ARMARCH7
        MODIMAGEPATH=$WORKSPACE/$MODULE/${BSP}_image
        TFTPSERVER=128.224.153.135 # pek-cc-pb05l.wrs.com
        TFTPPATH=/folk/svc-cmnet/tftpboot
        mkdir -p $MODIMAGEPATH
        
        $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=2 --vlmtargets="25002,25003" --supports=mipl --target-speed=50 --vxworks="board=$BSP,imagepath=$MODIMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$spinPath,tty=/dev/ttyS0" --toolchain=$TOOL --speed $SMP -c $MODULE --buildonly
    elif [ "$BSP" = "itl_generic" ]; then
        TARGET=NEHALEM
        MODIMAGEPATH=$WORKSPACE/$MODULE/${BSP}_image
        TFTPSERVER=128.224.153.135
        TFTPPATH=/folk/svc-cmnet/tftpboot
        mkdir -p $MODIMAGEPATH
            
        $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=2 --vlmtargets="28525,28526" --supports=mipl --target-speed=50 --vxworks="board=$BSP,imagepath=$MODIMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$spinPath,tty=/dev/ttyS0" --toolchain=$TOOL --64bit --speed $SMP -c $MODULE --buildonly
    fi      
else    
    # handle branch
    PKGSPATH=$(GetPkgsPath $GITPATH)
    SCRIPTPATH=$PKGSPATH/net/ipnet/coreip/src/ipcom/util/scripts
 
    # show current branch and commit
    cd $GITPATH
    git branch | grep ^\*
    git log -1 HEAD    
    
    cd $WORKSPACE
    if [ "$BSP" = "vxsim_linux" ]; then            
        $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --vxworks="board=$BSP,target=simlinux,version=7,wrenv=$vxversion,path=$GITPATH" --toolchain=$TOOL --speed $SMP -c $MODULE --buildonly  
    elif [ "$BSP" = "fsl_imx6" ]; then
        TARGET=ARMARCH7
        MODIMAGEPATH=$WORKSPACE/$MODULE/${BSP}_image
        TFTPSERVER=128.224.153.135 # pek-cc-pb05l.wrs.com
        TFTPPATH=/folk/svc-cmnet/tftpboot
        mkdir -p $MODIMAGEPATH
        
        $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=2 --vlmtargets="25002,25003" --supports=mipl --target-speed=50 --vxworks="board=$BSP,imagepath=$MODIMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$GITPATH,tty=/dev/ttyS0" --toolchain=$TOOL --speed $SMP -c $MODULE --buildonly
    elif [ "$BSP" = "itl_generic" ]; then
        TARGET=NEHALEM
        MODIMAGEPATH=$WORKSPACE/$MODULE/${BSP}_image
        TFTPSERVER=128.224.153.135
        TFTPPATH=/folk/svc-cmnet/tftpboot
        mkdir -p $MODIMAGEPATH
            
        $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=2 --vlmtargets="28525,28526" --supports=mipl --target-speed=50 --vxworks="board=$BSP,imagepath=$MODIMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$GITPATH,tty=/dev/ttyS0" --toolchain=$TOOL --64bit --speed $SMP -c $MODULE --buildonly
    fi
fi

if [ $? -eq 0 ]; then
    if [ "$CURRENTHOST" = "$IMAGEHOST" ]; then
        mv ${MODULE} ${IMAGEPATH}/${BSP}
        cp $SCRIPTPATH/runtestsuite*.py ${IMAGEPATH}/${BSP}/${MODULE}
        cp $SCRIPTPATH/lockboard.py     ${IMAGEPATH}/${BSP}/${MODULE}
        cp $SCRIPTPATH/vlmTarget.py     ${IMAGEPATH}/${BSP}/${MODULE}
        cp $SCRIPTPATH/shellUtils.py    ${IMAGEPATH}/${BSP}/${MODULE}
        if [ "$MODULE" = "SNTP_SERVER" ]; then # special handling for the component with dependency
            mv SNTP_CLIENT ${IMAGEPATH}/${BSP}
            cp $SCRIPTPATH/runtestsuite*.py ${IMAGEPATH}/${BSP}/SNTP_CLIENT
            cp $SCRIPTPATH/lockboard.py     ${IMAGEPATH}/${BSP}/SNTP_CLIENT
            cp $SCRIPTPATH/vlmTarget.py     ${IMAGEPATH}/${BSP}/SNTP_CLIENT
            cp $SCRIPTPATH/shellUtils.py    ${IMAGEPATH}/${BSP}/SNTP_CLIENT
        fi
    else
        sudo chown -R svc-cmnet ${MODULE}
        sudo chgrp -R users ${MODULE}
        mv ${MODULE} /net/$IMAGEHOST/${IMAGEPATH}/${BSP}
        cp $SCRIPTPATH/runtestsuite*.py /net/$IMAGEHOST/${IMAGEPATH}/${BSP}/${MODULE}
        cp $SCRIPTPATH/lockboard.py     /net/$IMAGEHOST/${IMAGEPATH}/${BSP}/${MODULE}
        cp $SCRIPTPATH/vlmTarget.py     /net/$IMAGEHOST/${IMAGEPATH}/${BSP}/${MODULE}
        cp $SCRIPTPATH/shellUtils.py    /net/$IMAGEHOST/${IMAGEPATH}/${BSP}/${MODULE}
        if [ "$MODULE" = "SNTP_SERVER" ]; then # special handling for the component with dependency
            sudo chown -R svc-cmnet SNTP_CLIENT
            sudo chgrp -R users SNTP_CLIENT
            mv SNTP_CLIENT /net/$IMAGEHOST/${IMAGEPATH}/${BSP}
            cp $SCRIPTPATH/runtestsuite*.py /net/$IMAGEHOST/${IMAGEPATH}/${BSP}/SNTP_CLIENT
            cp $SCRIPTPATH/lockboard.py     /net/$IMAGEHOST/${IMAGEPATH}/${BSP}/SNTP_CLIENT
            cp $SCRIPTPATH/vlmTarget.py     /net/$IMAGEHOST/${IMAGEPATH}/${BSP}/SNTP_CLIENT
            cp $SCRIPTPATH/shellUtils.py    /net/$IMAGEHOST/${IMAGEPATH}/${BSP}/SNTP_CLIENT
        fi        
    fi
else
    echo "Kong build failed"
    exit 1
fi
