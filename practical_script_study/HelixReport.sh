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
export PYTHONPATH=/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/try/workspace/PdvTool/vx7tool/new

# delay 60 seconds to parse test result
# and hope it can help to get the whole content
sleep 60
$scriptPath/HelixReport.py $BRANCH $NEWCOMMIT $MODULE $BSP

