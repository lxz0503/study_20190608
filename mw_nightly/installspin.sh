#!/bin/bash
# nightly use as basename $0 -s spinname

sourcePath=$(cd $(dirname $0); pwd)

usage() {
    echo "Usage:`basename $0` -spinname spin_name -installpath install_path -profile profile"
	echo "-serv|-spinserver"
	echo "The spinserver path,default is ${default_server}"
    echo "-s|-spinname"
    echo "The spin name which should exist in ${default_server}"
    echo "-i|-installpath "
    echo "The path which the SPIN will install to,if skip this parameter,the default is ${default_install}"
	echo "-p|-profile"
	echo "The used profile when install SPIN,if skip this parameter,the default is ${default_profile}"
	echo "-c|-conf"
	echo "The conf file which should be given,if skip this parameter,the default is ${default_conf}"
}

while [ $# -gt 0 ]; do
    case $1 in
        -s|-spinname) shift; spin_name=$1 ;;
        -i|-installpath) shift; install_path=$1 ;;
        -f|-profile) shift;profile=$1 ;;
		-serv|-spinserver) shift;spinserver=$1 ;;
		-c|-conf) shift;configf=$1 ;;
        -help|-h|--help) usage;exit 1 ;;
        *) echo "invalid parameter '$1',See usage help." >&2; usage;exit 1;;
    esac
    shift
done

default_conf=config_nightly.ini
## config file
if [ -z $configf ]
then
    echo "Info:The config file is skip and use ${default_conf}"
    configf=${default_conf}
fi
source $sourcePath/$configf

## default value from config file
default_server=${default_server}
default_install=${default_install}
default_profile=${default_profile}

## spin server
if [ -z $spinserver ]
then
    echo "Info:The spinserver path parameter is skip and use ${default_server}"
    spinserver=${default_server}
fi

## spin name
if [ -z ${spin_name} ]
then
    echo "!!!!Error:Spin name can not skip"
    usage
    exit 1
fi
if [ -d $spinserver/vxworks-7-r2/${spin_name} ]
then
    echo "Your are ready to install $spin_name"
else
    echo "!!!!Error:The ${spin_name} can not found on $spinserver"
    exit 1
fi

## install path
if [ -z ${install_path} ]
then
    echo "Info:The install path parameter is skip and use the default path to install SPIN"
    install_path=${default_install}/${spin_name}
else
    install_path=${install_path}/${spin_name}
fi
if [ -d ${install_path} ]
then
  rm -rf ${install_path}
fi
mkdir -p ${install_path}

## profile
if [ -z $profile ]
then
    echo "Info:The profile parameter is skip and use ${default_profile}"
    profile=${default_profile}
fi

echo "****Info:Start to Install SPIN ****"
echo "****Info:Spin name is $spin_name.****"
echo "****Info: Profile is $profile.****"
echo "****Info:Install_path is ${install_path}.****"

## install spin
cd ${spinserver}/vxworks-7-r2/${spin_name}/bootstrap_installer/
./setup_linux -yum install  -y --installroot=${install_path}

## replace license
echo "****Info:Replace with the local license.****"
if [ -f "/net/pek-cdftp/pek-cdftp1/ftp/r1/license/WRSLicense.lic" ]
then
    rm -rf ${install_path}/license/*.lic
    cp -f /net/pek-cdftp/pek-cdftp1/ftp/r1/license/WRSLicense.lic ${install_path}/license/
    chmod -R 777 ${install_path}/license/*
    if [ -f "${install_path}/license/WRSLicense.lic" ]
    then
        echo "spin install suceeded"
    else
        cd ${spinserver}/vxworks-7-r2/${spin_name}/bootstrap_installer/
        ./setup_linux -yum install  -y --installroot=${install_path}
        cp -f /net/pek-cdftp/pek-cdftp1/ftp/r1/license/WRSLicense.lic ${install_path}/license/
        chmod -R 777 ${install_path}/license/*
    fi
else
    echo "****Warning:Keep using the remote license"
fi

echo "****Info:end to Install SPIN ****"
exit 0
