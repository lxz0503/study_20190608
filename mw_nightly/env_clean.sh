#!/bin/bash
#kill vxsim
process=$(ps -ef |grep vxsim |grep -v grep|awk '{print $2}') 
echo $process
if [ -z "$process" ]
then
echo "no vxsim process need kill."
else
ps -ef |grep vxsim |grep -v grep|awk '{print $2}' |xargs sudo  kill -9
fi

#kill other wassp
process=$(ps -ef |grep wassp |grep -v grep|grep -v env_clean |awk '{print $2}')
echo $process
if [ -z "$process" ]
then
echo "no wassp process need kill."
else
echo "because the server is share with release,so skip the wassp killing"
#ps -ef |grep wassp |grep -v grep |grep -v env_clean |awk '{print $2}' |xargs sudo  kill -9
fi

#unreserve the instances used by nightly
simics="simics1 simics2"
bsp="qsp_arm qsp_ppc p2020rdb ia t2080qds"

qsp_arm_simics1_min=1601
qsp_arm_simics1_max=1650
qsp_arm_simics2_min=1621
qsp_arm_simics2_max=1650
qsp_ppc_simics1_min=1801
qsp_ppc_simics1_max=1850
qsp_ppc_simics2_min=1870
qsp_ppc_simics2_max=1890
p2020rdb_simics1_min=0501
p2020rdb_simics1_max=0540
p2020rdb_simics2_min=0501
p2020rdb_simics2_max=0550
ia_simics1_min=2401
ia_simics1_max=2450
ia_simics2_min=2421
ia_simics2_max=2440
t2080qds_simics1_min=1301
t2080qds_simics1_max=1350
t2080qds_simics2_min=1341
t2080qds_simics2_max=1370
for bspi in ${bsp}
do
    for simicsi in $simics
    do
        loopmin=`eval echo '$'"${bspi}_${simicsi}_min"`
        loopmax=`eval echo '$'"${bspi}_${simicsi}_max"`
        if [ "$bspi" == "ia" ]
        then
        bspj="x86-x58-ich10"
        elif [ "$bspi" == "qsp_arm" ]
        then
        bspj="qsp-arm"
        elif [ "$bspi" == "qsp_ppc" ]
        then
        bspj="qsp-ppc"
        else
        bspj=${bspi}
        fi

        if [ ${simicsi} == simics1 ]
        then
        portN=9090
	    else
		portN=9091
		fi

        for idx in `seq $loopmin $loopmax`
        do
        curl -s "http://pek-${simicsi}.wrs.com:${portN}/unreserve/pek-${simicsi}_simics_${bspj}_vx7_$idx" &
        done
        wait
    done
done
