#!/bin/bash -x

BUILDVSB=true
BUILDVIP=true
#
source /home/xli3/pytestAuto/config/vx7_nightly_spin.config
Spin_name=$NIGHTLYSPIN
spin=SPIN
vxver=$VXVER
Branch_name=$LTAFRELEASE
time=$timestamp
patch_branch=$PatchBranch
# xiaozhan
if [ -z $Spin_name ];then
    echo "SPIN is Not ready,change to CISPIN"
    source /home/xli3/pytestAuto/config/vx7_ci_nightly_spin.config
    spin=CISPIN
    Spin_name=$NIGHTLYSPIN
    vxver=$VXVER
    Branch_name=$LTAFRELEASE
    time=$timestamp
    patch_branch=$PatchBranch
    if [ -z $Spin_name ];then
        echo "CISPIN is Not ready,exit"
        exit 1  
    fi
fi
echo "spin type is ${spin}"
git=/home/xli3/SPIN/$Spin_name
pkgname=$vxver
echo $pkgname

# add below line for 2107
wrenv=$git"/wrenv.linux -p vxworks/$pkgname LM_LICENSE_FILE=27000@ala-lic4.wrs.com"

bsp=itl_generic
tool=llvm

vsbDir=$git/vsb_${bsp}_tsn
vipDir=$git/vip_${bsp}_tsn

# vsb   
if $BUILDVSB; then
    sudo rm -fr $vsbDir
    cd $git
    $wrenv vxprj vsb create -force -S -lp64 -smp -inet6 -bsp $bsp $vsbDir

    cd $vsbDir    
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_PTP=y
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_GPTP=y
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_TSN=y
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_IPERF3=y
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_FS=y
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_FS_ROMFS=y
    $wrenv make -j 8
fi

# vip
if [ $? -eq 0 ]; then
    if $BUILDVIP; then
        sudo rm -fr $vipDir
        $wrenv vxprj create -inet6  $bsp $tool $vipDir -vsb $vsbDir
        cd $vipDir
        $wrenv vxprj component add INCLUDE_IPPTP INCLUDE_GPTP INCLUDE_VXBUS_SHOW
        $wrenv vxprj component add INCLUDE_8021QBV INCLUDE_LEGACY_QBV_API INCLUDE_8021QBV_SHOW INCLUDE_1588_CLOCK INCLUDE_GEI_IEEE1588 INCLUDE_GEI825XX_VXB_END
        $wrenv vxprj component add INCLUDE_PING  INCLUDE_IPIFCONFIG_CMD INCLUDE_IFCONFIG INCLUDE_SHELL INCLUDE_PCI_SHOW INCLUDE_IPATTACH INCLUDE_STANDALONE_DTB INCLUDE_STANDALONE_SYM_TBL INCLUDE_IPERF3 INCLUDE_ROMFS INCLUDE_TSN_CONFIG INCLUDE_TSN_CONFIG_CMD INCLUDE_IPTELNETS INCLUDE_DEBUG_KPRINTF INCLUDE_INT_SHOW INCLUDE_ISR_HANDLER_SHOW INCLUDE_ISR_SHOW INCLUDE_ARP_API
        $wrenv vxprj component remove INCLUDE_SMT_ENABLE INCLUDE_CPU_LOW_PWR_IDLE
        $wrenv vxprj parameter set STREAM_EXTRA_OFFSET 1
	cp -rf /home/xli3/demo ./
        rm -rf demo/tsnPerfLxRx.c   # if it has this file
        $wrenv vxprj vip file add demo/*.c
        $wrenv vxprj parameter set TSN_CLK_INT_THROTTLE_INTERVAL 1
        $wrenv vxprj parameter set NUM_NET_DAEMONS 4
        $wrenv vxprj parameter set NET_DAEMONS_CPU_AFFINITY "TRUE"
        $wrenv vxprj parameter setstring NET_TASK_PRIORITIES "0,50;1,50;2,50;3,40"
        mkdir romfs
        cp  -rf /home/xli3/demo/config/case1_1000stream.json romfs/
        cp  -rf /home/xli3/demo/config/case2_300stream.json romfs/
        cp  -rf /home/xli3/demo/config/case3_20stream.json romfs/
        cp  -rf /home/xli3/demo/config/case4_60stream.json romfs/
        cp  -rf /home/xli3/demo/config/case5_100stream.json romfs/

        $wrenv vxprj build
        if [ $? -eq 0 ]; then
            #sudo chown xli3:users $vipDir/default/vxWorks
            cp $vipDir/default/vxWorks /folk/xli3/tsn_perf/
        else
            echo "vip build failed"
            exit 1
        fi
    fi
else
    echo "vsb build failed"
    exit 1
fi

