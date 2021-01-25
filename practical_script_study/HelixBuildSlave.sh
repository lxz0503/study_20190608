#!/bin/bash -x

date
id
hostname
pwd

echo $BRANCH
echo $NEWCOMMIT
echo $MODULE
echo $BSP

scriptPath=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
export PYTHONPATH=$scriptPath

sleep 20
$scriptPath/HelixBuild.py $BRANCH $NEWCOMMIT $MODULE $BSP

