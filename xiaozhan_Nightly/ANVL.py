#!/usr/bin/env python
#remove mail notify (not mail tinderbox)
#future: remove unionfs, beware of proper cleanup and "cvs-builds" (ie components/ip_net-6.6)
#todo: lock per union compile, not just board.
import MimeWriter, StringIO, base64, uu, gzip, tarfile, smtplib #mail related
import getopt
from glob import glob
import os
import re
import sys
import time
import pdb
import traceback
import socket
from ANVL_conf import *

class ClashException(Exception):
    pass
class DotException(Exception):
    pass
class WrongCaseNameException(Exception):
    pass
class NoneAddOrDeleteException(Exception):
    pass
class NonePackageNameException(Exception):
    pass

def HelpGuide():
    print """\nUsage:    ./ANVL.py [option...]\n\nMandatory Options:\n\n -t  [target(s)]    input DUT type: e.g: pcPentium4 / itl_64_1_0_0_3 / SIMICS \n\n -c  [case(s)]      input case(s) to test, valid format is as below:\n\n               individual number    e.g. 2.3\n               group number     e.g. 2\n               range of numbers     e.g. 1.1-1.5 or 1-3\n               wildcard use     e.g. 1-* or 2.3-2.*\n               multiple numbers     e.g  1.1, 2.3, 6.3\n               'all'        to execute all cases\n\n -s  [suite(s)]     input below suite(s) to test, using ',' to separate if inputting more suites\n                    use keyword 'all' to run all suites.\n\n 
                 ICMPv4,ICMPv6,IPv4,IPv6FlowLevelEnable,IPv6FlowLevelDisable,\n
                 IPGW,IGMPv2,IGMPv3,Mldv1,Mldv2,DHCPC,DHCPS,\n
                 RipPoison,RipCompatibility,RipSplitHorizon,\n
                 TcpCore_UrgPtrRFC1122,TcpCore_UrgPtrRFC793,TcpAdv,TcpPerf,\n
                 IPsecAHv4,IPsecAHv6,IPsecESPv4,IPsecESPv4-noencry,IPsecESPv6,IPsecESPv6-des,\n
                 IKEMain,IKEAggressive,IKECombinedSA,IKEDH1md5,IKEDH1sha,IKEv2,\n
                 IKEIPv6Main,IKEIPv6CombinedSA,IKEIPv6Aggressive,IKEIPv6md5\n\nOptional options:\n\n -l  [log_dir]      input directory to save test logs. e.g:\n\n               '/home/windriver'\n               './'\n                default is current directory\n\n --exclude  remove suite(s) from those suite(s) that indicated by "--suite" option to be executed.\n\n -d  [dvd_info]     input dvd info. to the log folder. e.g:\n\n               '6931Apr11'\n               '6923Feb15'\n                default is null\n\n -v  [version]      input dvd version to test,e.g:\n\n               '6.7'\n                default is 6.9\n\nExamples:\n\n             ./ANVL.py -t pcPentium4 -c all -s all\n             ./ANVL.py -t Q35 -c 1.1 -l ./ -d 6931Apr11 -v 7.0 -s ICMPv4\n\n"""
     
def checkLogFileFolder(logFolder):
    if os.path.isdir(logFolder):
        return True
    else:
        os.system("mkdir -p %s"%logFolder)
   


def run_anvl_for_one_suite(suite, cfgDir, logDir, case, version):
    cmd = "sudo /opt/Ixia/IxANVL880/ANVL-SRC/Bin/ix86-Linux/anvl -l low -f %s %s %s | tee %s 2>&1" %(cfgDir, suite, case, logDir)        
    print "cmd=%s\n"%cmd
    start_dir = os.getcwd()
    os.chdir("/opt/Ixia/IxANVL880/ANVL-SRC/")
    os.popen(cmd)
    os.chdir(start_dir)
      
def parse_option(argv):
    para = {
      'target'          : '',     # Default target_type is PENTIUM4
      'case'            : '',     # Default cases is ALL
      'version'         : '6.9',  # Default version is 6.9
      'log'             : '',     # Default is cwd
      'dvd'             : '', 
      'exclude'         : [],   
      'suite'           : '',      
      }
    shorts = 'fht:c:v:l:d:s:'
    longs = [
      'target=',
      'case=',
      'version',
      'suite',
      'exclude=',
      'log',
      'help',
      'dvd',]
    try:
        opts, args = getopt.gnu_getopt(argv, shorts, longs)
    except getopt.GetoptError, desc:
        print 'Error! %s!\n'%desc
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            HelpGuide()
            sys.exit(1)
        if opt in ('-t', '--target'):
            if arg == 'pcPentium4' or arg == 'Q35' or arg == 'SMPQ35' or arg == "fsl_p2020_rdb" or arg == 'bsp6x_fsl_p2020_rdb_6_9_0_0' or arg == 'bsp6x_itl_x86_2_1_2_1':
                para['target'] = arg  
                continue
            else:
                print"Error! You input invalid target '%s' type with '-t'. The valid is pcPentium4 / Q35 / fsl_p2020_rdb / bsp6x_fsl_p2020_rdb_6_9_0_0"%arg 
                sys.exit(1)
        if opt in ('-c', '--case'):
            para['case'] = arg  
            continue
        if opt in ('-v', '--version'):
            tmpArg = arg.split('.')[0]
            if tmpArg not in ('6', '7','platform','helix'):
                print 'ERROR! You input invalid --version %s\n'%arg
                sys.exit(1)   
                
            if tmpArg == '6':
                assert len(arg.split('.')) > 1
                tmpArg = arg.split('.')[0]+'.'+arg.split('.')[1]
            para['version'] = tmpArg
            continue
        if opt in ('-d', '--dvd'):
            para['dvd'] = arg 
            continue 
        if opt in ('-s', '--suite'):
            para['suite'] = arg
            continue  
        if opt in ('--exclude',):
            para['exclude'] = arg.split(',')  
            continue
        if opt in ('-l', '--log'):
            para['log'] = os.path.abspath(arg)
            if not para['log']:
                print"Error! You input '-l' with invalid dir: '%s'\n"%arg
                sys.exit(1) 
            continue 

    if not para['target']:
        print"Error! You don't input '-t' to indicate target(s) to test. The valid is pcPentium4 / itl_64_1_0_0_3 / fsl_p2020_rdb / bsp6x_fsl_p2020_rdb_6_9_0_0 ." 
        sys.exit(1)
    if not para['case']:
        print"Error! You don't input '-c' to indicate case(s) to run. Input \"./ANVL.py\" for help ." 
        sys.exit(1)
    if not para['suite']:
        print"Error! You don't input '-s' to indicate suite(s) to run. Input \"./ANVL.py\" for help ." 
        sys.exit(1)
    return para, args     

               
if __name__ == '__main__':
    if len(sys.argv) == 1:
        HelpGuide()
        sys.exit(1)
    try:
        opt, tmp = parse_option(sys.argv[1:])
        print "opt=%s"%opt
        AllSuiteList = ANVL_targets[opt['target']].keys()
        suitesList = []    
        if opt['suite'] == 'all':
            suitesList = AllSuiteList
        else:
            suitesList = opt['suite'].split(',')
            tmpList = suitesList
            for suite in suitesList:
                if suite not in AllSuiteList:
                    tmpList.remove(suite) #In case certain ANVL suite is removed for certain bsp.
            suitesList = tmpList 
                       
        if opt['exclude'] != []:
            tmpList = suitesList
            for suite in opt['exclude']:
                if suite in suitesList:
                    tmpList.remove(suite)
                else:
                    print '\nError! You input invalid suite "%s" to be excluded with "--exclude".\n    Current valid suite(s) is [%s]\n'%(suite, suitesList)
                    sys.exit(1) 
            suitesList = tmpList
                
        curTime = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime())
        if opt['log']:
            logFolder = opt['log']
        else:
            if opt['dvd']:
                logFolder = os.getcwd() + "/ANVL_"+ opt['target'] + "_" + opt['dvd'] + "_" + curTime
            else:
                logFolder = os.getcwd() + "/ANVL_"+ opt['target'] + "_" + curTime
        print "logFolder=%s\n"%logFolder
        if not checkLogFileFolder(logFolder): 
            print "Error! Fail to create log folder:%s"%logFolder
            sys.exit(1)
        for suite in suitesList:
            logFilePath = logFolder + "/" + ANVL_targets[opt['target']][suite]['logfile']
            if opt['case'] == 'all':
			    # Skip test 6.1 of suite ICMPv4 in vx69 because defect VXW-85670
                #if opt['version'] == '6.9' and suite == 'ICMPv4':
                    #run_anvl_for_one_suite(ANVL_targets[opt['target']][suite]['engine'], ANVL_targets[opt['target']][suite]['cfg_prm_path'], logFilePath, '1-5, 7-10', opt['version'])
                if opt['version'] == '6.7' and suite == 'IPsecESPv6':
                    run_anvl_for_one_suite(ANVL_targets[opt['target']][suite]['engine'], ANVL_targets[opt['target']][suite]['cfg_prm_path'], logFilePath, '1-6.2 6.5-11 12.2-13 14.3 15-16.5 17-25', opt['version']) 
                if opt['version'] == '6.7' and suite == 'IPsecAHv6':
                    run_anvl_for_one_suite(ANVL_targets[opt['target']][suite]['engine'], ANVL_targets[opt['target']][suite]['cfg_prm_path'], logFilePath, '1-5.3 5.7-11 12.2 14.2-18', opt['version']) 
                else: 
                    run_anvl_for_one_suite(ANVL_targets[opt['target']][suite]['engine'], ANVL_targets[opt['target']][suite]['cfg_prm_path'], logFilePath, ANVL_targets[opt['target']][suite]['allcase'], opt['version'])
            else:
                run_anvl_for_one_suite(ANVL_targets[opt['target']][suite]['engine'], ANVL_targets[opt['target']][suite]['cfg_prm_path'], logFilePath, opt['case'], opt['version'])

    except ClashException, desc:
        print'%s exception raised:\n %s' % (desc.__class__.__name__, desc)
        sys.exit(1)

    except DotException, desc:
        print'%s exception raised:\n %s' % (desc.__class__.__name__, desc)
        sys.exit(1)

    except WrongCaseNameException, desc:
        print'%s exception raised:\n %s' % (desc.__class__.__name__, desc)
        print'\nplease use the correct case name~\nand make sure your case name is at sanity_conf at first!'
        sys.exit(1)

    except NoneAddOrDeleteException, desc:
        print'%s exception raised:\n %s' % (desc.__class__.__name__, desc)
        sys.exit(1)

    except NonePackageNameException, desc:
        print'%s' % desc
        sys.exit(1)
