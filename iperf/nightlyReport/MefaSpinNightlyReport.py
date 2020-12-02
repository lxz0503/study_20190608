#!/usr/bin/env python

import sys
import os, socket
import subprocess
import re
import time
from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from optparse import OptionParser
from datetime import datetime, timedelta, date
import argparse

def run_shell_cmd(cmd):
    print 'cmd %s', cmd
    p = subprocess.Popen(cmd,bufsize=1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out, std_err = p.communicate()
    print 'std_out : %s' % std_out
    return (p.returncode, std_out)

   
def send_mail(config):

    message = MIMEMultipart('related')
    message['from'] = config['from']
    message['to'] = config['to']
    message['Subject'] = config['subject']
    message['Date'] = time.ctime(time.time())
    toAddressList = config['to'].split(';')


    #body = MIMEText(config['body'], 'html', 'utf-8')
    body = MIMEText(config['body'], 'html')
    message.attach(body)

    if config.has_key('file') and config.get('file') and os.path.exists(config['file']):
        f=open(config['file'], 'rb')
        print config['file']
        #file = MIMEApplication(f.read())
        file = MIMEImage(f.read())
        f.close()
        #file.add_header('Content-Disposition', 'attachment', filename= os.path.basename(config['file']))
        file.add_header('Content-ID', '<chartImage>')
        message.attach(file)

    smtp = SMTP(config['server'])
    smtp.sendmail(config['from'], toAddressList, message.as_string())
    smtp.close()


def get_test_result_from_html(testresult_html_link, saved_testresult_html_name):
    cmd='wget -O %s "%s"' % (saved_testresult_html_name, testresult_html_link)
    run_shell_cmd(cmd)
    f = open('%s' % saved_testresult_html_name, 'r')
    content = f.readlines()
    f.close()

    pass_no=0
    fail_no=0
    total_no=0
    block_no=0
    pass_rate=0
    fail_rate=0
    total_rate=0
    block_rate=0

    for line in content:
        if 'Pass = ' in line:
            pass_no = line.split("Pass = ")[1].split(' ')[0]
        if 'Fail = ' in line:
            fail_no = line.split("Fail = ")[1].split(' ')[0]
        if 'Blocked = ' in line:
            block_no = line.split("Blocked = ")[1].split(' ')[0]
        if 'Total = ' in line:
            total_no = line.split("Total = ")[1].split(' ')[0]

    if total_no != 0:
        pass_percentage = float(pass_no) / float(total_no) * 100
        pass_rate = "%.2f%%" % pass_percentage
    return (pass_no, pass_rate, fail_no, fail_rate, total_no, block_no, block_rate)
            

def get_ltaf_trendgraph(ltaf_release_name, ltaf_component):
    trend_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + 'ltafTrend.png'

    mefa_spin_date = os.getenv('MEFA_SPIN_DATE', default=datetime.today().strftime("%Y-%m-%d"))
    year, month, day =  mefa_spin_date.split('-')
    local_time = date(int(year), int(month), int(day))
    report_end_time = local_time + timedelta(days = 0)
    report_start_time = local_time + timedelta(days = -13)
    report_end_date = report_end_time.strftime("%Y-%m-%d")
    report_start_date = report_start_time.strftime("%Y-%m-%d")

    ltaf_trend_html_link = 'http://pek-lpgtest3.wrs.com/ltaf/nightly_interface.php?release_name=%s&f_type=chart&start_date=%s&end_date=%s&component=%s&tags=IPERF' % (ltaf_release_name, report_start_date, report_end_date, ltaf_component)
    cmd = 'wget -O %s "%s"' % (trend_filename, ltaf_trend_html_link)
    run_shell_cmd(cmd)
    
    return (ltaf_trend_html_link)


def getDefectList (html_filename, jira_id):
    exePath = os.path.dirname(os.path.realpath(__file__))
    exeCmd = exePath + '/' + 'listDefects.sh'
    defectListFile = exePath + '/' + html_filename
    cmd = exeCmd + ' ' + defectListFile + ' ' + jira_id 
    run_shell_cmd(cmd)
    

def msg2html (fd, msg):
    fd.write(str(msg))
    fd.write("\n")


def summary (fd, productName, spin_name, ltaf_release_name, ltaf_component, matrix_page,
             total_no, pass_no, pass_rate, fail_no, block_no,
             gitDir, wasspHome, 
             configure, htmlLink, projectPath, ltaf_link, total_time, run_date
             ):
    buildFail = 0
    execFail = 0
    timeout = 0
    bootFail = 0
    noTarget = 0
    exception = 0
    
    graph_page = get_ltaf_trendgraph(ltaf_release_name, ltaf_component) 
    # Replace the space in "VxWorks 7.0" with %20
    graph_page = graph_page.replace(' ', '%20')
       
    # Title
    msg2html(fd, '<basefont face="arial" size="4">')
    msg2html(fd, '<head><style>body {background-repeat:no-repeat;background-position:right top;}')
    msg2html(fd, 'table, td, th{border:1px solid black;}th{background-color:powderblue;color:blue;}</style></head>')

    # Show the product name and spin name in the e-mail html
    msg2html(fd, '<font face="arial" size="6"> %s Nightly Test On Spin: %s </font><br><br>' % (productName, spin_name.split('/')[-1]))

    # Testing Summary
    # msg2html(fd, '<b><font face="arial">1. Testing Summary</b>')
    msg2html(fd, '<b><font face="arial">Testing Summary</b>')
    msg2html(fd, '<br>')
    msg2html(fd, '<b><br></b>')
    msg2html(fd, '<table style="font-family:Arial"><thead><tr><th width="100">Total</th><th width="100">Pass</th><th width="100">Passrate</th></tr></thead>')
    msg2html(fd, '''<tbody><tr><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr></tbody></table>''' % (total_no, pass_no, pass_rate))
    msg2html(fd, "</tbody></table><br>" )
    msg2html(fd, '<table style="font-family:Arial"><thead><tr><th width="100">BuildFail</th><th width="100">ExecFail</th><th width="100">Fail</th><th width="100">Timeout</th><th width="100">BootFail</th><th width="100">NoTarget</th><th width="100">WASSP Exception</th><th width="100">Blocked</th></tr></thead>')
    msg2html(fd, '<tbody><tr><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td><td align="center"> %s</td><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr></tbody></table><br>' % (buildFail, execFail, fail_no, timeout, bootFail, noTarget, exception, block_no))

    # Get graph trend
    msg2html(fd, '<a href=%s><img src=cid:chartImage width=800 height=400/></a>' % graph_page)
    msg2html(fd, '<br><br>')
    msg2html(fd, '<b><br></b>')

    # MongoDB link
    msg2html(fd, '<table style="font-family:Arial"><tr><th width="100">LTAF Link</th><td><a href=%s> %s </a></td></tr>' % (ltaf_link, ltaf_link))
    msg2html(fd, '<tr><th width="100">Test Results</th><td><a href=%s> %s </a></td></tr></table>' % ('http://pek-vx-nwk1/report/{date}'.format(date = run_date), 'http://pek-vx-nwk1/report/{date}'.format(date = run_date)))
    msg2html(fd, '<br><br>')
    msg2html(fd, '<b><br></b>')

    # Defect list
    #if int(fail_no) != 0:  
    if 0:
        getDefectList('defectlist.html', '21806')
        cmd = "cat defectlist.html"
        (rtn_code, defect_list) = run_shell_cmd(cmd)
        msg2html(fd, '<b><font face="arial">Open Defects:</b>')
        msg2html(fd, '<table style="font-family:Arial"><tbody>')
        msg2html(fd, '<tr><td></td> %s </tr>' % str(defect_list))
        msg2html(fd, '</tbody></table><br>')

    # Last commit 
    cmd = 'cd %s && git log -1 HEAD | grep "commit" | head -n 1' % gitDir
    rtncode, lastCommit = run_shell_cmd(cmd)
    #print (type(lastCommit))

    # Testing Details
#    msg2html(fd, '<b><font face="arial">2. Testing Details:</b>')
#    msg2html(fd, '<br>')
#    msg2html(fd, '<b><br></b>')
#    msg2html(fd, '<table style="font-family:Arial"><tbody>')
#    msg2html(fd, '<tr><th width="100">GIT HEAD</th><td><a>%s</a></td></tr>' % lastCommit)
#    msg2html(fd, '<tr><th width="100">Test Server</th><td>pek-vx-nightly1.wrs.com</td></tr>')
#    msg2html(fd, '<tr><th width="100">WIND_HOME</th><td><a>%s</a></td></tr>' % gitDir)
#    msg2html(fd, '<tr><th width="100">Test Matrix</th><td><a href="%s">%s</a></td></tr>' % (matrix_page, matrix_page))
#    msg2html(fd, '<tr><th width="100">Total Time</th><td><a>%s</a></td></tr>' % total_time)
#    msg2html(fd, '<tr><th width="100">WASSP HOME</th><td><a>%s</a></td></tr>' % wasspHome)
#    msg2html(fd, '<tr><th width="100">WASSP VERSION</th><td><a>2.0.32</a></td></tr>')
#    msg2html(fd, '<tr><th width="100">HTML Log</th><td><a>%s</a></td></tr>' % htmlLink)
#    msg2html(fd, '</tbody></table><br>')

    
def send_nighlty_test_report_email_ltaf(email_to_list, spin_name, ltaf_release_name, ltaf_component, total_time, run_date):
    mefa_spin_date = os.getenv('MEFA_SPIN_DATE', default=datetime.today().strftime("%Y-%m-%d"))
    year, month, day =  mefa_spin_date.split('-')
    local_time = date(int(year), int(month), int(day))
    report_end_time = local_time + timedelta(days = 0)
    report_start_time = local_time + timedelta(days = -13)
    report_end_date = report_end_time.strftime("%Y-%m-%d")
    report_start_date = report_start_time.strftime("%Y-%m-%d")

    testresult_html_link = 'http://pek-lpgtest3.wrs.com/ltaf/nightly_interface.php?release_name=%s&f_type=info&date=%s&component=%s&tags=IPERF' % (ltaf_release_name, run_date, ltaf_component)
    saved_testresult_html_name = 'ltaf_nighlty_result.html'
    (pass_no, pass_rate, fail_no, fail_rate, total_no, block_no, block_rate) = get_test_result_from_html(testresult_html_link, saved_testresult_html_name)
    print (pass_no, pass_rate, fail_no, fail_rate, total_no, block_no, block_rate)
    
    exePath = os.path.dirname(os.path.realpath(__file__))
    productName = 'VxWorks 7 Networking'
    matrix_page = 'http://pek-vx-nightly1.wrs.com' + exePath + '/' + 'networking.xls'
    gitDir = exePath + '/' + 'vxworks'
    wasspHome = exePath + '/' + 'wassp-repos'
    configure = 'MEFA'
    htmlLink = 'http://pek-vx-nightly1.wrs.com' + exePath + '/' + 'wassp-repos/NightlyLogs/Summary/summary.html'
    htmlLink = ' '
    projectPath = exePath + '/' + 'vxworks'

    ltaf_link='http://pek-lpgtest3.wrs.com/ltaf/nightly_results.php?releasename=%s&clearfilter=true&tf_tr_whentostart=%s&tf_test_component=%s&tf_tr_tags=IPERF' % (ltaf_release_name, run_date, ltaf_component)
    
    run_shell_cmd('rm -f ltaf_email.html')
    htmlFd = open ('ltaf_email.html', 'a')
    summary (htmlFd, productName, spin_name, ltaf_release_name, ltaf_component, matrix_page,
             total_no, pass_no, pass_rate, fail_no, block_no,
             gitDir, wasspHome,
             configure, htmlLink, projectPath, ltaf_link, total_time, run_date)
    htmlFd.close()
    cmd = "cat ltaf_email.html"
    (rtn_code, mail_body) = run_shell_cmd(cmd)
    mail_title = 'VxWorks 7 Networking Nightly Testing Report (%s) - IPERF' % run_date
    mail_content = {'from': 'VxWorks7 Nightly NEVER_REPLY <target@windriver.com>',
                   'to': email_to_list,
                   'subject': mail_title,
                   'body': str(mail_body),
                   'file': '%s/ltafTrend.png' % os.path.dirname(os.path.realpath(__file__)),
                   'server': 'smtp-na.wrs.com'}
    send_mail(mail_content)


def get_fail_case_list(ltaf_release_name, ltaf_component):
    exePath = os.path.dirname(os.path.realpath(__file__))
    failcaselist_filename = exePath + '/' + 'failcaselist.wassp'
    # remove existing fail case list file
    cmd = 'rm -f ' + failcaselist_filename
    run_shell_cmd(cmd)

    # generate the fail case list file
    mefa_spin_date = os.getenv('MEFA_SPIN_DATE', default=datetime.today().strftime("%Y-%m-%d"))
    year, month, day =  mefa_spin_date.split('-')
    local_time = date(int(year), int(month), int(day))
    report_time = local_time + timedelta(days = 0)
    report_date = report_time.strftime("%Y-%m-%d")

    cmd = "curl -F show_type=nightly -F release_name='%s' -F filter_rundate=%s -F filter_tr_domain=%s -F filter_status=Fail -F show_fields=test_name http://pek-lpgtest3.wrs.com/ltaf/show_result_fields.php > " % (ltaf_release_name, report_date, ltaf_component) + failcaselist_filename
    run_shell_cmd(cmd)

    failcase_num = 0
    failcaselistFd = open(failcaselist_filename, 'r')
    html_content = failcaselistFd.readlines()
    for line in html_content:
            failcase_num = failcase_num + 1
    failcaselistFd.close()
    print 'Fail case number: %s' % failcase_num

    if failcase_num == 0:
        cmd = 'rm -f ' + failcaselist_filename
        run_shell_cmd(cmd)

def time_delta(run_date):
    y = datetime.strptime(run_date, '%Y-%m-%d')
    z = datetime.now()
    diff = z - y
    return diff.days - 1

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate the nightly fail case list or sending nightly report email.')
    parser.add_argument('-r', '--report', metavar='yes', dest='report_email_on', nargs='+', help='report_email_on', default=None)
    parser.add_argument('-b', '--spin', metavar='yes', dest='spin_name', nargs='+', help='spin_name', default=None)
    parser.add_argument('-l', '--ltaf', metavar='yes', dest='ltaf_release_name', nargs='+', help='ltaf_release_name', default=None)
    parser.add_argument('-t', '--totaltime', metavar='yes', dest='total_time', nargs='+', help='total_time', default=None)
    parser.add_argument('-d', '--run_date', metavar='yes', dest='run_date', nargs='+', help='run_date', default=None)
    args = parser.parse_args()

    email_to_list = 'yanyan.liu@windriver.com; xiaozhan.li@windriver.com; haixiao.yan@windriver.com; li.wan@windriver.com; xiuli.sun@windriver.com; peng.bi@windriver.com; chunyan.ye@windriver.com; ENG-VxNET-China@windriver.com'
    #email_to_list = 'haixiao.yan@windriver.com'
    ltaf_component = 'networking'

    spin_name = args.spin_name[0]
    ltaf_release_name = args.ltaf_release_name[0]
    total_time = args.total_time[0]
    run_date = args.run_date[0]

    if args.report_email_on[0] == 'yes' and time_delta(run_date) <= 0:
        send_nighlty_test_report_email_ltaf(email_to_list, spin_name, ltaf_release_name, ltaf_component, total_time, run_date)
    #else:
    #   get_fail_case_list(ltaf_release_name, ltaf_component)
