#!/bin/bash
# nightly use as : basename $0 -s spinname -t testplan -d domain -b branchname -week week

sourcePath=$(cd $(dirname $0); pwd)

usage() {
    echo "Usage:`basename $0` -spinname spinname -testplan testplan [-matrixpath matrixpath] -d domain [-logpath logpath -mailadr mailadr] -branchname branchname -week week"
    echo "-s|-spinname"
    echo "The spin name info for email"
    echo "-mr|-matrixpath"
	echo "Test matrix path info email"
    echo "-t|-testplan"
	echo "Test plan name info email"
	echo "-d|-domain"
	echo "The domain,should be CORE or CERT ...."
	echo "-l|-logpath "
    echo "The logpath, if skip,use the default {LogRoot}/{branchname}/{spinname}_{domain}"
	echo "-m|-mailadr"
	echo "The send mail adr,none for not send."
	echo "-b|-branchname"
	echo "The branchname"
	echo "-w|-week"
	echo "week used for ltaf trend pic.such as 2017-02-07,if skip default as the date from the spinname"
    echo "-c|-conf"
    echo "The conf file"	
}

while [ $# -gt 0 ]; do
    case $1 in
        -s|-spinname) shift; spinname=$1 ;;
        -t|-testplan) shift; testplan=$1 ;;
    	-d|-domain) shift;domain=$1 ;;
	    -l|-logpath) shift;logpath=$1 ;;
	    -m|-mailadr) shift;mailadr=$1 ;;
        -mr|-matrixpath) shift;matrixpath=$1 ;;
	    -b|-branchname) shift;branchname=$1 ;;
	    -w|-week) shift;week=$1 ;;
        -c|-conf) shift;configf=$1 ;;
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
## default vaulue
wasspHome=${wasspHome}
LogRoot=${LogRoot}
LogServer=${LogServer}
default_EMAIL_LIST=${default_EMAIL_LIST}

if [ -z $logpath ]
then
    logpath=${LogRoot}/${branchname}/${spinname}_${domain}
else
    logpath=${logpath}
fi

if [ -z $matrixpath ]
then
    matrixpath=${wasspHome}/testmatrices/vxworks7/Nightly
else
    matrixpath=${matrixpath}
fi

# !! cp the result to the Logs server
#zipdate=`date +%Y%m%d_%H%M%S`
#zipdate=`echo $zipdate`
#bash ${wasspHome}/testcases/vxworks7/LTAF_meta/wassp_log.sh $logpath $logpath/../$zipdate
#mv ${logpath}/../${zipdate}_log.zip  ${LogServer}/$branchname/
#cd ${LogServer}/$branchname/
#unzip -o ${zipdate}_log.zip
#rm -rf ${zipdate}_log.zip
#cd -

# get week info
if [ ! -z $week ]
then 
 week=$week
else
    temval=$(echo ${spinname}_${domain}|awk -F _ '{print $1}')
    temval=$(echo $temval | grep -o '[0-9]\+')
    Yearval=`echo ${temval:0:4}`
    Monval=`echo ${temval:4:2}`
    Dayval=`echo ${temval:6:2}`
    week=$Yearval-$Monval-$Dayval
fi

# get tr_domain info for LTAF
# Tr_domain=${domain}
# because cert is import to core 
Tr_domain=${domain}
if [ ${Tr_domain} == "cert" ]
then
Tr_domain=mw
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

# call ltaf script 
cd ${wasspHome}/testcases/vxworks7/LTAF_meta
LTAF_Project=${branchname}
bash ltaf_vxworks.sh -sprint Nightly  -week $week -ltaf $LTAF_Project -Logs  ${logpath}/  -domain $Tr_domain -spin $spinname -tester cye -nightly -update
rm -rf ${logpath}/LTAF/vxworks7
cd -

# add the check of the LTAF result.
cmdret=$(curl "http://pek-lpgtest3.wrs.com/ltaf/nightly_interface.php?release_name=${LTAF_Project}&f_type=info&date=$week")
check=$(echo $cmdret|grep "ERROR")
if [ ! -z "$check" ]
then
  echo "Meet error when put the result to LTAF"
  exit 1
fi

# which will analysis the result for the test report
function ResultMailSend {
  FROM=WASSP-Nightly
  echo "------result mail send file-------\n"
  EMAIL_LIST=$EMAIL_LIST
  JSON_FILE=${logpath}/Summary/summary.json
  TEMPMESSAGE="${logpath}/tmp/emailmessage.tmp"
  mkdir -p ${logpath}/tmp/
# remove ^M characters
  tr -d '\r' < $JSON_FILE > $TEMPMESSAGE && mv $TEMPMESSAGE $JSON_FILE
# Catch total test runs from json file
  TOTAL=0
  TOTAL=`cat $JSON_FILE | grep "testRunCount"`
  TOTAL_NUM="${#TOTAL}"
  TOTAL=${TOTAL:20:$TOTAL_NUM-20}
  echo Total: ${TOTAL//[,]/}
# Catch PASSED test runs from json file
  PASS=0
  PASS=`cat $JSON_FILE | grep "passes"`
  PASS_NUM="${#PASS}"
  PASS=${PASS:14:$PASS_NUM-14}
  echo PASS: ${PASS//[,]/}
# Calculate passrate
  totalnum=`echo $TOTAL | sed 's/,//g' | sed 's/ //g'`
  passnum=`echo $PASS | sed 's/,//g' | sed 's/ //g'`
  PASSRATE=`echo "scale=2; $passnum*100/$totalnum" | bc`
  echo PASSRATE: $PASSRATE%
# Catch Exec Fail test runs from json file
  EXECFAIL=`cat $JSON_FILE | grep "Exec FAIL"`
  EXECFAIL_NUM="${#EXECFAIL}"
   if [ $EXECFAIL_NUM == 0 ]
  then
     EXECFAIL=0
  else
     EXECFAIL=${EXECFAIL:20:$EXECFAIL_NUM-20}
  fi
  echo Exec Fail: ${EXECFAIL//[,]/}
# Catch FAIL test runs from json file
  FAIL=`cat $JSON_FILE | grep -w "\"FAIL\""`
  FAIL_NUM="${#FAIL}"
  if [ $FAIL_NUM == 0 ]
  then
     FAIL=0
  else
      FAIL=${FAIL:15:$FAIL_NUM-15}
  fi
  echo Fail: ${FAIL//[,]/}
# Catch BOOT_FAIL test runs from json file
  BOOTFAIL=`cat $JSON_FILE | grep "Boot Fail"`
  BOOTFAIL_NUM="${#BOOTFAIL}"
  if [ $BOOTFAIL_NUM == 0 ]
  then
       BOOTFAIL=0 
  else
       BOOTFAIL=${BOOTFAIL:20:$BOOTFAIL_NUM-20}
  fi
  echo Boot Fail: ${BOOTFAIL//[,]/}
# Catch TIMEOUT test runs from json file
  TIMEOUT=`cat $JSON_FILE | grep "TIMEOUT"`
  TIMEOUT_NUM="${#TIMEOUT}"
  if [ $TIMEOUT_NUM == 0 ]
  then
     TIMEOUT=0
  else
      TIMEOUT=${TIMEOUT:18:$TIMEOUT_NUM-18}
  fi
  echo TIMEOUT: ${TIMEOUT//[,]/}
# Catch EXECBLK test runs from json file
  EXECBLK=`cat $JSON_FILE | grep "No Target"`
  EXECBLK_NUM="${#EXECBLK}"
  if [ $EXECBLK_NUM == 0 ]
  then
       EXECBLK=0
  else
       EXECBLK=${EXECBLK:22:$EXECBLK_NUM-22}
  fi
  echo Exec Block: ${EXECBLK//[,]/}
# Catch BUILDFAIL test runs from json file
  BUILDFAIL=`cat $JSON_FILE | grep "Build Fail"`
  BUILDFAIL_NUM="${#BUILDFAIL}"
  if [ $BUILDFAIL_NUM == 0 ]
  then
      BUILDFAIL=0
  else
      BUILDFAIL=${BUILDFAIL:22:$BUILDFAIL_NUM-22}
  fi
  echo Build Fail: ${BUILDFAIL//[,]/}
# Catch EXCEPTION test runs from json file
  EXCEPTION=0
  EXCEPTION=`cat $JSON_FILE | grep "EXCEPTION"`
  EXCEPTION_NUM="${#EXCEPTION}"
  if [ $EXCEPTION_NUM == 0 ]
  then
     EXCEPTION=0
  else
     EXCEPTION=${EXCEPTION:20:$EXCEPTION_NUM-20}
  fi
  echo EXCEPTION: ${EXCEPTION//[,]/}
# Catch BLOCK test runs from json file
  BLOCK=`cat $JSON_FILE | grep "BLOCK"`
  BLOCK_NUM="${#BLOCK}"
  if [ $BLOCK_NUM == 0 ]
  then 
      BLOCK=0
  else
      BLOCK=${BLOCK:20:$BLOCK_NUM-20}
  fi
  echo BLOCK: ${BLOCK//[,]/}

# Catch the DVD info from jason file.
  DVDINFO=`cat $JSON_FILE | grep "dvdDir"`
  DVDINFO_LENGTH="${#DVDINFO}"
  DVD_DIR=`echo ${DVDINFO:15:$DVDINFO_LENGTH-16} |sed 's/\",//g'`
  #LASTCOMMIT=`cd $DVD_DIR && git Logs -1|grep "commit"`
  WASSP_TAG=$domain

Test_Start=`cat $JSON_FILE | grep "date"`
Test_Start=${Test_Start:12}
Test_Start=${Test_Start//[,]/}
Test_Start=${Test_Start//\"/}
WeekAGO=`date -d " 2 week ago" +%Y-%m-%d`
scheduler_log=${logpath}/timeStamp
SCHEDULER_LOG=`/bin/ls -rt ${scheduler_log}/WASSP_schedLog*.txt | tail -1`
TOTAL_TIME_SUMMARY=`cat -n $SCHEDULER_LOG | grep "Total time"`
echo "00000 $SCHEDULER_LOG"
TOTAL_HOURS=`echo $TOTAL_TIME_SUMMARY | grep -o -P '.{0,3}hours' | tr -d '[:alpha:]'`
TOTAL_MINUTES=`echo $TOTAL_TIME_SUMMARY | grep -o -P '.{0,3}minutes' | tr -d '[:alpha:]'`
TOTAL_SECONDS=`echo $TOTAL_TIME_SUMMARY | grep -o -P '.{0,3}seconds' | tr -d '[:alpha:]'`
echo "Total Time is  $TOTAL_HOURS $TOTAL_MINUTES $TOTAL_SECONDS"
TOTAL_TIME=`echo ${TOTAL_HOURS}:$(printf "%02d" ${TOTAL_MINUTES}):$(printf "%02d" ${TOTAL_SECONDS}) |sed "s/ //g"`
 
wassp_version=`eval export PATH=$wasspHome/wassp-nest/tools/bin:$wasspHome/wassp/host/scheduler/bin:${PATH} && runwassp --version|tail -1`
wassp_version=`echo $wassp_version|awk  -F ':'  '{print $2}' `
SUBJECT="VxWorks 7 MW Nightly Testing Report ($week) "
if [[ ! -z "$MailTitle" ]]; then
    SUBJECT="${SUBJECT}-$MailTitle"
fi

SUMMARY_FILE=${logpath}/Summary/summary.html
EMAILMESSAGE="${logpath}/tmp/emailmessage.html"
echo -e '<basefont face="arial" size="4">' > $EMAILMESSAGE
echo -e '<head><style>body {background-image:url("http://$(hostname)/${wasspHome}/wassp/host/engines/report/template/wassp2.png");background-repeat:no-repeat;background-position:right top;}' >> $EMAILMESSAGE
echo -e 'table, td, th{border:1px solid black;}th{background-color:powderblue;color:blue;}</style></head>' >> $EMAILMESSAGE
echo -e "<font face="arial" size="6"> VxWorks 7 Nightly Test On DVD: $spinname </font><br><br>" >> $EMAILMESSAGE

## Testing Summary
echo -e "<b> 1.Testing Summary</b>" >> $EMAILMESSAGE
echo -e "<table style="font-family:Arial"><thead><tr><th width="100">Total</th><th width="100">Pass</th><th width="100">Passrate</th><th width="150">Elapsed Time</th></tr></thead>" >> $EMAILMESSAGE
echo -e "<tbody><tr><td align="center">${TOTAL//[,]/}</td><td align="center">${PASS//[,]/}</td><td align="center">$PASSRATE%</td><td align="center">$TOTAL_TIME</td></tr></tbody></table>" >> $EMAILMESSAGE
echo -e "<br>" >> $EMAILMESSAGE
echo -e "<table style="font-family:Arial"><thead><tr><th width="100">BuildFail</th><th width="100">ExecFail</th><th width="100">Fail</th><th width="100">Timeout</th><th width="100">BootFail</th><th width="100">NoTarget</th><th width="100">WASSP Exception</th><th width="100">Block</th></tr></thead>" >> $EMAILMESSAGE
echo -e "<tbody><tr><td align="center">${BUILDFAIL//[,]/}</td><td align="center">${EXECFAIL//[,]/}</td><td align="center">${FAIL//[,]/}</td><td align="center">${TIMEOUT//[,]/}</td><td align="center"> ${BOOTFAIL//[,]/}</td><td align="center">${EXECBLK//[,]/}</td><td align="center">${EXCEPTION//[,]/}</td><td align="center">${BLOCK//[,]/}</td></tr></tbody></table><br>" >> $EMAILMESSAGE

# Begin the Trend graph 
PIC=${logpath}/tmp/Trend.png
STARTDATE=$WeekAGO
ENDDATE=$(echo $Test_Start)
wget -O ${PIC} "http://pek-lpgtest3.wrs.com/ltaf/nightly_interface.php?release_name=${LTAF_Project}&f_type=chart&start_date=${STARTDATE}&end_date=${ENDDATE}&component=${Tr_domain}"
imgLink="http://pek-lpgtest3.wrs.com/ltaf/"
echo -e "<a><img src="cid:chartImage"  border="0" align="absmiddle" alt="Trend Figure" title="Week Trend PIC"></a>" >> $EMAILMESSAGE
echo -e "<br>" >> $EMAILMESSAGE
echo -e "<br>" >> $EMAILMESSAGE
	
# LTAF link
MANGODBLINK="<a href='http://pek-lpgtest3.wrs.com/ltaf/nightly_results.php?releasename=${LTAF_Project}&clearfilter=true&tf_tr_whentostart=${week}&tf_test_component=${Tr_domain}'>LTAF Report</a>"
echo -e '<table style="font-family:Arial"><tbody>' >> $EMAILMESSAGE
echo -e "<tr><th width="200">LTAF Link</th><td width="800"><a href='http://pek-lpgtest3.wrs.com/ltaf/nightly_results.php?releasename=$LTAF_Project&clearfilter=true&tf_tr_whentostart=${week}&tf_test_component=${Tr_domain}'>http://pek-lpgtest3.wrs.com/ltaf/nightly_results.php?releasename=$LTAF_Project&clearfilter=true&tf_tr_whentostart=${week}&tf_test_component=${Tr_domain}</a></b></td></tr>" >> $EMAILMESSAGE
echo -e "</tbody></table><br>"  >> $EMAILMESSAGE

# Defect list
if [ ! -z "$FAIL" ] && [ "$FAIL" != "0" ]
then
    echo -e "<br>" >> $EMAILMESSAGE
    echo -e "<b> Open Defects:</b>" >> $EMAILMESSAGE
    echo -e '<table style="font-family:Arial"><tbody>' >> $EMAILMESSAGE
    JIRA_FILTER_ID=31573
    DEFECT_LIST=${logpath}/tmp/defect_list.html
    source ${sourcePath}/listDefects.sh $DEFECT_LIST $JIRA_FILTER_ID
    echo -e "<tr><td></td>`cat $DEFECT_LIST`</tr>"  >> $EMAILMESSAGE
    echo -e "</tbody></table><br>"  >> $EMAILMESSAGE
fi

# end the Trend graph
echo -e "<br>" >> $EMAILMESSAGE
echo -e "<br>" >> $EMAILMESSAGE
 
## Test Details
echo -e "<b> 2.Testing Details:</b>" >> $EMAILMESSAGE
echo -e '<table style="font-family:Arial"><tbody>' >> $EMAILMESSAGE
echo -e "<tr><th width="200">Test Server</th><td>$(hostname)</td></tr>" >> $EMAILMESSAGE
echo -e "<tr><th width="200">WIND_HOME</th><td><a>$DVD_DIR</a></td></tr>" >> $EMAILMESSAGE
echo -e "<tr><th width="200">Test Matrix</th><td><a href="http://$(hostname)/$matrixpath/$testplan">$testplan</a></td></tr>" >> $EMAILMESSAGE
echo -e "<tr><th width="200">TotalTime</th><td>$TOTAL_TIME</td></tr>" >> $EMAILMESSAGE
echo -e "<tr><th width="200">WASSP HOME</th><td><a>$wasspHome</a></td></tr>" >> $EMAILMESSAGE
echo -e "<tr><th width="200">WASSP VERSION</th><td><a>$wassp_version</a></td></tr>" >> $EMAILMESSAGE
echo -e "<tr><th width="200">HTML LOG</th><td><a href="http://$(hostname)/${logpath}/Summary/summary.html">http://$(hostname)/${logpath}/Summary/summary.html</a></td></tr>" >> $EMAILMESSAGE
echo -e "</tbody></table><br>"  >> $EMAILMESSAGE
tr -d '\r' < $EMAILMESSAGE > $TEMPMESSAGE && mv $TEMPMESSAGE $EMAILMESSAGE

### using python script to send out the mail
export MAIL_SUBJECT=$SUBJECT
export MAIL_TO=$EMAIL_LIST
export MAIL_TXT=$EMAILMESSAGE
python $sourcePath/mail_map.py

}

# clean the tmp folder
rm -rf /tmp/images/ 

if [ ${EMAIL_LIST} == "none" ] ; then
   echo "There is no mail will send."
else
    ResultMailSend
fi

