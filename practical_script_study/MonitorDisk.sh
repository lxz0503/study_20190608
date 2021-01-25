#!/bin/bash -x

partition=/testcloud

cd $partition
availSize=`df -m . | awk 'FNR==3{print $3}'`

# warning if less than 100M
if [ "$availSize" -lt 100000 ]; then
    echo "warning"
    exit 1
else
    echo "normal"
    exit 0
fi
