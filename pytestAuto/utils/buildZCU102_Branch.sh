#!/bin/bash -x

BUILDVSB=true
BUILDVIP=true

git=/home/xli3/vxworks
# add below line for 2107

wrenv=$git"/wrenv.linux -p vxworks/relx"
#wrenv='/home/xli3/vxworks/wrenv.linux -p vxworks/relx'

bsp=xlnx_zynqmp
tool=llvm

vsbDir=$git/vsb_${bsp}
vipDir=$git/vip_${bsp}
# vsb   
if $BUILDVSB; then
    sudo rm -fr $vsbDir
    cd $git
    #sudo cp /home/windriver/ANVL/ANVL_Result/openssl-3.0.5.tar.gz   /home/windriver/$spin/download
    $wrenv vxprj vsb create -force -S -smp -bsp $bsp $vsbDir

    
    cd $vsbDir    
    $wrenv vxprj vsb config -o -add _WRS_CONFIG_COMPONENT_IPMCP=y
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_SYSTEMVIEWER
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_COMPONENT_NAT
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_COMPONENT_TUNNEL_SUPPORT
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_DETERMINISTIC_SMP
    $wrenv vxprj vsb config -s -remove _WRS_CONFIG_IPNET_BRIDGE
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_CORE_RTP=y
    $wrenv vxprj vsb config -s -add _WRS_CONFIG_IPERF3=y
    $wrenv make -j 8
fi

# vip
if [ $? -eq 0 ]; then
    if $BUILDVIP; then
        sudo rm -fr $vipDir
        $wrenv vxprj create -force -smp $bsp $tool $vipDir -vsb $vsbDir
        cd $vipDir
        $wrenv vxprj component add INCLUDE_RAM_DISK INCLUDE_IPCOM_USE_RAM_DISK INCLUDE_DISK_UTIL_SHELL_CMD INCLUDE_IPNET_PCAP_CMD INCLUDE_IPFTP_CMD  INCLUDE_ROUTECMD  INCLUDE_IPROUTE_CMD INCLUDE_PING INCLUDE_IPPING_CMD INCLUDE_IPPING6_CMD INCLUDE_PING6 INCLUDE_IPCOM_SYSVAR_CMD INCLUDE_IPCOM_SYSLOGD_CMD INCLUDE_IPARP_CMD INCLUDE_IPD_CMD INCLUDE_IPTELNETS INCLUDE_SHELL INCLUDE_SHELL_INTERP_CMD INCLUDE_IPIFCONFIG_CMD INCLUDE_IPATTACH INCLUDE_IFCONFIG  INCLUDE_IPMCP  INCLUDE_KEYADM_CMD  INCLUDE_IPMCP_USE_MLD INCLUDE_TELNET_CLIENT INCLUDE_STANDALONE_SYM_TBL  INCLUDE_DEBUG INCLUDE_DEBUG_KPRINTF  INCLUDE_ROMFS  INCLUDE_IPRADVD INCLUDE_IPRADVD_CMD  INCLUDE_DISK_UTIL
        $wrenv vxprj component add INCLUDE_XLNX_ZCU102 INCLUDE_IPERF3 INCLUDE_IPERF3_CMD INCLUDE_PCI_SHOW INCLUDE_GEI825XX_VXB_END
        $wrenv vxprj parameter set NUM_NET_DAEMONS 4
        $wrenv vxprj parameter set VX_SMP_NUM_CPUS 4
        $wrenv vxprj parameter set IPNET_MEMORY_LIMIT 33554432
        $wrenv vxprj parameter set NUM_FILES 300
        $wrenv vxprj parameter set NET_TASK_STACKSIZE 80000
        $wrenv vxprj component remove INCLUDE_PC_CONSOLE
        $wrenv vxprj component remove INCLUDE_WDB_COMM_END
        $wrenv vxprj build
        #sudo chown xli3:users $vipDir/default/vxWorks   
        cp $vipDir/default/uVxWorks  /folk/xli3/tsn_trial/ZCU102_Image/uVxWorks-IPERF
        cp $vipDir/default/xlnx-zcu102-rev-1.1.dtb  /folk/xli3/tsn_trial/ZCU102_Image/xlnx-zcu102-rev-1.1.dtb-IPERF
    fi
else
    echo "vsb build failed"
    exit 1
fi

