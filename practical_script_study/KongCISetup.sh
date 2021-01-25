#!/bin/bash -x

export PYTHONPATH=/folk/lchen3/try/workspace/PdvTool/vx7tool/new


MYSOURCE=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
#LOGDIR=/net/pek-cc-pb02l.wrs.com/testcloud/svc-cmnet/log
LOGDIR=/net/pek-sec-kong-02.wrs.com/workspace/svc-cmnet/log

export PYTHONPATH=$MYSOURCE
#export PATH=/folk/svc-cmnet/opt/bin:/folk/lchen3/package/opt/bin:$PATH
unset LD_LIBRARY_PATH

#/folk/svc-cmnet/opt/bin/
python $MYSOURCE/KongCISetup.py >> $LOGDIR/KongNightly.log


