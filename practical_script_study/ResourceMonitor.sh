#!/bin/bash -x

# Must run at pek-vx-nwk1 with Python 3
date
id
hostname

hoststr=`hostname`
if [ "$hoststr" = "pek-vx-nwk1" ]
then
    source /buildarea1/lchen3/virtualenvironment/py3env/bin/activate
    python -V
    export PYTHONPATH=/folk/lchen3/try/workspace/PdvTool/vx7tool/new
    /folk/lchen3/try/workspace/PdvTool/vx7tool/new/KongResourceMonitor.py
else
    echo "please run this tool at pek-vx-nwk1"
fi
