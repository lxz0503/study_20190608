#!/bin/bash -x

# Must run at pek-kong-06 with Python 3
echo "date=`date`"
echo "id=`id`"
echo "hostname=`hostname`"
echo "cwd=`pwd`"

echo "BRANCH=$BRANCH"
echo "NEWCOMMIT=$NEWCOMMIT"
echo "BSP=$BSP"

hoststr=`hostname`
if [ "$hoststr" = "pek-kong-06" ]
then
  cd $WORKSPACE
  rm -fr *
  git clone --depth 1 https://gitlab.devstar.cloud/lchen3/kong.git kong
  git clone --depth 1 https://gitlab.devstar.cloud/lchen3/kong_cases.git kong_cases
  $WORKSPACE/kong_cases/V7NET-2794/udb-storage-interference.sh $BRANCH $NEWCOMMIT $BSP
else
  echo "please run this tool at pek-kong-06"
fi
