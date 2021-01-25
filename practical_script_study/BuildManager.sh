#!/bin/bash -x
# run at pek-cc-pb02l
date
id
hostname

echo $BRANCH
echo $NEWCOMMIT

#export PYTHONPATH=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
#export PATH=/folk/lchen3/package/opt/bin:$PATH
#export LD_LIBRARY_PATH=/folk/lchen3/package/opt/lib:$LD_LIBRARY_PATH

export PYTHONPATH=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
#export PATH=/folk/svc-cmnet/opt/bin:/folk/lchen3/package/opt/bin:$PATH

export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin:/sbin/:/usr/local/bin:/usr/bin:/usr/atria/bin:/folk/cm/bin:/folk/qms/tools:/folk/vlm/commandline:/usr/X11R6/bin:/folk/vlm/bin

# kill all the hanging workbench processes
ps -eaf | grep /workbench-4/eclipse/x86_64-linux2/jre/bin/java | awk '{print $2}' | xargs sudo kill -9

ps -eaf | grep /workbench-4/eclipse/x86_64-linux2/jre/bin/java

# remove the lock for rtp build
sudo rm -f /tmp/wrtool_lock
/folk/lchen3/try/workspace/PdvTool/vx7tool/new/KongBuildManager.py $BRANCH $NEWCOMMIT

