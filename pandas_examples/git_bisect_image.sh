#!/bin/bash -x

BUILDVSB=true
BUILDVIP=true
# must be assigned
git=/home/windriver/Integration/vxworks

wrenv=$git"/wrenv.linux -p helix LM_LICENSE_FILE=27000@ala-lic4.wrs.com"


bsp=itl_generic
tool=llvm

vsbDir=$git/vsb_${bsp}
vipDir=$git/vip_${bsp}
sudo kill -9 `ps -ef | grep 128.224.164.57 | grep --color=auto telnet |  awk '{print $2}'`
# vsb   
if $BUILDVSB; then
    rm -fr $vsbDir
    cd $git
    $wrenv vxprj vsb create -force -S -lp64  -smp -inet6 -bsp $bsp $vsbDir
    
    cd $vsbDir    
    $wrenv vxprj vsb config -o -add _WRS_CONFIG_COMPONENT_IPMCP=y
    $wrenv vxprj vsb add IPNET_DHCP_SERVER IPNET_DHCP_RELAY IPNET_FIREWALL  IPNET_IPSECIKE IPNET_ROUTEPROTO IPNET_IPSECIKE_GDOI IPNET_IPSECIKE_IKE SECURITY_MISC_SEC_CRYPTO 
    $wrenv make -j 8
fi

# vip
if [ $? -eq 0 ]; then
    if $BUILDVIP; then
        rm -fr $vipDir
        $wrenv vxprj create -inet6  $bsp $tool $vipDir -vsb $vsbDir
        cd $vipDir
        $wrenv vxprj component add INCLUDE_RAM_DISK INCLUDE_IPCOM_USE_RAM_DISK INCLUDE_DISK_UTIL_SHELL_CMD INCLUDE_IPNET_PCAP_CMD INCLUDE_IPFTP_CMD  INCLUDE_ROUTECMD  INCLUDE_IPROUTE_CMD INCLUDE_PING INCLUDE_IPPING_CMD INCLUDE_IPPING6_CMD INCLUDE_PING6 INCLUDE_IPCOM_SYSVAR_CMD INCLUDE_IPCOM_SYSLOGD_CMD INCLUDE_IPARP_CMD INCLUDE_IPD_CMD INCLUDE_IPTELNETS INCLUDE_SHELL INCLUDE_SHELL_INTERP_CMD INCLUDE_IPIFCONFIG_CMD INCLUDE_IPATTACH INCLUDE_IFCONFIG INCLUDE_IPDHCPS INCLUDE_IPDHCPC INCLUDE_IPDHCPR  INCLUDE_IPMCAST_PROXY_CMD INCLUDE_IPMCP  INCLUDE_IP_SECURITY INCLUDE_IPSECCTRL_CMD INCLUDE_KEYADM_CMD INCLUDE_INTERNET_KEY_EXCHANGE INCLUDE_IPMCP_USE_IGMP INCLUDE_IPMCP_USE_MLD INCLUDE_TELNET_CLIENT INCLUDE_STANDALONE_SYM_TBL  INCLUDE_DEBUG INCLUDE_DEBUG_KPRINTF  INCLUDE_ROMFS INCLUDE_IPFIREWALL INCLUDE_IPFIREWALL_CMD INCLUDE_IPRADVD INCLUDE_IPRADVD_CMD  INCLUDE_DISK_UTIL INCLUDE_IPRIP INCLUDE_IPRIP_CTRL_CMD
        $wrenv vxprj parameter setstring SEC_VAULT_KEY_ENCRYPTING_PW  "aaa" 
        mkdir romfs
        cp /home/windriver/ANVL/ANVL_vsbcfg/Vx7/romfs/* $vipDir/romfs
        $wrenv vxprj build
        
        #cp $vipDir/default/vxWorks /home/windriver/ANVL/ANVL_image
    fi
else
    echo "vsb build failed"
    exit 1
fi

