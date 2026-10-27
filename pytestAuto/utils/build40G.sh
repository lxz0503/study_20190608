#!/bin/bash -x

BUILDVSB=true
BUILDVIP=true
#
source /home/wrsadmin/AutoTSN/config/vx7_nightly_spin.config
Spin_name=$NIGHTLYSPIN
spin=SPIN
vxver=$VXVER
Branch_name=$LTAFRELEASE
time=$timestamp
patch_branch=$PatchBranch
# xiaozhan
if [ -z $Spin_name ];then
    echo "SPIN is Not ready,change to CISPIN"
    source /home/wrsadmin/AutoTSN/config/vx7_ci_nightly_spin.config
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
# xiaozhan
# must be assigned
git=/home/wrsadmin/SPIN/$Spin_name
pkgname=$vxver
echo $pkgname

# add below line for 2107
wrenv=$git"/wrenv.linux -p vxworks/$pkgname LM_LICENSE_FILE=27000@ala-lic4.wrs.com"

bsp=itl_generic
tool=llvm

vsbDir=$git/vsb_${bsp}_40G
vipDir=$git/vip_${bsp}_40G

# vsb   
if $BUILDVSB; then
    sudo rm -fr $vsbDir
    cd $git
    #sudo cp /home/windriver/ANVL/ANVL_Result/openssl-3.0.5.tar.gz   /home/windriver/$spin/download
#    $wrenv vxprj vsb create -force -S -lp64  -smp -cpu CORE -inet6 -bsp $bsp $vsbDir
    $wrenv vxprj vsb create -force -S -lp64 -smp -inet6 -bsp $bsp $vsbDir

    cd $vsbDir    
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_SUPPORTS_SMP=y
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_COMPONENT_IPSCTP=y
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_SYSTEMVIEWER
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_COMPONENT_NAT
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_COMPONENT_TUNNEL_SUPPORT
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_DETERMINISTIC_SMP
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_IPNET_BRIDGE
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_CORE_RTP=y
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_IPERF3=y
    $wrenv make -j 64
fi

# vip
if [ $? -eq 0 ]; then
    if $BUILDVIP; then
        sudo rm -fr $vipDir
        $wrenv vxprj create -inet6  $bsp $tool $vipDir -vsb $vsbDir
        cd $vipDir
        $wrenv vxprj component add INCLUDE_IPPTP INCLUDE_GPTP INCLUDE_VXBUS_SHOW INCLUDE_GEI825XX_VXB_END
        $wrenv vxprj component add INCLUDE_PING  INCLUDE_IPIFCONFIG_CMD INCLUDE_IFCONFIG INCLUDE_SHELL INCLUDE_PCI_SHOW INCLUDE_IPATTACH INCLUDE_STANDALONE_DTB INCLUDE_STANDALONE_SYM_TBL INCLUDE_IPERF3  INCLUDE_IPERF3_CMD INCLUDE_ROMFS INCLUDE_IPTELNETS INCLUDE_DEBUG_KPRINTF
        $wrenv vxprj component add DRV_VXBEND_QEIXL710 INCLUDE_IPCOM_SYSVAR_CMD 
    
	$wrenv vxprj parameter set IPNET_MEMORY_LIMIT 33554432
	$wrenv vxprj parameter set NUM_FILES 300
        $wrenv vxprj parameter set NET_TASK_STACKSIZE 80000
	$wrenv vxprj parameter set CONSOLE_BAUD_RATE 115200
	$wrenv vxprj parameter setstring IPNET_SOCK_DEFAULT_SEND_BUFSIZE "1000000"
	$wrenv vxprj parameter setstring IPNET_SOCK_DEFAULT_RECV_BUFSIZE "1000000"
       	$wrenv vxprj build
        if [ $? -eq 0 ]; then
            #sudo chown xli3:users $vipDir/default/vxWorks
            cp $vipDir/default/vxWorks /folk/xli3/40G_image/
        else
            echo "vip build failed"
            exit 1
        fi
    fi
else
    echo "vsb build failed"
    exit 1
fi

