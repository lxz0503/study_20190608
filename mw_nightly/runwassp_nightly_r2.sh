#!/bin/bash -x
# SbinDir: $spinhomepath/${spinname}
# LogDir : $LogRoot/$branchname/${spinname}_${domain}
# nightly use as basename $0 -s spinname -t testplan -d domain -b branchname 

sourcePath=$(cd $(dirname $0); pwd)
mydate=`date +%Y%m%d_%H%M%S`

usage() {
    echo "Usage:`basename $0` -s spinname -t testplan -d domain -b branchname [-m mailadr -l logpath -mr matrixpath -tp testcasepath -pp platformpath]"
    echo "-s|-spinname"
    echo "The spin name which testing"
    echo "-t|-testplan"
    echo "The testplan name which testing"	
    echo "-d|-domain"
    echo "The domain name which testing"
    echo "-b|-branchname"
    echo "The branch name which testing"		
    echo "-m|-mailadr"
    echo "The send mail adr,none for not send."
    echo "-l|-logpath"
    echo "logpath for run wassp"
    echo "-mr|-matrixpath"
    echo "matrix path for run wassp"
    echo "-tp|-testcasepath"
    echo "testcase path for run wassp"
    echo "-pp|-platformpath"
    echo "platform path for run wassp"
	echo "-c|-conf"
	echo "The conf file"
}

while [ $# -gt 0 ]; do
    case $1 in
        -s|-spinname) shift; spinname=$1 ;;
        -t|-testplan) shift; testplan=$1 ;;
        -d|-domain) shift;domain=$1 ;;
        -b|-branchname) shift;branchname=$1 ;;
        -m|-mailadr) shift;mailadr=$1 ;;
        -l|-logpath) shift;logpath=$1 ;;
        -c|-conf) shift;configf=$1 ;;
        -mr|-matrixpath) shift;matrixpath=$1 ;;	
        -pp|-platformpath) shift;platformpath=$1 ;;	
        -tp|-testcasepath) shift;testcasepath=$1 ;;		
        -help|-h|--help) usage;exit 1 ;;
        *) echo "invalid parameter '$1',See usage help." >&2; usage;exit 1;;
    esac
    shift
done


## conf file
default_conf=config_nightly.ini
if [ -z $configf ]
then
    configf=${default_conf}
fi
source $sourcePath/$configf

## default valule
wasspHome=${wasspHome}
LogRoot=${LogRoot}
default_EMAIL_LIST=${default_EMAIL_LIST}
default_install=${default_install}
spinhomepath=${default_install}

## logpath
if [[ $logpath == "new" ]] 
then 
    logpath=${LogRoot}/${branchname}/${mydate}_${spinname}_${domain}
elif [ -z "$logpath" ]
then
    logpath=${LogRoot}/${branchname}/${spinname}_${domain}
else
    logpath=${logpath}
fi

## matrix path info
if [ -z ${matrixpath} ]
then
    matrixPath=${wasspHome}/testmatrices/vxworks7/Nightly
else
    matrixPath=${matrixPath}
fi

## testcase path info
if [ -z ${testcasepath} ]
then
    testcasepath=${wasspHome}/testcases/vxworks7
else
    testcasepath=${testcasepath}
fi

## platform path info
if [ -z ${platformpath} ]
then
    platformpath=${wasspHome}/systems/vxworks7
else
    platformpath=${platformpath}
fi

## If damp run 
if [ ! -z "$DAMPRUN" ]
then
    dampoption="--dampRun"
else
    dampoption=""
fi

## If spin is exist
if [ ! -d  "${spinhomepath}/${spinname}/vxworks-7" ]
then
   echo "ERROR: not a valid vxworks-7 Environment"
   exit 1
fi

## send mail adress
if [ -z ${mailadr} ] || [ ${mailadr} == "default" ]
then
EMAIL_LIST=${default_EMAIL_LIST}
elif [ ${mailadr} == "no" ]
then
EMAIL_LIST="none"
else
EMAIL_LIST="${EMAIL_LIST},${mailadr}"
fi

## result mail send function
function ResultMailSend {
  FROM=WASSP-Nightly
  echo "------result mail send file-------\n"
  JSON_FILE=${logpath}/coreos/Summary/summary.json
  TEMPMESSAGE="${logpath}/coreos/tmp/emailmessage.tmp"
  mkdir -p ${logpath}/coreos/tmp/
  # Remove ^M characters
  tr -d '\r' < $JSON_FILE > $TEMPMESSAGE && mv $TEMPMESSAGE $JSON_FILE
  # Catch total test runs from json file
  TOTAL=`cat $JSON_FILE | grep "testRunCount"`
  TOTAL_NUM="${#TOTAL}"
  TOTAL=${TOTAL:20:$TOTAL_NUM-20}
  echo Total: ${TOTAL//[,]/}
  # Catch PASSED test runs from json file
  PASS=`cat $JSON_FILE | grep "passes"`
  PASS_NUM="${#PASS}"
  PASS=${PASS:14:$PASS_NUM-14}
  echo PASS: ${PASS//[,]/}
  # Calculate passrate
  totalnum=`echo $TOTAL | sed 's/,//g' | sed 's/ //g'`
  passnum=`echo $PASS | sed 's/,//g' | sed 's/ //g'`
  PASSRATE=`echo "scale=1; $passnum*100/$totalnum" | bc`
  echo PASSRATE: $PASSRATE%
  # Catch Exec Fail test runs from json file
  EXECFAIL=`cat $JSON_FILE | grep "Exec FAIL"`
  EXECFAIL_NUM="${#EXECFAIL}"
  EXECFAIL=${EXECFAIL:20:$EXECFAIL_NUM-20}
  echo Exec Fail: ${EXECFAIL//[,]/}
  # Catch FAIL test runs from json file
  FAIL=`cat $JSON_FILE | grep -w "\"FAIL\""`
  FAIL_NUM="${#FAIL}"
  FAIL=${FAIL:15:$FAIL_NUM-15}
  echo Fail: ${FAIL//[,]/}
  # Catch BOOT_FAIL test runs from json file
  BOOTFAIL=`cat $JSON_FILE | grep "Boot Fail"`
  BOOTFAIL_NUM="${#BOOTFAIL}"
  BOOTFAIL=${BOOTFAIL:20:$BOOTFAIL_NUM-20}
  echo Boot Fail: ${BOOTFAIL//[,]/}
  # Catch TIMEOUT test runs from json file
  TIMEOUT=`cat $JSON_FILE | grep "TIMEOUT"`
  TIMEOUT_NUM="${#TIMEOUT}"
  TIMEOUT=${TIMEOUT:18:$TIMEOUT_NUM-18}
  echo TIMEOUT: ${TIMEOUT//[,]/}
  # Catch EXECBLK test runs from json file
  EXECBLK=`cat $JSON_FILE | grep "No Target"`
  EXECBLK_NUM="${#EXECBLK}"
  EXECBLK=${EXECBLK:22:$EXECBLK_NUM-22}
  echo Exec Block: ${EXECBLK//[,]/}
  # Catch BUILDFAIL test runs from json file
  BUILDFAIL=`cat $JSON_FILE | grep "Build Fail"`
  BUILDFAIL_NUM="${#BUILDFAIL}"
  BUILDFAIL=${BUILDFAIL:22:$BUILDFAIL_NUM-22}
  echo Build Fail: ${BUILDFAIL//[,]/}
  # Catch EXCEPTION test runs from json file
  EXCEPTION=`cat $JSON_FILE | grep "EXCEPTION"`
  EXCEPTION_NUM="${#EXCEPTION}"
  EXCEPTION=${EXCEPTION:20:$EXCEPTION_NUM-20}
  echo EXCEPTION: ${EXCEPTION//[,]/}
  # Catch the DVD info from jason file.
  DVDINFO=`cat $JSON_FILE | grep "dvdDir"`
  DVDINFO_LENGTH="${#DVDINFO}"
  DVD_DIR=`echo ${DVDINFO:15:$DVDINFO_LENGTH-16} |sed 's/\",//g'`
  Test_Start=`cat $JSON_FILE | grep "date"`
  Test_Start=${Test_Start:12}
  Test_Start=${Test_Start//[,]/}
  SCHEDULER_LOG=`/bin/ls -rt ${scheduler_log}/WASSP_schedLog*.txt | tail -1`
  TOTAL_TIME_SUMMARY=`cat -n $SCHEDULER_LOG | grep "Total time"`
  echo "00000 $SCHEDULER_LOG"
  TOTAL_HOURS=`echo $TOTAL_TIME_SUMMARY | grep -o -P '.{0,3}hours' | tr -d '[:alpha:]'`
  TOTAL_MINUTES=`echo $TOTAL_TIME_SUMMARY | grep -o -P '.{0,3}minutes' | tr -d '[:alpha:]'`
  TOTAL_SECONDS=`echo $TOTAL_TIME_SUMMARY | grep -o -P '.{0,3}seconds' | tr -d '[:alpha:]'`
  echo "88888 $TOTAL_HOURS $TOTAL_MINUTES $TOTAL_SECONDS"
  TOTAL_TIME=`echo ${TOTAL_HOURS}:$(printf "%02d" ${TOTAL_MINUTES}):$(printf "%02d" ${TOTAL_SECONDS}) |sed "s/ //g"`
  # wassp version
  wassp_version=`eval export PATH=$wasspHome/wassp-nest/tools/bin:$wasspHome/wassp/host/scheduler/bin:${PATH} && runwassp --version|tail -1`
  wassp_version=`echo $wassp_version|awk  -F ':'  '{print $2}' `
  # subject
  SUBJECT="DATE: $Test_Start WASSP Test on $spinname  finished - tag: $domain "
  if [[ ! -z "$MailTitle" ]]; then
   SUBJECT="${MailTitle}-${SUBJECT}"
  fi
  SUMMARY_FILE=${logpath}/coreos/Summary/summary.html
  EMAILMESSAGE="${logpath}/coreos/tmp/emailmessage.html"
  echo -e '<basefont face="arial" size="4">' > $EMAILMESSAGE
  echo -e '<head><style>body {background-image:url("http://$(hostname)/${wasspHome}/wassp/host/engines/report/template/wassp2.png");background-repeat:no-repeat;background-position:right top;}' >> $EMAILMESSAGE
  echo -e 'table, td, th{border:1px solid black;}th{background-color:powderblue;color:blue;}</style></head>' >> $EMAILMESSAGE
  echo -e "<font face="arial" size="6"> VxWorks Nightly Test On SPIN: $spinname </font><br><br>" >> $EMAILMESSAGE
  # Test Environment
  echo -e "<li><b>Testing Environment:</b>" >> $EMAILMESSAGE
  echo -e '<table style="font-family:Arial"><tbody>' >> $EMAILMESSAGE
  echo -e "<tr><th width="200">Test Server</th><td>$(hostname)</td></tr>" >> $EMAILMESSAGE
  echo -e "<tr><th width="200">WIND_HOME</th><td><a>$DVD_DIR</a></td></tr>" >> $EMAILMESSAGE
  echo -e "<tr><th width="200">Test Matrix</th><td><a href="http://$(hostname)/$matrixPath/$testplan">$testplan</a></td></tr>" >> $EMAILMESSAGE 
  echo -e "<tr><th width="200">WASSP HOME</th><td><a>$wasspHome</a></td></tr>" >> $EMAILMESSAGE
  echo -e "<tr><th width="200">WASSP VERION</th><td><a>$wassp_version</a></td></tr>" >> $EMAILMESSAGE
  echo -e "</tbody></table><br>"  >> $EMAILMESSAGE
  echo -e "<li><a href="http://$(hostname)/${logpath}/coreos/Summary/summary.html"><b>Testing Reports</b></a>" >> $EMAILMESSAGE
  echo -e '<table style="font-family:Arial"><tbody>' >> $EMAILMESSAGE
  echo -e "<tr><th width="200">HTML LOG:</th><td><a href="http://$(hostname)/${logpath}/coreos/Summary/summary.html">http://$(hostname)/${logpath}/coreos/Summary/summary.html</a></td></tr>" >> $EMAILMESSAGE
  echo -e "</tbody></table><br>"  >> $EMAILMESSAGE

  # total  pass passrate totalTime
  echo -e "<table style="font-family:Arial"><thead><tr><th width="100">Total</th><th width="100">Pass</th><th width="100">Passrate</th><th width="100">TotalTime</th></tr></thead>" >> $EMAILMESSAGE
  echo -e "<tbody><tr><td align="center">${TOTAL//[,]/}</td><td align="center">${PASS//[,]/}</td><td align="center">$PASSRATE%</td><td align="center">$TOTAL_TIME</td></tr></tbody></table>" >> $EMAILMESSAGE
  echo -e "<table style="font-family:Arial"><thead><tr><th width="100">BuildFail</th><th width="100">ExecFail</th><th width="100">Fail</th><th width="100">Timeout</th><th width="100">BootFail</th><th width="100">NoTarget</th><th width="100">WASSP Exception</th></tr></thead>" >> $EMAILMESSAGE
  echo -e "<tbody><tr><td align="center">${BUILDFAIL//[,]/}</td><td align="center">${EXECFAIL//[,]/}</td><td align="center">${FAIL//[,]/}</td><td align="center">${TIMEOUT//[,]/}</td><td align="center"> ${BOOTFAIL//[,]/}</td><td align="center">${EXECBLK//[,]/}</td><td align="center">${EXCEPTION//[,]/}</td></tr></tbody></table><br>" >> $EMAILMESSAGE

  # Remove ^M characters & send an email using /bin/mail
  tr -d '\r' < $EMAILMESSAGE > $TEMPMESSAGE && mv $TEMPMESSAGE $EMAILMESSAGE
{
cat << EOF - $EMAILMESSAGE
From: $FROM
To: $EMAIL_LIST
Subject: $SUBJECT
Content-Type: text/html
EOF
} | /usr/sbin/sendmail -t

}

##################################
wasspEnv="\
            -E WASSP_BASE=$wasspHome/wassp/host \
            -E WASSP_HOME=$wasspHome \
            -E WASSP_WIND_HOME=$spinhomepath/$spinname \
            -E WASSP_VSB_BASE=${logpath}/coreos/Workspace/vsb  \
            -E WASSP_LOGS_HOME=${logpath}/coreos \
            -E WASSP_WORKSPACE_HOME=${logpath}/coreos/Workspace/ \
            -E WASSP_TESTCASE_HOME=${testcasepath}/.. \
            -E WASSP_TESTCASE_BASE=${testcasepath} \
            -E WASSP_SYSTEMS_BASE=${platformpath} \
            -E WASSP_SYSTEMS_HOME=${platformpath}/.. \
            -E WASSP_VSB_THREADS=128 \
            -E threads_build_max=128 \
            -E threads_exec_max=128 \
            -E HOSTNAME=$HOSTNAME \
            --env WASSP_DIE_ON_CMD_ERROR=False \
            --continueIfReleaseInvalid \
            -E timeoutTargetAcquisition=180"

# test step
if [ ! -z "$TEST_STEP" ]
then
    wasspEnv="${wasspEnv} --step $TEST_STEP"
fi

# if rerun
if [ ! -z "$RERUN" ]
then
    wasspEnv="${wasspEnv} $RERUN"
fi

scheduler_log=${logpath}/timeStamp
echo "=========================runwassp start running....."
$wasspHome/wassp/host/scheduler/bin/runwassp -D $wasspEnv   -P $scheduler_log  --file ${matrixPath}/$testplan $dampoption
##workaround for last get_target can not be pass.
${wasspHome}/.venv_wassp/bin/python3 $wasspHome/wassp/host/engines/report/testReportHtml.py -v 1 -a  ${logpath}/coreos

## chmod of the Logs dir.
chmod -R 777 ${logpath}/coreos
## clean the tmp folder
rm -rf /tmp/images/
if [ ${EMAIL_LIST} == "none" ] ; then
   echo "There is no mail will send."
else
    ResultMailSend
fi
