import re
import os
import sys
import subprocess
import time

from datetime import date
from datetime import timedelta

from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def runShCmd(cmd):
    #print 'cmd %s', cmd
    p = subprocess.Popen(cmd,bufsize=1,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out, std_err = p.communicate()
    #print 'std_out : %s' % std_out
    return (p.returncode, std_out)


def findFileByName(rootDir, fileNames):
    foundFiles = []
    for parentDir, subDirs, files in os.walk(rootDir, topdown=True, followlinks=False):
        for f in files:
            root, ext = os.path.splitext(f)
            baseName = os.path.basename(parentDir + '/' + f)
            if baseName in fileNames:
                foundFiles.append(parentDir + '/' + f)
    return foundFiles


def extractItem(content, rePattern):
    found = re.search(rePattern, content)
    if found is not None:
        return found.groups()[0]
    else:
        raise BaseException('not found %s' % rePattern)


def printAndExit(errMsg, errNo=1):
    print 'ERROR: %s' % errMsg
    sys.exit(errNo)
    

def printLog(msg):
    print '=== %s' % msg
    

def TodayStr():
    return date.today().strftime('%Y-%m-%d')

   
def AfterTodayStr(numToToday):
    assert type(numToToday) == int
    return (date.today() + timedelta(days=numToToday)).strftime('%Y-%m-%d')


def sendMail(config):
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


def ElapsedTime(func):
    def _ElapsedTime(*args, **kw):
        startTime = time.time()
        ret = func(*args, **kw)
        print '=== elapsed: %s() spending %.1f seconds ===' % (func.func_name, time.time() - startTime)
        return ret
    return _ElapsedTime


def waitFuncReady(func, args, expectResult, timeout=60, interval=5):
    start_time = time.time()
    
    while True:
        if (time.time() - start_time) >= timeout:
            print('\ntimeout after %s seconds' % timeout)
            break
        
        s = func(**args)
        if s == expectResult:
            print('\nusing %s seconds' % (time.time() - start_time))
            break
        else:
            print '.',
            time.sleep(interval)


def foundFile(directory, fileName):
    filePath = os.path.join(directory, fileName)
    if os.path.exists(filePath):
        return 'found'
    else:
        return 'not-found'
    

def test_waitFuncReady():
    func = foundFile
    args = {'directory' : '/folk/lchen3/try/workspace/PdvTool/vx7tool/new',
            'fileName' : 'hello.txt',
           }
    result = 'found'
    waitFuncReady(func, args, result, timeout=10, interval=2)
    