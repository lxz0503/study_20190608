#!/bin/bash -x

MYSOURCE=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
#LOGDIR=/net/pek-sec-kong-02.wrs.com/workspace/svc-cmnet/log
LOGDIR=/net/pek-vx-nwk1.wrs.com/buildarea1/svc-cmnet/log

export PYTHONPATH=$MYSOURCE:/folk/lchen3/try/workspace/PMT/src
#export PATH=/folk/lchen3/package/opt/bin:$PATH
#export LD_LIBRARY_PATH=/folk/lchen3/package/opt/lib:$LD_LIBRARY_PATH

$MYSOURCE/KongCIMonitor.py $@ >> $LOGDIR/KongNightly.log
