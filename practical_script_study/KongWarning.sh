#!/bin/bash -x

# Must run at pek-vx-nwk1 with Python 2
date
id
hostname

hoststr=`hostname`
if [ "$hoststr" = "pek-vx-nwk1" ]
then
    python -V
    export PYTHONPATH=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
    python /folk/lchen3/try/workspace/PdvTool/vx7tool/new/KongWarning.py
else
    echo "please run this tool at pek-vx-nwk1"
fi
