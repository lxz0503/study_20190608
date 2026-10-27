#!/bin/bash -x

BUILDVSB=true
BUILDVIP=true

git=/home/xli3/vxworks
# add below line for 2107

wrenv=$git"/wrenv.linux -p vxworks/relx"

bsp=itl_generic
tool=llvm

vsbDir=$git/vsb_${bsp}
vipDir=$git/vip_${bsp}

# vsb   
if $BUILDVSB; then
    sudo rm -fr $vsbDir
    #sudo cp /home/windriver/ANVL/ANVL_Result/openssl-3.0.5.tar.gz   /home/windriver/$spin/download
    $wrenv vxprj vsb create -force -S -lp64  -smp -cpu CORE -inet6 -bsp $bsp $vsbDir
    
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
        $wrenv vxprj component add INCLUDE_IPPTP INCLUDE_GPTP
        $wrenv vxprj component add INCLUDE_8021QBV INCLUDE_LEGACY_QBV_API INCLUDE_8021QBV_SHOW INCLUDE_1588_CLOCK INCLUDE_GEI_IEEE1588
        $wrenv vxprj component add INCLUDE_PING  INCLUDE_IPIFCONFIG_CMD INCLUDE_IFCONFIG INCLUDE_SHELL INCLUDE_PCI_SHOW INCLUDE_IPATTACH INCLUDE_STANDALONE_DTB INCLUDE_STANDALONE_SYM_TBL INCLUDE_IPERF3 INCLUDE_ROMFS INCLUDE_TSN_CONFIG INCLUDE_TSN_CONFIG_CMD INCLUDE_IPTELNETS INCLUDE_DEBUG_KPRINTF

        cp -rf $git/vxworks/relx/source/os/net/tsn/demo .
        rm -rf demo/tsnPerfLxRx.c
        $wrenv vxprj vip file add demo/*.c
        $wrenv vxprj parameter set TSN_CLK_INT_THROTTLE_INTERVAL 1
        $wrenv vxprj build
        #sudo chown xli3:users $vipDir/default/vxWorks   
        cp $vipDir/default/vxWorks /folk/xli3/tsn_trial/IA_Image/
    fi
else
    echo "vsb build failed"
    exit 1
fi

