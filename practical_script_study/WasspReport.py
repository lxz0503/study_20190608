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
from datetime import datetime, timedelta

def run_cmd(cmd):
    print 'cmd %s', cmd
    p = subprocess.Popen(cmd,bufsize=1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out, std_err = p.communicate()
    print 'std_out : %s' % std_out
    return (p.returncode, std_out)

   
def sendmail(config):

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
        #file = MIMEApplication(f.read())
        file = MIMEImage(f.read())
        f.close()
        #file.add_header('Content-Disposition', 'attachment', filename= os.path.basename(config['file']))
        file.add_header('Content-ID', '<chartImage>')
        message.attach(file)

    smtp = SMTP(config['server'])
    smtp.sendmail(config['from'], toAddressList, message.as_string())
    smtp.close()


def getResult(report_page):
    spin_info = 'testResult'
    cmd='wget -O %s.html "%s"' %(spin_info,report_page)
    print cmd

    run_cmd(cmd)

    f = open('%s.html' % spin_info, 'r')
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
        if 'Passed:' in line:
            print line
            pass_no=line.split("Passed:</b>")[1].split('</li>')[0].split('(')[0]
            pass_rate=line.split("Passed:</b>")[1].split('</li>')[0].split('(')[1].strip(')')
            print pass_no
        if 'Failed:' in line:
            fail_no=line.split("Failed:</b>")[1].split('</li>')[0].split('(')[0]
            fail_rate=line.split("Failed:</b>")[1].split('</li>')[0].split('(')[1].strip(')')
            print fail_no
        if 'Blocked:' in line:
            block_no=line.split("Blocked:</b>")[1].split('</li>')[0].split('(')[0]
            block_rate=line.split("Blocked:</b>")[1].split('</li>')[0].split('(')[1].strip(')')
            print block_no
        if 'Total:' in line:
            total_no=line.split("Total:</b>")[1].split('</li>')[0]
            print total_no
    return (pass_no, pass_rate, fail_no, fail_rate, total_no, block_no, block_rate)
            

def msg2html (fd, msg):
    fd.write(str(msg))


def getGraphTrend (tags, project):
    trendFile = os.path.dirname(os.path.realpath(__file__)) + '/' + 'Trend.png'
    endDate = datetime.now()
    startDate = endDate + timedelta(days = -6)
    endDate = str(endDate).split(' ')[0]
    startDate = str(startDate).split(' ')[0]

    page = 'pek-lpgtest3.wrs.com/smartTool/genTrendChart/genTrendChart.php?project=%s&tags=%s&startdate=%s&enddate=%s' % (project, tags, startDate, endDate)
    cmd = 'wget -O %s "%s"' % (trendFile, page)
    run_cmd(cmd)
    
    #graph_page = 'http://report.wrs.com/reportgenerator/trendData/2d8fad74-84c0-11e4-a2ea-90b11c4fbb02/?main-TOTAL_FORMS=3&main-INITIAL_FORMS=3&main-MAX_NUM_FORMS=20&main-0-filter=test+date&main-0-dateStart=%s&main-0-dateEnd=%s&main-1-filter=project&main-1-options=%s&main-2-filter=tags&main-2-options=Nightly&mainform-submit=Search' % (startDate, endDate, proj_info)
    return (page)
    

def summary (fd, productName, tags, project, matrix_page,
             total_no, pass_no, pass_rate, fail_no, block_no,
             gitDir, wasspHome, 
             configure, htmlLink, projectPath
             ):
    buildFail = 0
    execFail = 0
    timeout = 0
    bootFail = 0
    noTarget = 0
    exception = 0
    
    graph_page = getGraphTrend (tags, project) 
       
    # Title
    msg2html(fd, '<basefont face="arial" size="4">')
    msg2html(fd, '<head><style>body {background-image:url("http://yow-ssp1-lx.wrs.com/buildarea1/wassp-repos/wassp/host/tools/report/templates/wassp2.png");background-repeat:no-repeat;background-position:right top;}')
    msg2html(fd, 'table, td, th{border:1px solid black;}th{background-color:powderblue;color:blue;}</style></head>')
    msg2html(fd, '<font face="arial" size="6"> %s Nightly Test On Branch: %s </font><br><br>' % (productName, project))

    # Test Summary
    msg2html(fd, '<b><font face="arial">1. Test Summary</b>')
    msg2html(fd, '<b><br></b>')
    msg2html(fd, '<table style="font-family:Arial"><thead><tr><th width="100">Total</th><th width="100">Pass</th><th width="100">Passrate</th></tr></thead>')
    msg2html(fd, '''<tbody><tr><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr></tbody></table>''' % (total_no, pass_no, pass_rate))
    msg2html(fd, "</tbody></table><br>" )
    msg2html(fd, '<table style="font-family:Arial"><thead><tr><th width="100">BuildFail</th><th width="100">ExecFail</th><th width="100">Fail</th><th width="100">Timeout</th><th width="100">BootFail</th><th width="100">NoTarget</th><th width="100">WASSP Exception</th><th width="100">Blocked</th></tr></thead>')
    msg2html(fd, '<tbody><tr><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td><td align="center"> %s</td><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr></tbody></table><br>' % (buildFail, execFail, fail_no, timeout, bootFail, noTarget, exception, block_no))
    msg2html(fd, '<table style="font-family:Arial"><tr><th width="100">MangoDB Link</th><td><a href=%s> %s </a> </td></tr></tbody>' % (graph_page, graph_page))
    msg2html(fd, "</tbody></table><br>" )

    # get 7 days graph trend
    msg2html(fd, '<a href=%s><img src=cid:chartImage width=800 height=400/><br>' % graph_page)
    msg2html(fd, '<b><br></b>')

    # Test Environment
    msg2html(fd, '<b><font face="arial">2. Test Details:</b>')
    msg2html(fd, '<b><br></b>')
    msg2html(fd, '<li><b>Testing Environment:</b>')
    msg2html(fd, '<table style="font-family:Arial"><tbody>')
    msg2html(fd, '<tr><th width="100">Test Server</th><td>128.224.159.246</td></tr>')
    msg2html(fd, '<tr><th width="100">WIND_HOME</th><td><a>%s</a></td></tr>' % gitDir)
    msg2html(fd, '<tr><th width="100">Test Matrix</th><td><a href="%s">%s</a></td></tr>' % (matrix_page, matrix_page))
    msg2html(fd, '<tr><th width="100">WASSP HOME</th><td><a>%s</a></td></tr>' % wasspHome)
    msg2html(fd, '<tr><th width="100">WASSP VERSION</th><td><a>2.0.28</a></td></tr>')
    msg2html(fd, '</tbody></table><br>')

    # Test Reports
    mongoDBLink = graph_page
    msg2html(fd, '<li><b>Testing Reports:</b>')
    msg2html(fd, '<table style="font-family:Arial"><thead><tr><th width="100">Configure</th><th width="200">MongoDB Links</th><th width="200">HTML Links</th><th width="200">Project Path</th></tr></thead>')
    msg2html(fd, '<tbody><tr><td align="left">%s</td><td align="left"><a href=%s> %s </a></td><td align="left"><a href=%s> %s </a></td><td align="left">%s</td></tr></tbody><br>' % (configure, mongoDBLink, mongoDBLink, htmlLink, htmlLink, projectPath))
    msg2html(fd, "</tbody></table><br>" )

    
def ReportWasspNightly(toEmail, project):
    today = time.strftime("%Y-%m-%d", time.localtime())
    tags = 'VX7_KONG_NIGHTLY'
    report_page='http://report.wrs.com/reportgenerator/rawresults/165cfbb8-215d-11e5-8a02-90b11c4fbb02/?main-TOTAL_FORMS=2&main-INITIAL_FORMS=2&table-1-sort=testName&main-MAX_NUM_FORMS=20&mainform-submit=Search&lastRunFilter=on&main-1-filter=test+date&main-0-filter=tags&main-1-dateStart=%s&main-1-dateEnd=%s&main-0-options=%s' % (today, today, tags)
    (pass_no, pass_rate, fail_no, fail_rate, total_no, block_no, block_rate) = getResult (report_page)
    print (pass_no, pass_rate, fail_no, fail_rate, total_no, block_no, block_rate)
    
    productName = 'VxWorks 7 Net'
    matrix_page = 'N/A'
    gitDir = '/testcloud/svc-cmnet/vxworks'
    wasspHome = '/testcloud/lchen3/wassp/wassp-repos'
    configure = 'vxsim_linux 32bit'
    htmlLink = 'http://128.224.159.246:8080/job/ci-manager/276'
    projectPath = '/testcloud/svc-cmnet/vxworks'
    
    run_cmd('rm -f email.html')
    htmlFd = open ('email.html', 'a')
    summary (htmlFd, productName, tags, project, matrix_page,
             total_no, pass_no, pass_rate, fail_no, block_no,
             gitDir, wasspHome,
             configure, htmlLink, projectPath)
    htmlFd.close()


    cmd = "cat email.html"
    (code, mail_body) = run_cmd(cmd)

    mail_title = 'VxWorks 7 Net Nightly Testing Report (%s)' % today
    print mail_title
    print mail_body

    mail_config = {'from': 'libo.chen@windriver.com',
                   'to': toEmail,
                   'subject': mail_title,
                   'body': str(mail_body),
                   'file': '%s/Trend.png' % os.path.dirname(os.path.realpath(__file__)),
                   'server': 'smtp-na.wrs.com'}
    sendmail(mail_config)

