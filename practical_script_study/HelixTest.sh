#!/bin/bash -x

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

date
id
hostname
pwd

echo $BRANCH
echo $NEWCOMMIT
echo $MODULE
echo $BSP

export PATH=/bin:/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin:/usr/atria/bin:/folk/cm/bin:/folk/qms/tools:/folk/vlm/commandline:/usr/X11R6/bin:/folk/vlm/bin:/folk/bcao/ccollab-client
export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib

scriptPath=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
export PYTHONPATH=/net/pek-rhfs1.wrs.com/pek-rhfs04/home04/lchen3/try/workspace/PdvTool/vx7tool/new

rm -fr *
cleanUpKongEnv
#sleep 40
$scriptPath/HelixTest.py $BRANCH $NEWCOMMIT $MODULE $BSP

