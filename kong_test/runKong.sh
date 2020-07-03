#!/bin/bash 

# the wrapper script to simplify network Kong test usage
# the following boards are supported now:
#    vxsim_linux    (vxworks simulator, support both IPNet and RTNET)
#    fsl_imx6       (ARM target, support both IPNet and RTNET)
#    itl_generic    (IA target, support only Helix or native RTNET)
#    nxp_layerscape_a72 (ARM target, support only Helix)
#    xlnx_zynqmp    (ARM target, support Helix and Native)
#    xlnx_zynqmp_hvsafe (ARM target, support only Helix)
#    xlnx_zynqmp_dynamic (ARM target for dymanic, support only Helix)
#    qsp_arm        (Simics ARM target, support only IPNet)
#    fsl_t2t4       (t2080qds)    (Simics PPC target, support only IPNet)

print_usage () {
echo "usage: $0 -g gitPath_or_spinPath
                    -m|--module moduleName
                    [-c|--testcase testName]
                    [-b|--bsp bsp]
                    [-t|--tool llvm|gnu]
                    [-d|--direct]
                    [--helix]
                    buildOnly|testOnly|manualTest|buildTest

tips:
    1. git or spin path should be absolute path instead of relative path
    2. the default value: bsp=vxsim_linux; tool=llvm
    3. the supported bsps are vxsim_linux, fsl_imx6, qsp_arm and fsl_t2t4
    4. when using fsl_imx6, IMAGEPATH/TFTPSERVER/TFTPPATH required
    5. when using bsp qsm_arm or fsl_t2t4, SIMICSPATH and IMAGEPATH required
    6. direct connected target only supports xlnx_zynqmp
    7. -d/--direct and --helix options cannot be used together
"
}


# decide which is pkg path
get_vxworks_pkgspath () {
if [ -f $1/vxworks-7/pkgs_v2/net/ipnet*/coreip*/src/ipcom/util/scripts/runtestsuite.py ]; then
    pkgspath=$1/vxworks-7/pkgs_v2
elif [ -f $1/helix/guests/vxworks-7/pkgs_v2/net/ipnet*/coreip*/src/ipcom/util/scripts/runtestsuite.py ]; then
    pkgspath=$1/helix/guests/vxworks-7/pkgs_v2
elif [ -f $1/vxworks-653/pkgs/net/ipnet*/coreip*/src/ipcom/util/scripts/runtestsuite.py ]; then
    pkgspath=$1/vxworks-653/pkgs
elif [ -f $1/vxworks-7/pkgs/net/ipnet*/coreip*/src/ipcom/util/scripts/runtestsuite.py ]; then
    pkgspath=$1/vxworks-7/pkgs    
else
    echo "pkgs_v2 or pkgs path not found for GITPATH=$1"
    exit 1
fi
echo -e $pkgspath
}

if [ $# -eq 0 ]
then
    print_usage
    exit 1
fi

POSITIONAL=()
HELIX=false
DIRECT=false
GITPATH=""
MODULE=""
TESTCASE=""
BOARD=""

IPV4=false
IPV6=false

TFTPSERVER=128.224.153.34       #pek-vx-nwk1
TFTPPATH=/folk/lchen3/tftpboot

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --helix)
    HELIX=true
    shift # past argument
    ;;
    -d|--direct)
    DIRECT=true
    shift # past argument
    ;;
    -g)
    GITPATH="$2"
    shift # past argument
    shift # past value
    ;;
    -m|--module)
    MODULE="$2"
    shift # past argument
    shift # past value
    ;;
    -c|--testcase)
    TESTCASE="$2"
    shift # past argument
    shift # past value
    ;;
    -b|--bsp)
    BOARD="$2"
    shift # past argument
    shift # past value
    ;; 
    -t|--tool)
    TOOL="$2"
    shift # past argument
    shift # past value
    ;;  
    --ipv4)
    IPV4=true
    shift # past argument
    ;;  
    --ipv6)
    IPV6=true
    shift # past argument
    ;;  
    --default)
    DEFAULT=YES
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
#echo $POSITIONAL
set -- "${POSITIONAL[@]}" # restore positional parameters

if [ "$GITPATH" = "" ]; then
    print_usage
    echo "ERROR: miss required argument -g gitPath_or_spinPath"
    exit 1
fi
if [ "$MODULE" = "" ]; then
    print_usage
    echo "ERROR: miss required argument -m moduleName"
    exit 1
fi
if [ "$POSITIONAL" = "buildTest" ] || [ "$POSITIONAL" = "testOnly" ]; then
    if [ "$TESTCASE" = "" ]; then
        print_usage
        echo "ERROR: miss required argument -c testCase"
        exit 1
    fi    
fi
if [ "$BOARD" = "" ]; then
    BOARD=vxsim_linux
fi
if [ "$TOOL" = "" ]; then
    TOOL=llvm
fi    
if $HELIX && $DIRECT; then
    echo "ERROR: -d/--direct and --helix options cannot be used together"
    exit 1
fi

# NOTE: MUST set up
SMP=--smp
#SMP=--up

#MODULE=FIREWALL
#TESTCASE=ipfirewall.ipfilter.http_proxy     # 1 vxsim + 3 linux targets
#TESTCASE=ipfirewall.ipfilter.soho           # 3 vxsim targets
#TESTCASE=ipfirewall.ipfilter.http_proxy     # fast ipv4
#TESTCASE=ipfirewall.ipfilter.icmp_type      # fast ipv4 ipv6

PKGSPATH=$(get_vxworks_pkgspath $GITPATH)
if [[ $PKGSPATH =~ (pkgs_v2 or pkgs path not found) ]]; then
    exit 1
fi

IMAGEPATH=$PKGSPATH/net/ipnet/coreip/src/ipcom/util/scripts/$MODULE/${BOARD}_vip/default
SCRIPTPATH=$PKGSPATH/net/ipnet*/coreip*/src/ipcom/util/scripts # use * for both git and spin
wrenv=7

if $HELIX; then
    echo "=== building and testing helix $MODULE ==="
    TARGET=simlinux
    HELIXBSP=$BOARD
    if [ "$BOARD" = "itl_generic" ]; then 
        HELIXHOST=pek-canoepass
        HELIXCPU=SKYLAKE
    elif [ "$BOARD" = "nxp_layerscape_a72" ]; then 
        HELIXHOST=pek-kong-02
        HELIXCPU=ARMARCH8A
    elif [ "$BOARD" = "xlnx_zynqmp" ]; then 
        HELIXHOST=pek-kong-03
        HELIXCPU=ARMARCH8A
    elif [ "$BOARD" = "xlnx_zynqmp_hvsafe" ]; then
        HELIXHOST=pek-kong-04
        HELIXCPU=ARMARCH8A
    elif [ "$BOARD" = "xlnx_zynqmp_dynamic" ]; then
        HELIXHOST=pek-kong-04
        HELIXCPU=ARMARCH8A
    fi
    cmdPrefix="$SCRIPTPATH/runtestsuite.py --helix --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --toolchain=$TOOL --vxworks="board=vxsim_linux,target=$TARGET,version=7,wrenv=$wrenv,path=$GITPATH,helixbsp=$HELIXBSP,helixcpu=$HELIXCPU,helixhost=$HELIXHOST" --speed $SMP "
elif $DIRECT; then
    echo "=== building and testing direct connected $MODULE ==="
    TARGET=simlinux
    DIRECTBSP=$BOARD
    if [ "$BOARD" = "xlnx_zynqmp" ]; then
        DIRECTHOST="pek-kong-04"
        DIRECTCPU=ARMARCH8A
    fi
    cmdPrefix="$SCRIPTPATH/runtestsuite.py --direct --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --toolchain=$TOOL --vxworks="board=vxsim_linux,target=$TARGET,version=7,wrenv=$wrenv,path=$GITPATH,directbsp=$DIRECTBSP,directcpu=$DIRECTCPU,directhost=$DIRECTHOST" --speed $SMP --64bit"
else
    if [ "$BOARD" = "vxsim_linux" ]; then
        TARGET=simlinux
        if [ "$MODULE" = "RTNET" ]; then
            cmdPrefix="$SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --toolchain=$TOOL --targets=2 --vxworks="board=$BOARD,target=$TARGET,version=7,wrenv=$wrenv,path=$GITPATH" --speed $SMP "
        elif [ "$MODULE" = "RTNET_RTP" ]; then
            echo "ERROR: RTNET_RTP not supported for the BSP vxsim_linux"
            exit 1
        else
            cmdPrefix="$SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --toolchain=$TOOL --vxworks="board=$BOARD,target=$TARGET,version=7,wrenv=$wrenv,path=$GITPATH" --speed $SMP " 
        fi    
    elif [ "$BOARD" = "qsp_arm" ]; then
        TARGET=ARMARCH7
        SIMICSPATH=/buildarea3/lchen3/simics5-workspace,target=$TARGET,version=7,wrenv=$wrenv,path=$GITPATH
            
        cmdPrefix="$SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --supports=mipl --target-speed=50 --speed $SMP --toolchain=$TOOL --vxworks="board=$BOARD,simicspath=$SIMICSPATH,imagepath=$IMAGEPATH" "
    elif [ "$BOARD" = "fsl_t2t4" ]; then
        TARGET=PPCE6500
        SIMICSPATH=/buildarea3/lchen3/simics5-workspace,target=$TARGET,version=7,wrenv=$wrenv,path=$GITPATH
        
        #code coverage with debug info
        #cmdPrefix="$SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=4 --codecoverage --supports=mipl --target-speed=50 --toolchain=$TOOL --vxworks="board=$BOARD,simicspath=$SIMICSPATH,imagepath=$IMAGEPATH" "
        
        #simics without debug info
        cmdPrefix="$SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=4 --speed $SMP --supports=mipl --target-speed=50 --toolchain=$TOOL --vxworks="board=$BOARD,simicspath=$SIMICSPATH,imagepath=$IMAGEPATH" "
    elif [ "$BOARD" = "fsl_imx6" ]; then
        if [ "$MODULE" = "RTNET" ] || [ "$MODULE" = "RTNET_RTP" ]; then
            TARGET=ARMARCH7
            IMAGEPATH=$PKGSPATH/net/ipnet/coreip/src/ipcom/util/scripts/$MODULE/${BOARD}_image
            VLMTARGETS="25002,25003"
            VLMTARGETNUM=2

            cmdPrefix="$SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=$VLMTARGETNUM --vlmtargets="$VLMTARGETS" --speed $SMP --supports=mipl --target-speed=50 --toolchain=$TOOL --vxworks="board=$BOARD,imagepath=$IMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$GITPATH,tty=/dev/ttyS0" "
        else
            print_usage
            echo "ERROR: only RTNET/RTNET_RTP modules supported for the BSP fsl_imx6"
            exit 1
        fi
    elif [ "$BOARD" = "itl_generic" ]; then
        if [ "$MODULE" = "RTNET" ] || [ "$MODULE" = "RTNET_RTP" ]; then
            TARGET=NEHALEM
            IMAGEPATH=$PKGSPATH/net/ipnet/coreip/src/ipcom/util/scripts/$MODULE/${BOARD}_image
            VLMTARGETS="28525,28526"
            VLMTARGETNUM=2
                        
            cmdPrefix="$SCRIPTPATH/runtestsuite.py --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test" --targets=$VLMTARGETNUM --vlmtargets="$VLMTARGETS" --speed $SMP --64bit --supports=mipl --target-speed=50 --toolchain=$TOOL --vxworks="board=$BOARD,imagepath=$IMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$GITPATH,tty=/dev/ttyS0" "
        else
            print_usage
            echo "ERROR: only RTNET/RTNET_RTP modules supported for the BSP itl_generic"
            exit 1
        fi
    else
        print_usage
        echo "ERROR: bsp should be either vxsim_linux,fsl_imx6 or qsp_arm / fsl_t2t4 for the script"
        exit 1
    fi
fi

if $IPV4; then
    cmdPrefix=$cmdPrefix" --ipv4-only"
elif $IPV6; then
    cmdPrefix=$cmdPrefix" --test-ipv6"
fi

if [ "$1" = "buildOnly" ]; then
    # build image
    echo "=== building $MODULE image ==="
    echo "    using GITPATH=$GITPATH"
    echo "    using bsp=$BOARD"
    echo "    using tool=$TOOL"
    echo "    using $SMP"
    sudo rm -fr $MODULE
    echo "$cmdPrefix --buildonly -c $MODULE"
    $cmdPrefix --buildonly -c $MODULE
elif [ "$1" = "testOnly" ]; then
    # test only after building image
    if [ "$TESTCASE" = "ALL" ]; then
        echo "$cmdPrefix --no-rebuild $MODULE"
        $cmdPrefix --no-rebuild $MODULE
    else
        echo "$cmdPrefix --no-rebuild $MODULE -n $TESTCASE"
        $cmdPrefix --no-rebuild $MODULE -n $TESTCASE
    fi    
elif [ "$1" = "manualTest" ]; then
    # start up targets and wait for iptestengine.py to run test case
    echo "$cmdPrefix --no-rebuild -d $MODULE"
    $cmdPrefix --no-rebuild -d $MODULE

elif [ "$1" = "buildTest" ]; then
    # build and then test
    echo "=== building and testing $MODULE image ==="
    echo "    using GITPATH=$GITPATH"
    echo "    using bsp=$BOARD"
    echo "    using tool=$TOOL"
    echo "    using $SMP"    
    sudo rm -fr $MODULE
    if [ "$TESTCASE" = "ALL" ]; then
        echo "$cmdPrefix -c $MODULE"
        $cmdPrefix -c $MODULE
    else
        echo "$cmdPrefix -c $MODULE -n $TESTCASE"
        $cmdPrefix -c $MODULE -n $TESTCASE
    fi
else
    print_usage
    echo "ERROR: unsupported command; should be buildOnly|testOnly|manualTest|buildTest"
    exit 1
fi

