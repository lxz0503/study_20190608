#!/bin/bash

testSpin=$1
mefaHost=$(hostname);
echo $mefaHost;

timeStamp=$(date +%y_%m_%d_%H_%M);
echo $timeStamp;

#35
#testSuite=APPL,ARP,DHCP,DNS,FIPS,FIREWALL,IGMP,IP,IPCOM,IPCRYPTO,IPIKE,IPV6,L2TP,MIB,MLD,MUX,NAT,NTP,PPP,RSH,RADIUS,RIP,ROHC,ROHC_TCP,ROHCOIPSec,ROUTE,SCTP,SNTP,SSH,SSL,TCP,TRACEROUTE,VLANSTACK,VRRP,EPOLL;

mefaPlat=/Jenkins/workspace/19-Vx7_Nig/vxworks_7/mefa_platform;
suiteDir=/Jenkins/workspace/19-Vx7_Nig/vxworks_7/mefa_cases/features;
#mefaPlat=/home/yliu2/vxworks_7/mefa_platform;
#suiteDir=/home/yliu2/vxworks_7/mefa_cases/features;
dockerDNS="-dontdestorybridge"
#buildOps="-dontcopyhosttool -nobuild -tests 4.0"
buildOps="-tests 2.0 -up"
#buildOps="-tests 1.0 -buildOnly"
#buildOps="-dontcopyhosttool -nobuild"
#buildOps=""
#buildOps="-dontcopyhosttool -nobuild -tests 1.0"

#dvdPath="/view_test/yliu2/v7release/vx20160722125550_vx7-CR0472-features_vx7-release -buildserver target:vxTarget@128.224.160.44";
#dvdPath="/view_test/yliu2/v7release/vxworks7  -buildserver target:vxTarget@128.224.160.44"
#dvdPath="/home/windriver/DVD_Installation/Nightly/latest"
#dvdPath="/view_test/yliu2/v7release/vx20160728131508_cr0472-update_vx7-release -buildserver target:vxTarget@128.224.160.44";
#dvdPath="/view_test/yliu2/v7release/vx20160730145159_diab-5961-GA_vx7-release -buildserver target:vxTarget@128.224.160.44";
#dvdPath="/buildarea1/yliu2/vx20161028085403_vx7-integration -buildserver target:vxTarget@128.224.179.60";
#dvdPath="/buildarea1/yliu2/vx20161101150805_vx7-integration -buildserver target:vxTarget@128.224.179.60";
#dvdPath="/net/pek-vx-system1/buildarea1/yliu2/nightly/$testSpin"
dvdPath="/buildarea1/yliu2/nightly/$testSpin -buildserver target:vxTarget@128.224.179.60"

testSuite="CAN";

cd $mefaPlat;

# p4080(18996) IA(22037) am335x(22599) imx6(25005)
#for testSuite in $sanity; do
#./runTest.tcl -suite $testSuite -suitedir $suiteDir -path $dvdPath -vxworks 7 -syslog 3 -caselog 2 -productinclude 6.9.2.f0 $dockerDNS $buildOps \
#-target cpu=PPCE500MC,bsp=fsl_p3p4p5,tool=gnu,portSrv=128.224.164.56:2008,pduSrv=128.224.164.112:3,bootdev=dtsec0,eif=eth4,ftp=windriver,passwd=windriver,uboot="uPrompt='=>';dtbFile=p4080ds.dtb;uUAddr=tftp 0x1000000;uDAddr=tftp 0xf000000;uBAddr=bootm 0x1000000 - 0xf000000" \
#-target cpu=NEHALEM,bsp=itl_generic,tool=llvm,portSrv=128.224.164.57:2002,pduSrv=128.224.164.113:3,bootdev=gei0,eif=eth4,ftp=windriver,passwd=windriver \
#-target cpu=ARMARCH7,bsp=ti_sitara_a8,tool=llvm,portSrv=128.224.164.53:2008,pduSrv=128.224.164.106:1,bootdev=cpsw0,eif=eth3,ftp=windriver,passwd=windriver,uboot="uPrompt='=>';dtbFile=am335x-evm.dtb;uUAddr=tftp 0x88000000;uDAddr=tftp 0x80005000;uBAddr=bootm 0x88000000 - 0x80005000" \
#-target cpu=ARMARCH7,bsp=fsl_imx6,tool=llvm,portSrv=128.224.164.53:2007,pduSrv=128.224.164.106:3,bootdev=enet0,eif=eth3,ftp=windriver,passwd=windriver,uboot="uPrompt='=>';dtbFile=imx6q-sabrelite.dtb;uUAddr=tftp 0x15000000;uDAddr=tftp 0x14000000;uBAddr=bootm 0x15000000 - 0x14000000" \
#-fastvsb -mail "haixiao.yan@windriver.com";

# p4080(18995) imx6(25005)

echo -e "./runTest.tcl -suite $testSuite -suitedir $suiteDir -path $dvdPath -vxworks 7 -syslog 3 -caselog 2 -productinclude 6.9.2.f0 $dockerDNS $buildOps -target cpu=PPCE500MC,bsp=fsl_p3p4p5,tool=gnu,portSrv=128.224.164.50:2010,pduSrv=128.224.164.103:2,bootdev=dtsec0,eif=eth3,ftp=windriver,passwd=windriver,uboot=\"uPrompt='=>';dtbFile=p4080ds.dtb;uUAddr=tftp 0x1000000;uDAddr=tftp 0xf000000;uBAddr=bootm 0x1000000 - 0xf000000\" -target bsp=vxsim_linux,tool=llvm 
-target cpu=ARMARCH7,bsp=fsl_imx6,tool=llvm,portSrv=128.224.164.53:2007,pduSrv=128.224.164.106:3,bootdev=enet0,eif=eth3,ftp=windriver,passwd=windriver,uboot=\"uPrompt='=>';dtbFile=imx6q-sabrelite.dtb;uUAddr=tftp 0x15000000;uDAddr=tftp 0x14000000;uBAddr=bootm 0x15000000 - 0x14000000\" -fastvsb"


./runTest.tcl -suite $testSuite -suitedir $suiteDir -path $dvdPath -vxworks 7 -syslog 3 -caselog 2 -productinclude 6.9.2.f0 $dockerDNS $buildOps \
-target cpu=PPCE500MC,bsp=fsl_p3p4p5,tool=gnu,portSrv=128.224.164.50:2010,pduSrv=128.224.164.103:2,bootdev=dtsec0,eif=eth3,ftp=windriver,passwd=windriver,uboot="uPrompt='=>';dtbFile=p4080ds.dtb;uUAddr=tftp 0x1000000;uDAddr=tftp 0xf000000;uBAddr=bootm 0x1000000 - 0xf000000" \
-target bsp=vxsim_linux,tool=llvm \
-target cpu=ARMARCH7,bsp=fsl_imx6,tool=llvm,portSrv=128.224.164.53:2007,pduSrv=128.224.164.106:3,bootdev=enet0,eif=eth3,ftp=windriver,passwd=windriver,uboot="uPrompt='=>';dtbFile=imx6q-sabrelite.dtb;uUAddr=tftp 0x15000000;uDAddr=tftp 0x14000000;uBAddr=bootm 0x15000000 - 0x14000000" \
-fastvsb -mail "haixiao.yan@windriver.com";
