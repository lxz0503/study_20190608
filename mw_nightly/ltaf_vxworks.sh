#!/bin/bash
#
# ltaf_vxworks.sh - import test result to LTAF server
#
# Copyright (c) 2017-2020 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
# modification history
# --------------------
# 06may20,zyj  replace domain name from bsp to riscv if bsp is sifive_generic
# 28apr20,zyj  change the '&' character in domain name to '\&'
# 27apr20,zyj  set environment $USER as default tester
# 26apr20,zjl  added external ltaf result directory and case repos support
# 08aug19,h_l  add WASSP_HELIX_CONF search in testRun.xml
# 05aug19,h_l  add -configuration parameter
# 31jul19,h_l  add curl result check for "Successfully
# 26apr19,h_l  add ":" when search case name keyword for "XXX1:" and "XXX:"
#              different test cases. 
# 31jan19,zyj  remove quotation mark in bspName
# 16jan19,h_l  revert host os value to environment_hostos 
# 14jan19,h_l  add -spin parameter and update host os and tester support.
# 28dec18,pzh  align the date format with ISO, use %g%V for year and week
# 24dec18,pzh  change week format from weekxx to weekyyxx
# 10dec18,h_l  replace domain value from bsp to specific arch for nightly test
# 21nov18,zjl  add grep -v EXEC_CONSOLE for run_result check 
# 28sep18,h_l  import to ltaf and upload Logs controled by diff parameter
# 14sep18,h_l  do not cover LTAF_WEEK from capital to lowercase 
# 14sep18,h_l  fix LTAF_WEEK issue when it contian space
# 03sep18,h_l  change %U to %W for ltaf week
# 23aug18,h_l  change helix search key word
# 13aug18,h_l  add weekly and SpinType support
# 18jul18,h_l  do not upload to LTAF when no target
# 17apr18,h_l  add -noLogUpload option
# 07feb18,h_l  double check vxTest Logs format as sometimes "vxTestOptions"
#        ,     is print out as "vxTes-> tOptions:"
# 02jan18,h_l  add -httpServer and -caseGitRepo parameter
# 15nov17,h_l  remove unnecessary ltaf upload retry
# 06nov17,jie  support group test name get.
# 10oct17,h_l  select latest test Logs by file name
# 28aug17,h_l  add curl retry when network is not stable
# 22aug17,pzh  fix line 902 miss backquote
# 31may17,jie  fix tracebility issue in test case list
# 10feb17,h_l  support upload specific test result with "select" parameter
# 16jan17,h_l  created
#

myName=`basename $0`

ppcBspList=("fsl_mpc82xx" "fsl_p1p2" "fsl_p3p4p5" "fsl_t1" "fsl_t2t4" "qsp_ppc")
armBspList=("fsl_imx6" "fsl_imx6sx_m4" "fsl_k70" "fsl_vf610_a5" "fsl_vf610_m4" "itl_arria10" "itl_cyclone5" "nxp_imx8" "nxp_layerscape_a7" "nxp_layerscape_a53")
iaBspList=("itl_generic" "vxsim")
riscvBspList=("sifive_generic")

ltaf_result () {
    local logDir=$1
    local TestName=$2 
    echo "*** TestName is $TestName"
    cfileTestList=""
    ############################################################################
    for one in `find $logDir -mindepth 1 -name "testRun.xml"`
    do
        #### begin to generate the test result for each valid instances
        ###begin to check test cases list of each wassp cases.
        restultdir=$(dirname $one)

        existed=$(grep -m 1 "packagename=\"helix\"" $one)
        if [ -z "$existed" ]
        then
            spinType_value="native"
        else
            spinType_value="helix"
        fi

        # if we have input parameter from command line, we will use it, else we will find in xml file.
        helixConfigValue=""
        if [ -z "$helixConfigParam" ]
        then
            helixConfigValue=`grep -m 1 "WASSP_HELIX_CONF=" $one|awk -F 'WASSP_HELIX_CONF=' '{print $2}'`
            helixConfigValue=$(echo ${helixConfigValue%%' '*})
            helixConfigValue=${helixConfigValue/\"/} 
            helixConfigValue=${helixConfigValue/\"/} 
        else
            helixConfigValue=$helixConfigParam
        fi
        
        if [ "$debug_flag" == 1 ]
        then
            echo -e "helixConfigValue is $helixConfigValue"
        fi
        
        testName=`grep -m 1 "primary_test_case=" $one|awk -F 'primary_test_case=' '{print $2}'`
        testName=$(echo ${testName%%' '*})

        uriName=`grep  'uri=' $one|grep -m 1  $testName|awk -F 'uri=' '{print $2}'`
        uriName=$(echo ${uriName%%' '*})

        gitRepoLastDirname=`basename $caseGitRepo`
        uriLink=${uriName#*${gitRepoLastDirname}\/}
        uriLink=${uriLink%%\"/*}
        if [ -z "$uriLink" ]
        then
            trapname=`echo $testName|sed 's/\"//g'`
            caseFolder=$caseGitRepo/$trapname
        else
            caseFolder=$caseGitRepo/$uriLink
        fi
        
        if [ "$debug_flag" == 1 ]
        then
            echo -e "caseFolder is $caseFolder"
        fi

        
        if [ -z "$cfileTestList" ]
        then
            caseConfList=$(find $caseFolder -name "test_case.conf")
            
            if [ "$debug_flag" == 1 ]
            then
                echo -e "caseConfList is $caseConfList"
            fi

            ####################################################################
            for testfile in $caseConfList
            do
                testComponent=`grep -m 1 'COMPONENT=' $testfile |awk -F 'COMPONENT=' '{print $2}'`
                echo -e $COMPONENT
                testComponent=`echo $testComponent`   #remove space char in string
                
                
                ctestfile=$(grep -m 1 "TEST_CASE_LIST" $testfile)
                ctestfile2=$(awk '/TEST_CASE_LIST/{while(getline)if($0!~/GIT_LINK/)print;else exit}' $testfile)
                ctestfile="$ctestfile $ctestfile2"

                
                if [ ! -z "$ctestfile" ]
                then
                    tempCfile=`echo $tempCfile`
                    tempCfile=${ctestfile#*\=}
                    #tempCfile=${tempCfile%%\"*}
                  
                    if [ "$debug_flag" == 1 ]
                    then
                        echo -e "tempCfile is $tempCfile END"
                    fi
                  
                    for testone in $tempCfile
                    do
                        if [ "$debug_flag" == 1 ]
                        then
                            echo -e "testone is $testone cfileTestList is $cfileTestList"
                        fi
                        existed=$(echo $cfileTestList |grep "$testone")
                        if [ -z "$existed" ]
                        then
                            cfileTestList="$cfileTestList $testone"
                            #echo "cfileTestList  is $cfileTestList"
                        fi
                    done
                fi
            done
            ########################################################################
            
            if [ "$debug_flag" == 1 ]
            then
                echo -e "cfileTestList is $cfileTestList"
            fi
          
            #### remove the \" from the cfileTestList
            cfileTestList=${cfileTestList/\"/} 
            
            if [ "$debug_flag" == 1 ]
            then
                echo "after remove \", cfileTestList is $cfileTestList"
            fi
                
        fi    # end of if [ -z "$cfileTestList" ]

        
        #### begin to generate the test result for each valid instance
        ########################################################################
        for cone in $cfileTestList
        do
            testCfile=$cone
            testCfile=$(echo $testCfile|awk -F ":" '{print $1}')
            testCkey=${testCfile/\"/}
            testCkey=${testCfile/\"/}
            testCkey=${testCkey%%.*}
            
            testCfile=${testCfile/\"/}
            if [ "$debug_flag" == 1 ]
            then
                echo -e "in for loop, testCfile is $testCfile testResultNum is $testResultNum"
            fi

            if [ -z "$testCfile" ]
            then
                continue
            fi
            
            ### analysis the topology.jason file and get the tag and replace in ini file.
            #### bspa
            instanceDir=$(dirname $one)
            instanceFile=${instanceDir}/topology.json

            ####################################################################
            if [ -f "$instanceFile" ]
            then
                #### topology.json exist that means the  build success.
                bspName=$(grep -Po '"bsp":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                
                if [ -z "$bspName" ]
                then
                    bspName=$(grep -Po '"bsp": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    bspName=${bspName//\}/}
                fi
            
                bspName=${bspName//\"/}
                bspName=${bspName//,/}
                bspName=$(echo "$bspName" | grep -o "[^ ]\+\( \+[^ ]\+\)*")

                ### one states that the test based on cpu (vsb create based on CPU)
       
                #### check about the cpuname
                cpuName=$(grep -Po '"cpuname":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                if [ -z "$cpuName" ]
                then
                    cpuName=$(grep -Po '"cpuname": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    cpuName=${cpuName//\}/}
                fi
                cpuName=${cpuName//\"/}
                cpuName=${cpuName//,/}
                cpuName=$(echo "$cpuName" | grep -o "[^ ]\+\( \+[^ ]\+\)*")      
                
                if [ ! -z "$cpuName" ]
                then
                    bspName="${bspName}:${cpuName}"
                fi
                
                #### Tool
                toolName=$(grep -Po '"tool":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                if [ -z "$toolName" ]
                then
                    toolName=$(grep -Po '"tool": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    toolName=${toolName//\}/}
                fi
                toolName=${toolName//\"/}
                toolName=${toolName//,/}
                toolName=$(echo "$toolName" | grep -o "[^ ]\+\( \+[^ ]\+\)*")
                #### LTAF_BARCODE
                barcode=$(grep -Po '"barcode":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                if [ -z "$barcode" ] 
                then   
                    barcode=$(grep -Po '"barcode": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    barcode=${barcode//\}/}
                fi    
                barcode=${barcode//\"/}
                barcode=${barcode//,/}
                barcode=$(echo "$barcode" | grep -o "[^ ]\+\( \+[^ ]\+\)*")
                #### LTAF config
                config_label=$(grep -Po '"config_label":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                if [ -z "$config_label" ] 
                then   
                    config_label=$(grep -Po '"config_label": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    config_label=${config_label//\}/}
                fi    
                config_label=${config_label//\"/}
                config_label=${config_label//,/}
                config_label=$(echo "$config_label" | grep -o "[^ ]\+\( \+[^ ]\+\)*")
                #### LTAF_TECH
                tech=$(grep -Po '"tech":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                if [ -z "$tech" ] 
                then   
                    tech=$(grep -Po '"tech": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    tech=${tech//\}/}
                fi    
                tech=${tech//\"/}
                tech=${tech//,/}
                tech=$(echo "$tech" | grep -o "[^ ]\+\( \+[^ ]\+\)*") 
                #### Board Name
                board_name=$(grep -Po '"board_name":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                if [ -z "$board_name" ]
                then
                    board_name=$(grep -Po '"board_name": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    board_name=${board_name//\}/}
                fi
                board_name=${board_name//\"/}
                board_name=${board_name//,/}
                board_name=$(echo "$board_name" | grep -o "[^ ]\+\( \+[^ ]\+\)*")
                #### options Name
                options=$(grep -Po '"options":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                if [ -z "$options" ]
                then
                    options=$(grep -Po '"options": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    options=${options//\}/}
                fi
                
                options=${options//\"/}
                options=${options//,/}
                options=$(echo "$options" | grep -o "[^ ]\+\( \+[^ ]\+\)*")
                #### vsbOptions Name

                vsboptions=$(grep -Po '"vsboptions":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                if [ -z "$vsboptions" ]
                then
                    vsboptions=$(grep -Po '"vsboptions": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    vsboptions=${vsboptions//\}/}
                fi
                vsboptions=${vsboptions//\"/}
                vsboptions=${vsboptions//,/}
                vsboptions=$(echo "$vsboptions" | grep -o "[^ ]\+\( \+[^ ]\+\)*")
                #### buildoptions
                buildoptions=$(grep -Po '"buildoptions":.*?[^\\],' $instanceFile |awk -F : '{print$2}')
                if [ -z "$buildoptions" ]
                then
                    buildoptions=$(grep -Po '"buildoptions": .*?[^\\]*.' $instanceFile |awk -F : '{print$2}')
                    buildoptions=${buildoptions//\}/}
                fi
                buildoptions=${buildoptions//\"/}
                buildoptions=${buildoptions//,/}
                buildoptions=$(echo "$buildoptions" | grep -o "[^ ]\+\( \+[^ ]\+\)*")
                ### Build and Fail result comes from statusTestRun.Logs
                #### LTAF_BUILD
                resultdir=$(dirname $one)


                ################################################################
                if [ "$Plan_only" == 0 ]
                then
                    run_result=Blocked
                    run_detail_result="noTargets"
                    #### add the status of the  func_pass and func_fail
                    vxTest_details_pass="0"
                    vxTest_details_fail="0"

                    execution_done=0
                    #### check if it is the vxTest Logs. if the vxTest Logs. check the test Logs.
                    #### build status.
                    #check statusTestRun.Logs file first
                    resultFile=$resultdir/statusTestRun.Logs
                    r_build=$(grep "BUILD_PASS" $resultFile)
                    
                    if [ ! -z "$r_build" ]
                    then
                         build_result=PASS
                    else   
                         build_result=FAIL
                    fi
                    
                    ### analysis the the no Targets states
                    exec_ino=$(grep "EXEC_*" $resultFile|grep -v EXEC_CONSOLE|tail -1)
                    #exec_other=$(grep "EXEC_SKIP" $resultFile|tail -1)
                    notargets=""
                    notargets=$(echo $exec_ino|grep -E "EXEC_NOTARGETAVAILABLE|EXEC_NOTARGETTIMEOUT")
                    if [ ! -z "$notargets" ]
                    then
                        run_result=Blocked
                        run_detail_result="noTargets"
                        #For no target error, we will not
                        #import test result to LTAF, if we have plan in LTAF,  
                        #test case will still be "NOT_STARTED"
                        if [ "$debug_flag" == 1 ]
                        then
                            echo -e "skip LTAF import for EXEC_NOTARGETAVAILABLE or EXEC_NOTARGETTIMEOUT"
                        fi
                        continue
                    fi
                    
                    r_exec=$(echo $exec_ino|grep "EXEC_PASS")
                    
                    if [ ! -z "$r_exec" ]
                    then
                        run_result=PASS
                        run_detail_result=PASS
                        build_result=PASS
                        execution_done=1
                    fi
                    
                    fail_exec=$(echo $exec_ino|grep "EXEC_FAIL")
 
                    if [ ! -z "$fail_exec" ]
                    then
                        run_result=FAIL
                        run_detail_result=fail
                        execution_done=1
                    fi
                    
                    timeout_exec=$(echo $exec_ino|grep "EXEC_TIMEOUT")
 
                    if [ ! -z "$timeout_exec" ]
                    then
                        run_result=FAIL
                        run_detail_result=fail
                    fi
                             
                    execption_exec=$(echo $exec_ino|grep "EXEC_EXCEPTION")
                    if [ ! -z "$execption_exec" ]
                    then
                        run_result=FAIL
                        run_detail_result=fail
                    fi
                    
                    ### in new-version of WASSP have the EXEC_SKIP status, we set as fail
                    exec_other=$(echo $exec_ino|grep "EXEC_SKIP")
                    if [ ! -z "$exec_other" ]
                    then

                        #For EXEC_SKIP, this should be boot fail, we will not
                        #import test result to LTAF, if we have plan in LTAF,  
                        #test case will still be "NOT_STARTED"
                        if [ "$debug_flag" == 1 ]
                        then
                            echo -e "skip LTAF import for EXEC_SKIP"
                        fi
                        continue
                    fi
 
                    #### first get the result
                    if [ "$debug_flag" == 1 ]
                    then
                        echo -e "result dir is $resultdir"
                    fi
                    
                    runlogList=""
                    runlogList=`find $resultdir -name "target_*.log"  -a ! -name "target_host*.log" `

                    if [ -z "$runlogList" ]
                    then
                        ### don't find the runlog, Skip the assign the details.
                        if [ "$debug_flag" == 1 ]
                        then
                            echo "no avaiable vxTest log"
                        fi
                              
                        vxTest_details_total="1"
                        if [ "$run_result" == "Blocked" ]
                        then
                            vxTest_details_pass="0"
                            vxTest_details_fail="0"
                        fi
                        
                        if [ "$run_result" == "PASS" ]
                        then
                            vxTest_details_pass="1"
                            vxTest_details_fail="0"
                        fi
                        if [ "$run_result" == "FAIL" ]
                        then
                            vxTest_details_pass="0"
                            vxTest_details_fail="1"
                        fi
                    else
                        runlog=""
                        latestTimeStamp=""

                        for logItem in $runlogList
                        do

                            currentTimeStamp=${logItem#*target_*_B*_}
                            currentTimeStamp=${currentTimeStamp%.Logs}
                            part2=${currentTimeStamp#*_}
                            part1=${currentTimeStamp%_*}
                            currentTimeStamp=${part1}${part2}
            
                            if [ "$runlog" == "" ]
                            then
                                runlog=$logItem
                                latestTimeStamp=$currentTimeStamp
                                continue
                            fi
        
                            if [[ $currentTimeStamp -gt $latestTimeStamp ]]
                            then
                                runlog=$logItem
                                latestTimeStamp=$currentTimeStamp
                            fi
                        done
                        
                        if [ "$debug_flag" == 1 ]
                        then
                            echo "latest run log is $runlog"
                        fi
                        
                        #### check if is a vxTest format report
                        vxTest_details_pass=0
                        vxTest_details_fail=0
                        vxTest_details_abort=0
                        vxTest_details_total=0
                        vxTestReport=$(grep "vxTestOptions" $runlog)
                        
                        if [ -z "$vxTestReport" ]
                        then
                            ### double check, as sometimes "vxTestOptions" is print out as "vxTes-> tOptions:" in kernel shell
                            vxTestReport=$(grep "vxTest Options Summary:" $runlog)
                        fi
                        
                        summary_details=""
                        if [ -z "$vxTestReport" ]
                        then
                            if [ "$debug_flag" == 1 ]
                                then
                                    echo "$runlog is not vxTest format"
                            fi
                            
                            if [ "$run_result" == "PASS" ]
                            then
                                vxTest_details_pass="1"
                                vxTest_details_fail="0"
                            else
                                vxTest_details_pass="0"
                                vxTest_details_fail="1"
                            fi
                            summary_details=$(grep "MRES Benchmarks Functions" $runlog)   # added for performance test
                            
                        else
                            summary_details=$(grep "MRES" $runlog|grep "${testCkey}:"|tail -1)
                            if [ -z "$summary_details" ]
                            then
                                if [ "$debug_flag" == 1 ]
                                then
                                    echo "we do not find MRES keyword or key $testCkey in vxTest log $runlog"
                                    echo "we will not change LTAF, just leave it as what it was"
                                fi
                                #For vxTest report, we do not find Logs like below format
                                #"MRES tmCacheDmaMallocLib:1 TESTS=4 PASSES=2 FAILS=0 ABORTS=0 SKIPS=2 EXC_TIME=0 ticks"
                                #so we do nothing here, just leave it as it is
                                #we have considered to mark it as "Will Not Run"
                                #but this will bring us more effort to delete these "Will Not Run" cases manually in LTAF
                                continue
                            fi      # fi for if [ -z "$summary_details" ]
                        fi   # fi for if [ -z "$vxTestReport" ]
                        
                        if [ ! -z "$summary_details" ]
                        then
                                #echo "nnnnn $testCkey  summmary_details is $summary_details"
                                vxTest_details_pass=$(echo $summary_details|grep -o "PASSES=[0-9]*")
                                vxTest_details_pass=${vxTest_details_pass#*=}
                                vxTest_details_pass=`echo $vxTest_details_pass`
                                vxTest_details_fail=$(echo $summary_details|grep -o "FAILS=[0-9]*")
                                vxTest_details_fail=${vxTest_details_fail#*=}
                                vxTest_details_fail=${vxTest_details_fail//logWrite/}
                                vxTest_details_fail=${vxTest_details_fail//\*/}
                                vxTest_details_fail=${vxTest_details_fail//\//}
                                vxTest_details_fail=${vxTest_details_fail//tc/}
                                vxTest_details_fail=${vxTest_details_fail%%Logs*}
                                vxTest_details_abort=$(echo $summary_details|grep -o "ABORTS=[0-9]*")
                                   
                                vxTest_details_abort=${vxTest_details_abort#*=}
                                vxTest_details_abort=${vxTest_details_abort//logWrite/}
                                vxTest_details_abort=${vxTest_details_abort//\*/}
                                vxTest_details_abort=${vxTest_details_abort//\//}
                                vxTest_details_abort=${vxTest_details_abort//tc/}
                                vxTest_details_abort=${vxTest_details_abort%%Logs*}
                                    
                                if [ "$vxTest_details_abort" -gt 0 ]
                                then
                                    vxTest_details_fail=`expr $vxTest_details_fail + $vxTest_details_abort`
                                fi
                                   
                                vxTest_details_fail=`echo $vxTest_details_fail`
                                 #### total number
                                vxTest_details_total=`expr $vxTest_details_pass + $vxTest_details_fail`
                                 ###
                                    
                                if [ "$vxTest_details_fail" -gt 0 ]
                                then
                                    run_result=FAIL
                                    run_detail_result=FAIL
                                else
                                    run_result=PASS
                                    run_detail_result=PASS
                                fi
                        fi    # fi for if [ ! -z "$summary_details" ]
                            
                                 
                        
                                
                    fi # fi for if [ -z "$runlog" ]
 
                fi # fi for if [ "$Plan_only" == 0 ]
                ################################################################
                
            else    #else for if [ -f "$instanceFile" ]
            
                ##### topology.json not exist
                #run_result=Blocked
   
                
                ##### Build and Fail result comes from statusTestRun.Logs
                #### LTAF_BUILD
                restultdir=$(dirname $one)
                
                if [ "$Plan_only" == 0 ]
                then
                   resultFile=$restultdir/statusTestRun.Logs
                   r_build=$(grep "BUILD_PASS" $resultFile)
                   if [ ! -z "$r_build" ]
                   then
                       build_result=PASS
                   else
                       build_result=FAIL
                   fi
                   ### check about if it is build-only test case
                   buildonly=$(grep "EXEC_STARTED" $resultFile)
                   
                   if [ -z "$buildonly" ]
                   then
                       if [ $build_result == "PASS" ]
                       then
                           run_result=PASS
                           run_detail_result=Pass
                       else
                           run_result=FAIL
                           run_detail_result=fail
                       fi
                   else
                        run_result=Blocked
                        run_detail_result=Blocked
                  
                        #### run result determin "No Target"
                        notarget=$(grep "EXEC_NOTARGETAVAILABLE" $resultFile)
                        if [ ! -z "$notarget" ]
                        then
                            if [ "$debug_flag" == 1 ]
                            then
                                echo -e "find EXEC_NOTARGETAVAILABLE at tail"
                            fi
                            run_result=Blocked
                            run_detail_result="noTargets"
                        fi
                        
                   fi   # fi for if [ -z "$buildonly" ]
                   
                fi # fi for if [ "$Plan_only" == 0 ]
                
                ###### bsp, tool config_label barcode.
                testRunCopy=$restultdir/testRunWorkingCopy.xml 

                
                bspName=""
                toolName=""

                
                bspName=`grep -m 1 'bsp=' $testRunCopy |awk -F 'bsp=' '{print $2}'`
                bspName=$(echo ${bspName%%' '*})
                bspName=${bspName//\"/}
                echo "bsp name is ${bspName}"


                #### cpuname
                cpuName=""
                cpuName=$(grep  -wo 'cpuname=.*' $testRunCopy|awk -F '=' '{print $2}'|head -n 1|awk '{print $1}')


                
                if [ ! -z "$cpuName" ]
                then
                    bspName="${bspName}:${cpuName}"
                fi
              

                toolName=`grep -m 1 'tool=' $testRunCopy |awk -F 'tool=' '{print $2}'`
                toolName=$(echo ${toolName%%' '*})
                                
                #### barcode
                barcode=""
                
                config_label=`grep -m 1 'config_label' $testRunCopy |awk -F 'config_label=' '{print $2}'`
                config_label=$(echo ${config_label%%' '*})
                #echo -e "bspName is $bspName toolName is $toolName config_label is $config_label"

                
                #### tech
                tech=""
                tech=`grep -m 1 'tech=' $testRunCopy |awk -F 'tech=' '{print $2}'`
                tech=$(echo ${tech%%' '*})
                
               
                #### board_name
                board_name=""
                board_name=`grep -m 1 'board_name=' $testRunCopy |awk -F 'board_name=' '{print $2}'`
                board_name=$(echo ${board_name%%' '*})
                


                
                ### build options
                buildoptions=""
                buildcheck=$(grep  -wo 'buildoptions=.*' $testRunCopy|awk -F '=' '{print $2}'|head -n 1)
                buildcheck=${buildcheck%\"*}
                if [ ! -z "$buildcheck" ]
                then
                    buildoptions=${buildcheck}"\""
                fi
                ### options 
                options=""
                optioncheck=$(grep  -wo 'options=.*' $testRunCopy|awk -F '=' '{print $2}'|head -n 1)
                optioncheck=${optioncheck%\"*}
                
                if [ ! -z "$optioncheck" ]
                then
                    options=${optioncheck}"\""
                fi
                
                ### vsbOptions
                vsboptions=""
                vsbcheck=$(grep  -wo 'vsboptions=.*' $testRunCopy|awk -F '=' '{print $2}'|head -n 1)
                vsbcheck=${vsbcheck%\"*}
                if [ ! -z "$vsbcheck" ]
                then 
                    vsboptions=${vsbcheck}"\""
                fi
         
            fi  #fi for if [ -f "$instanceFile" ]
            
            if [ "$debug_flag" == 1 ]
            then
                echo "run_result is $run_result, run_detail_result is $run_detail_result"
            fi
            
            #check whether we only upload specific test result to LTAF
            if [ ! -z "$selected_result" ]
            then
                
                if [ $run_result != $selected_result ]
                then
                    if [ "$debug_flag" == 1 ]
                    then
                        echo "run_result is $run_result, but we only upload test cases with result: $selected_result"
                    fi
                    continue
                fi

            fi

            destIniFile=$ltafRetDir/LTAF/Result/${TestName}_${testResultNum}.ini
            #### check about the exec_result_detail is in skip_list, if existed, exit and continue with next run.
            if [ ! -z "$skip_list" ]
            then
                inList=$(echo $skip_list|grep "$run_detail_result")
               
                if [ ! -z "$inList" ]
                then
                    echo "result in Skip list"
                    rm -rf  $destIniFile
                    continue
                fi
            
            fi
            
            if [ "$debug_flag" == 1 ]
            then
                echo -e "we generate ini file ${TestName}_${testResultNum}.ini"
            fi
            cp  $result_template $destIniFile

            

            ##### we will find the hostos in testRunCopy.xml (only exist in RunCopy.xml)
            testRunCopy=$restultdir/testRunWorkingCopy.xml
            #### hostOS
            hostcheck=$(grep 'environment_hostos' $testRunCopy)
            hostcheck=${hostcheck//</}
            hostcheck=${hostcheck//>/}
            item=""
            
            for item in $hostcheck
            do
                check=$(echo $item|grep "environment_hostos")
                if [ ! -z "$check" ]
                then
                    host_os_name=$(echo $item |awk -F '=' '{print $2}')
                    break
                fi
            done
            
            if [ "$debug_flag" == 1 ]
            then   
                echo "host OS name is $host_os_name"
            fi
            #### User Story, if we found User Story in testRunCopy.xml, then we will using the userStory in that
            #### if user set the -req out side the run cmd, then we will use that REQ number as final REQ.
            testRunCopy=$restultdir/testRunWorkingCopy.xml
            userStory=$(grep  'userStories=*' $testRunCopy)
            if [ -z "$userStory" ] && [ "$debug_flag" == 1 ]
            then
                echo " don't find userStory in WASSP result"
            else
                userStory=${userStory//</}
                userStory=${userStory//>/} 
                item=""     
                for item in $userStory
                do
                    check=$(echo $item|grep "userStories")
                    if [ ! -z "$check" ]
                    then
                        LTAF_REQ=$(echo $item |awk -F '=' '{print $2}')
                        break
                    fi
                done
                
                if [ ! -z "$requirement" ]
                then
                    LTAF_REQ=$requirement
                fi
            fi
            ##### Tester check from testRunWorkingCopy.xml
            testIn=$(grep  'TESTER\=' $testRunCopy)
            
            if [ ! -z "$testIn" ]
            then
                testIn=${testIn//</ }
                testIn=${testIn//>/ }
                item=""
                for item in $testIn
                do
                    check=$(echo $item|grep "TESTER\=")
                    if [ ! -z "$check" ]
                    then
                        LTAF_USER=$(echo $item |awk -F '=' '{print $2}')
                        if [ "$debug_flag" == 1 ]
                        then
                            echo "$LTAF_USER"
                        fi
                        break
                    fi
                done
            fi
            
            ##### TAG get from  testRunWorkingCopy.xml
            tag=$(grep  'DBREPORT_TAGS*' $testRunCopy)
            if [ ! -z "$tag" ]
            then
               tag=${tag//</}
               tag=${tag//>/}
               item=""
               for item in $tag
               do
                   check=$(echo $item|grep "DBREPORT_TAGS")
                   if [ ! -z "$check" ]
                   then
                     LTAF_TAG=$(echo $item |awk -F '=' '{print $2}')
                     break
                   fi
               done
            fi
            
            if [ ! -z "$hostOS" ]
            then
               host_os_name=$hostOS
            fi
         
            if [ -z "$taskID" ]
             then
                taskID="TBD"
            fi
         
            if [ -z  "$result_key" ]
            then
                result_key=""
            fi
            
            if [ -z "$buildoptions" ]
            then
                buildoptions=""
            fi
            
            #### Logs link get
            LTAF_LOG=""
            if [ "$mongDB_link" == "yes" ]
            then
                ### using mongoDB link, need to keep the console Logs under you logfolder
                echo "mongoDB link not support in this verison of LTAF script!! pls remove it"
                exit 1
                test_status=$restultdir/statusTestRun.Logs
                report_console=$( grep "REPORT_CONSOLE" $test_status)
                if [ ! -z "$report_console " ]
                then
                   #mongDBLink="http://report.wrs.com/reportgenerator/matrixtestplat/aaaaaaaa-bbbb-cccc-eeee-ffffffffffff/?main-TOTAL_FORMS=2\&main-INITIAL_FORMS=2\&main-MAX_NUM_FORMS=20\&main-0-filter=project\&main-0-options=VxWorks\\+7.0\&main-1-filter=test\\+id\&main-1-options=$testid\&mainform-submit=Search" 
                   consoleLog=$(echo $report_console | awk -F '=' '{print $2}')
                   ### some consolelog have some extra word after the result. we remove it first
                    consoleLog=$(echo $consoleLog | awk  '{print $1}')
                   consoleLog=$(basename $consoleLog)
                   consoleLog=${logFolder}/consolelogs/$consoleLog
                   testid=""
                   testid=$(grep "INFO: Finished saving test result*" $consoleLog)
                   if [ ! -z "$testid" ]
                   then
                     testid=${testid//INFO: Finished saving test result /}
                     testid=${testid// to database/}
                     testid=$(echo $testid)
                     mongDBLink="http://report.wrs.com/reportgenerator/matrixtestplat/aaaaaaaa-bbbb-cccc-eeee-ffffffffffff/?main-TOTAL_FORMS=2\&main-INITIAL_FORMS=2\&main-MAX_NUM_FORMS=20\&main-0-filter=project\&main-0-options=VxWorks\\+7.0\&main-1-filter=test\\+id\&main-1-options=$testid\&mainform-submit=Search"
                     LTAF_LOG=$mongDBLink
                     echo "testid is $testid  LTAF_LOG is $LTAF_LOG"
                   else
                     LTAF_LOG="not find in mongoDB"
                   fi
                fi
            else
                ### if not specify httpServer, we will use local host name for http header for nightly or Chengdu run
                if [ -z "$httpServer" ]
                then
                    if [ ! -z "$ctu_host" ] || [ $nightly == 1 ]
                    then
                        httpServer=`hostname`
                    else
                        httpServer="pek-cc-pb08l"
                    fi
                fi
                
                HttpHead="http://${httpServer}"
                LTAF_LOG=${HttpHead}${restultdir}
                LTAF_LOG=${LTAF_LOG//"/net/${httpServer}"}  #chagne format http://pek-cc-pb08l/net/pek-cc-pb08l/xxx to http://pek-cc-pb08l/xxx 
            fi   #fi for if "$mongDB_link" == "yes"

            ##### handle the vxTest format Logs to record the detail testruns(pass fail abort numbers)
            if [ "$debug_flag" == 1 ]
            then
                echo -e "result dir is $restultdir"
            fi
            
            runlog=""
            runlog=`find $restultdir -name "target_*.log"  -a ! -name "target_host*.log"|tail -1`
            if [ -z "$runlog" ]
            then
                ### don't find the runlog, Skip the assign the details.
                if [ "$debug_flag" == 1 ]
                then
                    echo "no avaiable vxTest log"
                fi
                
                vxTest_details_total="1"
                
                if [ "$run_result" == "Blocked" ]
                then
                    vxTest_details_pass="0"
                    vxTest_details_fail="0"
                fi
                
                if [ "$run_result" == "PASS" ]
                then
                    vxTest_details_pass="1"
                    vxTest_details_fail="0"
                fi
                
                if [ "$run_result" == "FAIL" ]
                then
                    vxTest_details_pass="0"
                    vxTest_details_fail="1"
                fi
     
                if [ "$debug_flag" == 1 ]
                then
                    echo "pass is $vxTest_details_pass  fail is $vxTest_details_fail total is $vxTest_details_total"
                fi
            fi    
            #####
            if [ $update_only == 0 ]
            then
                if [ $nightly == 1 ] && [ "$Plan_only" == 0 ] && [ $build_result == "FAIL" ]
                then
                    # when vsb build fail for one test suite, it will mark all test cases under this suite as 
                    # FAIL, this may lead extra test results because some test cases may not be executed under 
                    # current configuration. To prevent it, we will not add new test results if nightly plan 
                    # does not have it.
                    
                    # disable this feature on 2017.08.16 requested by Guocai
                    #sed -i "s#LTAF_ACTION#update#" $destIniFile
                    sed -i "s#LTAF_ACTION#add_update#" $destIniFile
                else
                    
                    sed -i "s#LTAF_ACTION#add_update#" $destIniFile
                fi
            else
                sed -i "s#LTAF_ACTION#update#" $destIniFile
                           
            fi
            
            sed -i "s/LTAF_SPINTYPE/$spinType_value/g" $destIniFile
            sed -i "s/LTAF_SPIN_NAME/$spinName_value/g" $destIniFile
            sed -i "s/LTAF_BSP/$bspName/g" $destIniFile
            sed -i 's#LTAF_TOOL#'$toolName'#' $destIniFile
            sed -i "s/LTAF_SPRINT/${LTAF_SPRINT}/g" $destIniFile
            sed -i "s/LTAF_WEEK/${LTAF_WEEK}/g" $destIniFile
            sed -i "s/LTAF_REASES/${LTAF_REASES}/g" $destIniFile 
            if [ $nightly == 1 ] && [ "$domain" == "bsp" ]
            then
                bspToArchFound=0
                
                for bsp_tmp in ${ppcBspList[*]}; do	
                    if [ "$bspName" = "$bsp_tmp" ]; then
                        if [ "$debug_flag" == 1 ]; then
                            echo "change domain from bsp to ppc for nightly test"
                        fi
                        bspToArchFound=1
                        sed -i "s#LTAF_DOM#ppc#" $destIniFile
                        break
                    fi
                done
                
                if [ $bspToArchFound == 0 ]
                then
                    for bsp_tmp in ${iaBspList[*]}; do	
                        if [ "$bspName" = "$bsp_tmp" ]; then
                            if [ "$debug_flag" == 1 ]; then
                                echo "change domain from bsp to ia for nightly test"
                            fi
                            bspToArchFound=1
                            sed -i "s#LTAF_DOM#ia#" $destIniFile
                            break
                        fi
                    done
                fi

                for bsp_tmp in ${riscvBspList[*]}; do
                    if [ "$bspName" = "$bsp_tmp" ]; then
                        if [ "$debug_flag" == 1 ]; then
                            echo "change domain from bsp to riscv for nightly test"
                        fi
                        bspToArchFound=1
                        sed -i "s#LTAF_DOM#riscv#" $destIniFile
                        break
                    fi
                done

                if [ $bspToArchFound == 0 ]
                then
                    # to make the script run faster, we treat all left to "arm"
                    sed -i "s#LTAF_DOM#arm#" $destIniFile
                    if [ "$debug_flag" == 1 ]; then
                        echo "change domain from bsp to arm for nightly test"
                    fi
                fi
                
            else
                tr_domain=`echo ${domain/&/\\\&}`
                sed -i "s#LTAF_DOM#'""$tr_domain""'#" $destIniFile
            fi
            sed -i 's#LTAF_TEST#'$TestName'#' $destIniFile
            sed -i 's#LTAF_CTEST#'$testCfile'#' $destIniFile
            sed -i 's#LTAF_COMPONENT#'$testComponent'#' $destIniFile


            sed -i 's#LTAF_USER#'${LTAF_USER}'#'  $destIniFile
            sed -i 's#LTAF_REQ#'$LTAF_REQ'#'  $destIniFile
            sed -i 's#LTAF_CONFIG_LABEL#'$config_label'#'  $destIniFile
            sed -i 's#LTAF_TECH#'$tech'#'  $destIniFile
            #sed -i 's#LTAF_TAG#'$LTAF_TAG'#'  $destIniFile
            sed -i "s/LTAF_OPTION/${options}/g"  $destIniFile
            sed -i "s/LTAF_VSBOPTION/${vsboptions}/g"  $destIniFile
            sed -i "s/LTAF_CONFIGURATION/${helixConfigValue}/g"  $destIniFile
            sed -i "s/LTAF_BOPTIONS/${buildoptions}/g" $destIniFile
            sed -i "s/LTAF_HOSTOS/\"${host_os_name}\"/g"  $destIniFile
            sed -i 's#LTAF_TASKID#'$taskID'#'  $destIniFile
            sed -i 's#LTAF_BOARD#'$board_name'#'  $destIniFile
            if [ "$Plan_only" == 0 ]
            then
                sed -i 's#LTAF_LOG#'$LTAF_LOG'#'  $destIniFile
                sed -i 's#LTAF_BARCODE#'$barcode'#'  $destIniFile
                sed -i "s#LTAF_EXEC#$run_result#"  $destIniFile
                sed -i 's#LTAF_BUILD#'$build_result'#'  $destIniFile
                sed -i 's#LTAF_KEY#'$result_key'#' $destIniFile
                sed -i 's#LTAF_Pass#'$vxTest_details_pass'#'  $destIniFile
                sed -i 's#LTAF_Fail#'$vxTest_details_fail'#'  $destIniFile
            fi
            
            if [ "$Plan_only" == 1 ]
            then
                #### testplan only keep the key zones.
                sed -i "s/LTAF_LOG//g"  $destIniFile
                sed -i "s/LTAF_BARCODE//"  $destIniFile 
                sed -i "s/LTAF_EXEC/Not Started/g"  $destIniFile
                sed -i "s/LTAF_BUILD//g"  $destIniFile
                sed -i "s/LTAF_TAG//g"  $destIniFile
                if [ ! -z "result_key" ]
                then 
                    sed -i 's#LTAF_KEY#'$result_key'#' $destIniFile
                fi
                sed -i "s/LTAF_Pass//g"  $destIniFile
                sed -i "s/LTAF_Fail//g"  $destIniFile
            fi

            if [ "$debug_flag" == 1 ]
            then
                echo "parepare to upload to LTAF $destIniFile"
            fi

            if [ "$import_flag" == 1 ]
            then
                if [ $nightly == 0 ]
                then
                    curlCmd="curl -F resultfile=@$destIniFile  -F inheritDefectFrom=all  http://pek-lpgtest3.wrs.com/ltaf/upload_results.php"
                else
                    curlCmd="curl -F resultfile=@$destIniFile http://pek-lpgtest3.wrs.com/ltaf/upload_nightly_results.php"
                fi
                
                if [ "$debug_flag" == 1 ]
                then
                    echo "curlCmd is: $curlCmd -s -S"
                fi
                
                for ((i=1; i<5; ++i)) 
                do
                    addResult=`$curlCmd -s -S 2>&1`
                    if [ ! -z "$addResult" ]
                    then
                        if [ "$debug_flag" == 1 ]
                        then
                            echo "curl upload result is: $addResult"
                        fi
                        
                        if [ "$addResult" == "Successfully" ] || [ "$addResult" == "SKIP: action=update, TR doesn't exsit." ] || [ "$addResult" == "ERROR: No test case found:"* ]
                        then
                            break
                        fi
                        echo "#####curl upload result is: $addResult, we will retry for $i time"
                        sleep 1
                    else
                        break
                    fi 
                done
            fi
            
            #echo "---- result in test $one ini is $destIniFile"
            let testResultNum+=1
        done      #### done of for cone in $cfileTestList
        ########################################################################
        
    done     #### done of check of the each testRun.xml
    ############################################################################
    
} #end of ltaf_result


#
#usage of this script
#
usage () {
  echo -e "usage for impport WASSP log to LTAF"
  echo -e "------------------------------------"
  echo -e "sh ltaf_vxworks.sh"
  echo -e "\t -sprint   [*] sprint info in LTAF "
  echo -e "\t -week    [*] Week info in LTAF"
  echo -e "\t -ltaf    [*]release name in LTAF"
  echo -e "\t -log     [*]log loc of LOG"
  echo -e "\t -domain  [*]domain info. which show the TR_Domain in LTAF"
  echo -e "\t -prod [*] prod infor for the LOG server. Example Vx-7_IA_Arch-BSP"
  echo -e "\t -rel [*]  rel infor for the LOG server. Example Vx7_SR0450_Release"
  echo -e "\t \t     which usually come from LTAF.conf in WASSP test case repos."
  echo -e "\t \t     LTAF_comp=core, then the domain set as core"
  echo -e "\t -req $value_req [optional] assgin the requirement number in LTAF. if the WASSP testResult had the userStories set, then don't need to using this option"
  echo -e "\t -hostos $value_hostos [optional] assign the hostos type of test info in LTAF.if not assgin it. it will get from report"
  echo -e "\t -taskID $value_taskId [optional] assign the taskID to test info in LTAF."
  echo -e "\t -configuration static/dynamic [optional] assign the configuration to test info in LTAF."
  echo -e "\t -key $value_keyword [optional] assign the Key info in LTAF."
  echo -e "\t -select select one type of test result(PASS,FAIL,Blocked) parared to upload to LTAF"
  echo -e "\t -skip $value_skip [optional] will skip the states of follow test states to LTAF list should be"
  echo -e "\t \t noTargets exception timeout bootFail "
  echo -e "\t -mongDB  [NOT USE optional] using the mongDB link for LTAF log. or use the local loc."
  echo -e "\t -prod point to the LOG server producet directory"
  echo -e "\t -rel point to the LOG server relese directory"
  echo -e "\t -nTime assign a new TimeStamp folder to keep the log on LOG Server"
  echo -e "\t -nighlty for nightly test usage"
  echo -e "\t -debug more debug message will be print out"
  echo -e "\t -noltaf just generate ini files, do not import to ltaf"
  echo -e "\t -update  [optional] just update the tesult, or will update the test case first" 
  echo -e "\t -plan just import plan"
  echo -e "\t -httpServer specify http server name"
  echo -e "\t -caseGitRepo specify test case git repo for cases out of current repo"
  echo -e "------------------------------------"
  echo -e "Example:"
  echo -e ""
  echo -e "1.import Result to LTAF for usb domain and update test case first"
  echo -e ""
  echo -e "\t"
  echo -e " sh ltaf_vxworks.sh -sprint "Sprint 44 - Ending 30 October 2015"  -week Week3 -ltaf vxwors-fr -log /buildarea3/LOG/USB/20151021_093207_usb_vx20151019113827_vx7-oct2015-features_vx7-release  -domain usb -prod Vx-7_IA_Arch-BSP -rel Vx7_SR0450_Release -update -meta"
  echo -e ""
  echo -e "2.import Result to LTAF for usb domain, User should keep test case ready first"
  echo -e "\t"
  echo -e "sh ltaf_vxworks.sh -sprint "Sprint 44 - Ending 30 October 2015"  -week Week3 -ltaf vxwors-fr -log /buildarea3/LOG/USB/20151021_093207_usb_vx20151019113827_vx7-oct2015-features_vx7-release  -domain usb -update -prod Vx-7_IA_Arch-BSP -rel Vx7_SR0450_Release -update -mate"
  echo -e "3.import Result to LTAF for usb domain, User should keep test case ready first keep the log in LOG server use new timestamp"
  echo -e "\t"
  echo -e "sh ltaf_vxworks.sh -sprint "Sprint 44 - Ending 30 October 2015"  -week Week3 -ltaf vxwors-fr -log /buildarea3/LOG/USB/20151021_093207_usb_vx20151019113827_vx7-oct2015-features_vx7-release  -domain usb -update -prod Vx-7_IA_Arch-BSP -rel Vx7_SR0450_Release -nTime -meta -update"
  echo -e "4.debug purpose command"
  echo -e "\t"
  echo -e "./ltaf_vxworks.sh  -log /buildarea1/hli0/temp/coreos/ -week week2 -domain fs -sprint "abc" -rel vx7-integration-helix -prod Vx-7_Connectivity -configuration Dynamic -noLogUpload -ltaf vx7-integration-helix -noltaf -debug"

}



# Process optional parameter(s)
#
#### Beijing Logs Server
LOG_SERVER=/net/pek-cc-pb08l/vxtest/vxtest2/LOG_VX7 
####Chengdu Logs Server
ctu_host=$(echo `hostname`|grep "ctu-")
if [ ! -z "$ctu_host" ]
then
   LOG_SERVER=/net/ctu-cc-pb02l/testcloud/Log/LOG_VX7
fi
Spint=" "
Week=" "
LTAF_release=" "
logFolder=""
requirement=""
test_name=""
result_key=""
selected_result=""
mongDB_link=""
product=""
release=""
spinName_value=""
helixConfigParam=""
update_only=0
new_time=0
Plan_only=0
debug_flag=0
import_flag=1
upload_log_flag=1
testResultNum=0
ltafRetDir=""
nightly=0
while [ $# -gt 0 ]; do
    case $1 in
        -sprint) shift; Sprint=$1 ;;
        -week) shift; Week=$1 ;;
        -ltaf) shift; LTAF_release=$1 ;;
        -Logs) shift; logFolder=$1 ;;
        -req) shift; requirement=$1 ;;
        -hostos) shift; hostOS=$1 ;;
        -spin) shift; spinName_value=$1 ;;
        -taskID) shift; taskID=$1 ;;
        -configuration) shift; helixConfigParam=$1 ;;
        -tester) shift; tester=$1 ;;
        -domain) shift; domain=$1 ;;
        -key) shift; result_key=$1 ;;
        -select) shift; selected_result=$1 ;;
        -skip) shift; skip_list=$1 ;;
        -mongDB) mongDB_link="yes" ;;
        -prod) shift; product=$1 ;;
        -rel) shift;  release=$1 ;;
        -nTime)  new_time=1 ;;
        -debug)  debug_flag=1 ;;
        -noltaf)  import_flag=0 ;;
        -noLogUpload)  upload_log_flag=0 ;;
        -update) update_only=1 ;;
        -plan) Plan_only=1 ;;
        -httpServer) shift; httpServer=$1 ;;
        -caseGitRepo) shift; caseGitRepo=$1 ;;
        -ltafRetDir) shift; ltafRetDir=$1 ;;
        -nightly) nightly=1 ;;
        -iter) shift; iter=$1 ;;
        -help) usage; exit 0 ;;
        *) echo "$myName: invalid parameter '$1'" >&2; exit 1;;
    esac
    shift
done

if [ -z "$Sprint" ] || [ -z "$Week" ] || [ -z "$LTAF_release" ] || [ -z "$logFolder" ] || [ -z "$domain" ]
then
    echo "-sprint -week -ltaf -log -domain must be set"
    exit 1
#else
#    Week=$(echo $Week|sed 'y/ABCDEFGHIJKLMNOPQRSTUVWXYZ/abcdefghigklmnopqrstuvwxyz/')
fi

if [ "$Plan_only" == 1 ] || [ "$nightly" == 1 ]
then
    upload_log_flag=0
fi

if [ "$Plan_only" == 0 ] && [ "$nightly" == 0 ]
then
    if [ -z "$product" ] || [ -z "$release" ]
    then
        echo "-prod -rel must be set"
        exit 1
    else
        LOG_Root=${LOG_SERVER}/${product}/${release}
        if [ ! -d "$LOG_Root" ]
        then
            echo "Invalid option for -prod or -rel"
            echo "Valid options for -prod"
            
            for one in `find ${LOG_SERVER} -maxdepth 1 -type d -name "Vx-7*"`
            do 
              showone=$(basename $one)
              echo -e "----$showone"
            done
            
            echo "Valid options for -rel"
            for one in `find ${LOG_SERVER}/Vx-7_Core/ -maxdepth 1 -type d -name "Vx7*" -o -name "vx7*"`
            do
                showone=$(basename $one)
                echo -e "----$showone"
            done
            
            exit 1
        fi
    fi
fi   # end of if [ "$Plan_only" == 0 ] && [ "$nightly" == 0 ]

echo "Sprint  is $Sprint "
echo "Week is $Week "
echo "LTAF_release is $LTAF_release "
echo "logFolder is $logFolder"

export LTAF_SPRINT="$Sprint"
export LTAF_WEEK=$Week
export LTAF_REASES=$LTAF_release
export LTAF_COM=$domain

if [ "$LTAF_SPRINT" == "Weekly" ]
then
    LTAF_WEEK=`date -d $Week +%g%V`
    LTAF_WEEK=`echo "week$LTAF_WEEK"`
    echo "LTAF_WEEK is $LTAF_WEEK"
fi


if [ ! -z "$requirement" ]
then
    export LTAF_REQ=$requirement
else 
    export LTAF_REQ=""
fi

if [ ! -z  "$tester" ]
then
    LTAF_USER=$tester
    echo "tester is $LTAF_USER"
else
    LTAF_USER=`echo "$USER"`
    echo "tester is $LTAF_USER"
fi
 
if [ ! -z  "$skip_list" ]
then
    echo "skip_list is $skip_list"
fi

##### source confie file to import the LTAF test cases
scriptDir=$(cd $(dirname $0); cd ..; pwd)


TestProduce=vxworks7
   
TestSuite="bsp usb fs fs_dev fs_st fs/StorageCase_fsBench fs/StorageCase_fsNfs fs/StorageCase_fsStress os/vxTest_core os/core system system/PerformanceTest mw/cli mw/dsi mw/snmp mw/snmpmanager mw/soap mw/mib mw/tipc mw/web mw/xml os/vxTest_core_cert system/CertPerformanceTest multiversion networking can"


result_template=$scriptDir/LTAF_meta/result.ini
echo -e "scriptDir is $scriptDir"

if [ -z  "$caseGitRepo" ]
then
    caseGitRepo=$scriptDir
fi

echo -e "Test case Git Repo is $caseGitRepo"
echo -e "Test produce is $TestProduce"
echo -e "Test Component is $TestSuite"


#### check about the logFolder existence
if [ ! -d "$logFolder" ]
then
   echo "$logFolder does not exist"
   exit 1
fi

###
if [ "$mongDB_link" == "yes" ]
then
  echo "-mongDB is not supported in this verion, remove it from you cmdline"
  exit 1
fi

#### got the Logs to put on the LOG_Root first
#### plan_only function don't need to zip the logs.
if [ "$upload_log_flag" == 1 ]
then
    echo "==================== begin to zip the log to LOG SERVER" 
    zipdate=`date +%Y%m%d_%H%M%S`
    zipdate=`echo $zipdate`
    foldername=$(dirname $logFolder)
    filename=$(basename $logFolder)
    cd ${foldername}
    sh $scriptDir/LTAF_meta/wassp_log.sh $filename $zipdate
    mv ${logFolder}/${zipdate}_log.zip  ${LOG_Root}/
    cd ${LOG_Root}
    if [ "$new_time" == 1 ]
    then
        unzip -o ${zipdate}_log.zip  -d  ${zipdate} 
    else
        unzip -o ${zipdate}_log.zip
    fi
    rm -rf ${zipdate}_log.zip
    if [ "$new_time" == 1 ]
    then
       logFolder=${LOG_Root}/${zipdate}/$filename
    else
       logFolder=${LOG_Root}/$filename
    fi
    summrylog=$(find $logFolder -type d -name "Summary")
    if [ ! -z "$summrylog" ]
    then
       logFolder=$(dirname $summrylog)
    fi
    echo "log put to sever logFolder is $logFolder"
    sleep 60
else
    summrylog=$(find $logFolder -type d -name "Summary")
    if [ ! -z "$summrylog" ]
    then
       logFolder=$(dirname $summrylog)
    fi
fi

if [[ -z "$ltafRetDir" ]] || [[ ! -d $ltafRetDir ]]
then
    ltafRetDir=$logFolder
fi

if [ -d  $ltafRetDir/LTAF ]
then
    rm -rf $ltafRetDir/LTAF
fi
mkdir -p $ltafRetDir/LTAF/Result

####clone a new wassp test case repos
#git clone git://git.wrs.com/git/projects/wassp-repos/testcases/$TestProduce $logFolder/LTAF/$TestProduce


#####
#    for one in $TestSuite
#    do
#     eval sh $scriptDir/LTAF/ltaf_testSet.sh $logFolder/LTAF/$TestProduce  $one
#    done
#    ####
#     echo -e "have gen the Test Case set done in LTAF"
#fi
echo "we begin generate the WASSP result to LTAF ..."

# find all sub-directory
FolderList=`find $logFolder -maxdepth 1 -mindepth 1 -type d`


if [ -z "$FolderList" ]
then
   echo -e "empty folder $logFolder"
   exit 1
fi

if [ $import_flag -eq 0 ];then
    echo "********************* we just generate ini file, not import to ltaf ***********************"
fi

for test in $FolderList
do
    
    if [ "$Plan_only" == 0 ]
    then
        wassp_valid=$(find $test -mindepth 1 -name "statusTestRun.log")
        if [  -z "$wassp_valid" ]
        then
            echo " skip $test, not valid test log dir"
            continue
        fi
    fi
    echo " begin process $test"
    ltaf_result $test $(basename $test)
        
done

wait
rm -rf $logFolder/LTAF/$TestProduce

