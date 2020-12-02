#!/bin/bash

nightlyScriptDir=/net/pek-vx-system1/buildarea1/yliu2/nightly
v7GitPath=/net/pek-vx-system1/buildarea1/yliu2/vxworks7
v7GitBranch=vx7-integration

spinConfFile=$nightlyScriptDir/vx7_nightly_spin.config
source $spinConfFile
spin=$NIGHTLYSPIN
if [ -z $spin ]; then
    echo -e "There is not new spin for nightly test"
    exit 0
fi

if [ ! -z $PatchBranch ]; then
    v7GitBranch=$PatchBranch
fi
spinPath=/net/pek-vx-system1/buildarea1/yliu2/nightly/$spin
echo -E "spin=$spin"
echo -E "spinPath=$spinPath"
echo -E "v7GitBranch=$PatchBranch"
cd $v7GitPath
git pull
$nightlyScriptDir/vxTestPatch/vxTestPatchGetInstall.sh -gitPath $v7GitPath -b $v7GitBranch -windHome $spinPath




