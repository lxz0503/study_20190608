#!/bin/bash -x
# nightly use as (basename $0) 

sourcePath=$(cd $(dirname $0); pwd)

usage() {
    echo "usage:"
    echo "$(basename $0) -m wassp_matrix -t wassp_cases -p wassp_platform -d wassp_data"
    echo "-m|-matrix"
    echo "The matrix path"
    echo "-t|-testcase "
    echo "The testcase path"
    echo "-p|-platform "
    echo "The platform path"
    echo "-d|-data"
    echo "The ini data path"
	echo "-c|-conf"
	echo "The conf file which given the default value"
}

while [ $# -gt 0 ]; do
    case $1 in
        -m|-matrix) shift; wassp_matrix=$1 ;;
        -t|-testcase) shift; wassp_cases=$1 ;;
        -p|-platform) shift; wassp_platform=$1 ;;
        -d|-data) shift; wassp_data=$1 ;;
		-c|-conf) shift; configf=$1 ;;
        -help|-h|--help) usage;exit 1 ;;
        *) echo "invalid parameter '$1',See usage help." >&2; usage;exit 1;;
    esac
    shift
done

## config file
default_conf=config_nightly.ini
if [ -z ${configf} ]
then
    configf=${default_conf}
fi

source $sourcePath/$configf

## default valule
wasspHome=${wasspHome}
default_pwd=${default_pwd}

if [ -z "${wassp_matrix}" ]
then
    wassp_matrix=${wasspHome}/testmatrices/vxworks7
fi

if [ -z "${wassp_cases}" ]
then
    wassp_cases=${wasspHome}/testcases/vxworks7
fi

if [ -z "${wassp_platform}" ]
then
    wassp_platform=${wasspHome}/systems/vxworks7
fi

if [ -z "${wassp_data}" ]
then
    wassp_data=${wasspHome}/wassp-data/
fi

wassprpos="${wassp_matrix} ${wassp_cases} ${wassp_platform} ${wassp_data}"

for rpos in ${wassprpos}
do 
    cd ${rpos}
	echo ${rpos}
    find . -name "ORIG_HEAD.lock" -delete
    expect -c "
    set timeout -1
    spawn git pull
    expect  {
        -gl password*:  {
              send ${default_pwd}\r
                puts ******
                exp_continue
              }
        -gl (yes/no)? {
                send yes\r
                puts yes
                exp_continue
              }
        timeout {}
        eof {}
        }
    "   
done

