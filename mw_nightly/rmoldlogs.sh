## remove the overdate Logs and spin of nightly test.
## the spin path and Logs path should be given
#!/bin/bash
scriptpath=$(cd $(dirname $0); pwd)
usage() {
    echo "Usage:`basename $0` -rmpath rmpath -keepnum keepnum"
    echo "-p|-rmpath"
    echo "The spin path or log path which need remove"
    echo "-k|-keepnum "
    echo "The nummber of the latest items you should keep(not remove)"
}

while [ $# -gt 0 ]; do
    case $1 in
        -p|-rmpath) shift; rmpath=$1 ;;
        -k|-keepnum) shift; keepnum=$1 ;;
        *) echo "invalid parameter '$1',See usage help." >&2; usage;exit 1;;
    esac
    shift
done

if [ -z $rmpath ]
then
    echo "!!!!Error:The parent path you want to remove must be given"
    exit 1
fi

if [ -z $keepnum ]
then
    keepnum=10
fi

##start to remove the subdir
subdirlist=`ls -t $rmpath |grep vx20`
# echo $subdirlist
loopi=0
for subdir in $subdirlist
do
    loopi=$(expr $loopi + 1)
	if [ $loopi -gt $keepnum ]
	then
        echo "start removing the $subdir"
        rm -rf $rmpath/$subdir
        echo "finished remove $subdir"
    fi
done
