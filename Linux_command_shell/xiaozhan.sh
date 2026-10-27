#!/bin/bash
find  ./ -name "*.cfg"  > cfg_name.txt
for i in `cat cfg_name.txt`
    do
       sed -i "s/DUT Hostname                             128.224.166.238/License Server Location localhost\nDUT Hostname        128.224.166.238/g" $i

    done

