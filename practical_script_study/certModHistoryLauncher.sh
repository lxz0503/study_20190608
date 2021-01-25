#!/bin/bash

CERTGIT=/buildarea1/svc-cmnet/vxworks-cert
cd $CERTGIT
git log -1 HEAD &> /dev/null
git branch &> /dev/null
git pull &> /dev/null
git log -1 HEAD &> /dev/null

source /buildarea1/lchen3/virtualenvironment/py3env/bin/activate
export PYTHONPATH=/buildarea1/lchen3/workspace/cert-checker
python /buildarea1/lchen3/workspace/cert-checker/launchCommit.py
