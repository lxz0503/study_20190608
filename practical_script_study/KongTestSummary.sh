#!/bin/bash -x
date
id
hostname

BUILD_NUMBER=$1
BRANCH=$2
NEWCOMMIT=$3

echo $BUILD_NUMBER
echo $BRANCH
echo $NEWCOMMIT

GITPATH=/net/pek-vx-nightly3/buildarea1/svc-cmnet/vxworks # the 1st item in kongBuildServers at KongConfig.py
MYPATH=/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3
PATH=$PATH:/folk/lchen3/bin

export PYTHONPATH=/folk/lchen3/try/workspace/PMT/src
#export PATH=/folk/lchen3/package/opt/bin:$PATH
#export LD_LIBRARY_PATH=/folk/lchen3/package/opt/lib:$LD_LIBRARY_PATH
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin:/sbin:/usr/atria/bin:/folk/cm/bin:/folk/qms/tools:/folk/vlm/commandline:/folk/vlm/bin:/usr/X11R6/bin

echo "handle $BRANCH"
if [[ $BRANCH == "SPIN:"* ]]; then
    # handle spin
    spinPath=${BRANCH/SPIN:}
    if [ ! -d "$spinPath" ]; then
        echo "$spinPath not found"
        exit 1
    fi
else
    # handle branch
    cd $GITPATH
    pwd
    git branch
    git log -1 HEAD
fi    

$MYPATH/try/workspace/PdvTool/vx7tool/new/KongTestSummary.py $BUILD_NUMBER $BRANCH $NEWCOMMIT

