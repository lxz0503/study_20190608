#!/bin/bash

source /buildarea1/lchen3/virtualenvironment/py3env/bin/activate
export PYTHONPATH=/buildarea1/lchen3/workspace/cert-checker
python /buildarea1/lchen3/workspace/cert-checker/docxChecker.py $@
