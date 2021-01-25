#!/bin/bash -x

# Must run at pek-vx-nwk1 with Python 3
echo "date=`date`"
echo "id=`id`"
echo "hostname=`hostname`"
echo "cwd=`pwd`"

echo "BRANCH=$BRANCH"
echo "NEWCOMMIT=$NEWCOMMIT"
echo "BSP=$BSP"

hoststr=`hostname`
if [ "$hoststr" = "pek-vx-nwk1" ]
then
  cd $WORKSPACE
  rm -fr *
  git clone --depth 1 https://gitlab.devstar.cloud/lchen3/kong.git kong
  git clone --depth 1 https://gitlab.devstar.cloud/lchen3/kong_cases.git kong_cases

  source /buildarea1/lchen3/virtualenvironment/py3env/bin/activate
  python -V
  export PYTHONPATH=$WORKSPACE/kong
  export scriptPath=$WORKSPACE/kong_cases/VIRTIO_NETWORK_DRIVER
  #rm -fr *
  python $scriptPath/virtioNetworkDriver.py --branch $BRANCH --commit $NEWCOMMIT --bsp $BSP
else
  echo "please run this tool at pek-vx-nwk1"
fi
