#!/bin/bash -x

# RunTest.sh $BRANCH $NEWCOMMIT $MODULE $TESTCASE $BSP
date
id
BRANCH=$1
NEWCOMMIT=$2
MODULE=$3
TESTCASE=$4
BSP=$5

SMP=--smp
#SMP=--up

GetKongBuildFirstFlag(){
    flag=`grep kongBuildFirstFlag /net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/try/workspace/PdvTool/vx7tool/new/KongConfig.py | cut -d" " -f3`
    if [[ $flag == "False" ]]
    then
        echo "False"
        return
    else
        echo "True"
        return
    fi
}

GetVMType() {
    hoststr=`hostname`
    buildFirstFlag=$(GetKongBuildFirstFlag)
    if [ "$buildFirstFlag" = "False" ]
    then
        echo "REMOTE_VM"
        return
    fi
    
    if [[ $hoststr == "kong-vm-"* ]]
    then
        echo "LOCAL_VM" # Bash knows only status codes (integers) and strings written to the stdout.
        return
    elif [[ $hoststr == "kong-vm-tis-"* ]]
    then
        #echo "REMOTE_VM"
        echo "LOCAL_VM"
        return        
    elif [[ $hoststr == "kong-rvm-"* ]]
    then
        #echo "REMOTE_VM"
        echo "LOCAL_VM"
        return
    elif [[ $hoststr == "pek-testharness-s1" ]] # real machine, regarded as local vm
    then
        echo "LOCAL_VM"
        return
    else
        echo "UNKNOWN_VM"
        return
    fi
}

NeedSetuptool() {
    # must be used after git pull
    ret=`git status | grep "modified:" | grep "new commits" | sed "s/ //g"`
    if test -z "$ret"
    then
        echo "False"
        return
    else
        echo "True"
        return
    fi
}

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

# function to clean up Kong environment
cleanUpKongEnv(){
  kongIf=`ip link | grep "^[0-9]*: rs" | awk 'BEGIN{FS=":"} {print $2}'`

  echo $kongIf

  if [ "$kongIf" != "" ]; then
    echo "not blank"
    ip link | grep "^[0-9]*: rs" | awk 'BEGIN{FS=":"} {print $2}' | xargs -i -t sudo ip link delete {}
  else
    echo "blank"
  fi

  sudo pkill vxsim
  sudo pkill uml_switch
  sudo pkill telnet
  sudo pkill -f runtestsuite.py
  sudo pkill -f iptestengine.py

  sleep 6
  ps -eaf | grep -E "vxsim|uml" | grep -v grep
  ip link
  brctl show
}

# delete all the other subdirs with the same parent dir as $WORKSPACE except the current dir
cd ${WORKSPACE}
ls -l ../ | grep -v `basename \`pwd\`` | awk '{print $9}' | grep -v ^$ | xargs -t -i sudo rm -fr ../{} 
# delete all under $WORKSPACE
sudo rm -fr *

cleanUpKongEnv

hoststr=`hostname`
if [[ $hoststr == "kong-vm-tis-"* ]]
then
	GITPATH=/home/ubuntu/vxworks
elif [[ $hoststr == "kong-rvm-"* ]]
then
	GITPATH=/home/revo/vxworks
elif [[ $hoststr == "pek-testharness-s1" ]]
then
	GITPATH=/home/testadmin/vxworks	
else
	echo "UNKNOWN_VM"
	GITPATH=/home/${USER}/vxworks
fi

if [[ $NEWCOMMIT == "653SPIN" ]]; then
    vxversion=653
else
    vxversion=7
fi

#must use /net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/try/workspace/PdvTool/vx7tool/new
#instead of /folk/lchen3/try/workspace/PdvTool/vx7tool/new
export PYTHONPATH=/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/try/workspace/PdvTool/vx7tool/new

SCRIPTPATH=$GITPATH/vxworks-$vxversion/pkgs/net/ipnet/coreip/src/ipcom/util/scripts
# NOTE: IMAGEPATH must be the same as kongImageDir at KongConfig.py
#IMAGEPATH=/net/pek-sec-kong-02.wrs.com/workspace/svc-cmnet/IMAGES
IMAGEHOST=`python -c "import KongConfig; print KongConfig.GetImageServer()"`
IMAGEPATH=/net/$IMAGEHOST/`python -c "import KongConfig; print KongConfig.GetImageDir()"`

vm_type=$(GetVMType)
echo $vm_type


if [[ $vm_type == "LOCAL_VM" ]]
then
    echo "local vm: copy built module"
    
    # copy a tar package made by build to local/remote vm
    pwd
    cp ${IMAGEPATH}/${BSP}/${MODULE}.tar .
    tar zxf ${MODULE}.tar
    if [[ $MODULE == "SNTP_SERVER" ]]; then
        time cp ${IMAGEPATH}/${BSP}/SNTP_CLIENT.tar .
        time tar zxf SNTP_CLIENT.tar
    fi

    if [[ $BRANCH == "SPIN:"* ]]; then
        # handle spin
        if [[ `hostname` == $IMAGEHOST ]]; then
            spinPath=${BRANCH/SPIN:}
        else
            spinPath=/net/$IMAGEHOST/${BRANCH/SPIN:}
        fi
        GITPATH=$spinPath
        PKGSPATH=$(GetPkgsPath $GITPATH)
        searchPath=$PKGSPATH/net
        
        if true; then
            # method 1 : use runtestsuite*.py within the tar package to speed up testing
            mv ${WORKSPACE}/$MODULE/runtestsuite*.py ${WORKSPACE}
            mv ${WORKSPACE}/$MODULE/lockboard.py     ${WORKSPACE}
            mv ${WORKSPACE}/$MODULE/vlmTarget.py     ${WORKSPACE}
            mv ${WORKSPACE}/$MODULE/shellUtils.py    ${WORKSPACE}
            SCRIPTPATH=${WORKSPACE}                  
        else
            # method 2 : search runtestsuite.py since the path has version info
            rtn=`find $searchPath -name runtestsuite.py`
            if [ "$rtn" = "" ]; then
                echo "cannot find runtestsuite.py at the spin"
                exit 1
            else
                SCRIPTPATH=`dirname $rtn`
            fi
        fi
    else
        # handle git branch
        spinPath=/net/pek-sec-kong-02.wrs.com/workspace/svc-cmnet/vxworks
        GITPATH=$spinPath
        
        # use runtestsuite*.py within the tar package for testing
        mv ${WORKSPACE}/$MODULE/runtestsuite*.py ${WORKSPACE}
        mv ${WORKSPACE}/$MODULE/lockboard.py     ${WORKSPACE}
        mv ${WORKSPACE}/$MODULE/vlmTarget.py     ${WORKSPACE}
        mv ${WORKSPACE}/$MODULE/shellUtils.py    ${WORKSPACE}
        SCRIPTPATH=${WORKSPACE}
    fi
elif [[ $vm_type == "REMOTE_VM" ]]
then
    echo "remote vm: build and then test"
    cd $GITPATH
    git branch

    # remove all the changes for current branch so that changing to vx7-cert can be successfully
    git reset --hard HEAD 
    # git pull at vx7-cert to get latest branch names
    git checkout vx7-release
    git pull
    # remove the local existed branch in case that remote branch re-creates
    if [ "$BRANCH" != "vx7-release" ]; then
        # note: cat has to be added to the end of this pipe, or grep might generate -1 and all script gets exit here
        BranchName=`git branch | grep -w $BRANCH | cat`
        if [ "$BranchName" != "" ]; then
            echo "found $BRANCH"
            git branch -D $BRANCH
        else
            echo "not found $BRANCH"
        fi
    fi

    git checkout $BRANCH
    git pull

    # setup-tools has to be run sometimes or build gets failed
    need_setuptool=$(NeedSetuptool)
    echo $need_setuptool
    if [ "$need_setuptool" = "True" ]
    then
        ./setup-tools -clean
        ./setup-tools
    else
        echo "no need to run setup-tool"
    fi

    found=`git log | grep $NEWCOMMIT`
    if [ "$found" = "" ]
    then
        echo "not found $COMMIT at the branch $BRANCH"
        exit 1
    fi
    echo "use the commit $COMMIT"
    #git pull
    git reset --hard $NEWCOMMIT

    # show current branch and commit
    git branch | grep ^\*
    git log -1 HEAD

    cd -
else
    echo "unknown vm: exit"
    exit 1
fi

if [[ $vm_type == "LOCAL_VM" ]]
then
    VAR_ARG="--no-rebuild"
else
    VAR_ARG="-c"
fi

# make sure IPNET using pexpect 0.99
if [ "$MODULE" = "IPNET" ]
then
    export PYTHONPATH=$SCRIPTPATH:$PYTHONPATH
fi

# BOND using 3 networks
if [ "$MODULE" = "BOND" ]
then
    VAR_ARG="$VAR_ARG --networks 3"
fi

TIMEOUTCMD="timeout -s SIGKILL 7200"

if [ "$BSP" = "vxsim_linux" ]; then            
    if [ "$TESTCASE" = "ALL" ]
    then
        $TIMEOUTCMD $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --vxworks="board=$BSP,target=simlinux,version=7,wrenv=$vxversion,path=$GITPATH" --speed $SMP $MODULE ${VAR_ARG}
    else
        $TIMEOUTCMD $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --vxworks="board=$BSP,target=simlinux,version=7,wrenv=$vxversion,path=$GITPATH" --speed $SMP $MODULE ${VAR_ARG} -n $TESTCASE
    fi
elif [ "$BSP" = "fsl_imx6" ]; then
    TARGET=ARMARCH7
    MODIMAGEPATH=$WORKSPACE/${MODULE}/${BSP}_image
    TFTPSERVER=128.224.153.34 # pek-vx-nwk1.wrs.com
    TFTPPATH=/folk/svc-cmnet/tftpboot/${BSP}/${MODULE}
    VLMTARGETS="25002,25003"
    VLMTARGETNUM=2    

    rm -fr $TFTPPATH
    mkdir -p $TFTPPATH

    /folk/vlm/commandline/vlmTool forceUnreserve -s amazon.wrs.com -t 25002 -Z lchen3 -P wrslchen3
    /folk/vlm/commandline/vlmTool forceUnreserve -s amazon.wrs.com -t 25003 -Z lchen3 -P wrslchen3
    
    if [ "$TESTCASE" = "ALL" ]
    then
        $TIMEOUTCMD $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=$VLMTARGETNUM --vlmtargets="$VLMTARGETS" --supports=mipl --target-speed=50 --vxworks="board=$BSP,imagepath=$MODIMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$GITPATH,tty=/dev/ttyS0" --speed $SMP $MODULE ${VAR_ARG}
    else
        $TIMEOUTCMD $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=$VLMTARGETNUM --vlmtargets="$VLMTARGETS" --supports=mipl --target-speed=50 --vxworks="board=$BSP,imagepath=$MODIMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$GITPATH,tty=/dev/ttyS0" --speed $SMP $MODULE ${VAR_ARG} -n $TESTCASE        
    fi    
elif [ "$BSP" = "itl_generic" ]; then
    TARGET=NEHALEM
    MODIMAGEPATH=$WORKSPACE/${MODULE}/${BSP}_image
    TFTPSERVER=128.224.153.34 # pek-vx-nwk1.wrs.com
    TFTPPATH=/folk/svc-cmnet/tftpboot/${BSP}/${MODULE}
    VLMTARGETS="28525,28526"
    VLMTARGETNUM=2    
    rm -fr $TFTPPATH
    mkdir -p $TFTPPATH

    /folk/vlm/commandline/vlmTool forceUnreserve -s amazon.wrs.com -t 28525 -Z lchen3 -P wrslchen3
    /folk/vlm/commandline/vlmTool forceUnreserve -s amazon.wrs.com -t 28526 -Z lchen3 -P wrslchen3

    if [ "$TESTCASE" = "ALL" ]
    then
        $TIMEOUTCMD $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=$VLMTARGETNUM --vlmtargets="$VLMTARGETS" --supports=mipl --target-speed=50 --vxworks="board=$BSP,imagepath=$MODIMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$GITPATH,tty=/dev/ttyS0" --speed $SMP $MODULE ${VAR_ARG}
    else
        $TIMEOUTCMD $SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=$VLMTARGETNUM --vlmtargets="$VLMTARGETS" --supports=mipl --target-speed=50 --vxworks="board=$BSP,imagepath=$MODIMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$GITPATH,tty=/dev/ttyS0" --speed $SMP $MODULE ${VAR_ARG} -n $TESTCASE
    fi    
fi     
    

