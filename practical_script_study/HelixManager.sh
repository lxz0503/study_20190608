#!/bin/bash -x
# run at pek-vx-nwk1
date
id
hostname

echo $BRANCH
echo $NEWCOMMIT
echo $MODULE
echo $BSP

scriptPath=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
export PYTHONPATH=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin:/sbin/:/usr/local/bin:/usr/bin:/usr/atria/bin:/folk/cm/bin:/folk/qms/tools:/folk/vlm/commandline:/usr/X11R6/bin:/folk/vlm/bin

targets="28567 28593 28610"
for target in ${targets}
do
	/folk/vlm/commandline/vlmTool forceUnreserve -s amazon.wrs.com -t $target -Z lchen3 -P wrslchen3
	/folk/vlm/commandline/vlmTool reserve -t $target
    #echo "try"
done

$scriptPath/HelixManager.py $BRANCH $NEWCOMMIT
