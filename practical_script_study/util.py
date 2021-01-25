#############################################################################
#
# Copyright (c) 2006-2020 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#
#modification history
#--------------------
#24sep20,clb add Qemu IA target support

import os
import logging
import subprocess
import sys
import time
import yaml

debugFlag = False # boolean to turn on/off debug log
shcmdIndicator = '===='

def shCmd(cmd, sudo=False):
    if sudo:
        cmd = 'sudo ' + cmd
    lines = os.popen(cmd).readlines()
    if debugFlag:
        print('\n%s %s' % (shcmdIndicator, cmd))
        print('\n'.join(lines))
    return lines


def sudo(cmd):
    return shCmd(cmd, sudo=True)


def sudovoid(cmd):
    shCmd(cmd, sudo=True)
        
    
def runCmd(x, cmd_prefix=''):
    print(">>>>>> " + cmd_prefix + x)
    lines = shCmd(cmd_prefix + x + " 2>&1")
    for line in lines: 
        print(line)
    return lines


log = logging.getLogger(__name__)


def run_cmd(cmd, background=False, pollDelay=4, captureOutput=True, echo=True,
            echoEmpty=True, **kwargs):
    '''
    Runs an external commands and returns a tuple containing the
    status code and the output.

    when running in line, a temporary file is used to store the
    callee's output to circumvent a problem in getstatusoutput.

    INPUT:
    cmd           -- command to run
    background    -- run command as a background process
    pollDelay     -- number of seconds to wait to ensure process is still
                     running in case it dies prematurely.
    captureOutput -- when set, the output is returned to the caller. Otherwise
                     an empty string is returned.
    echo          -- prints (echoes) the cmd output to the console
    echoEmpty     -- allows to print the cmd empty output to the console
    kwargs        -- extra kwargs passed directly to subprocess Popen call

    OUTPUT:
    status -- the status from the shell running the command when the command
              is run directly and 'Running' or 'Terminated' when run in
              background mode.
    output -- command output (when background is False and captureOutput is
              True) or the process ID (when background is True)
    '''

    cmd = os.path.expandvars(cmd)

    log.debug('run_cmd: %s\n' % cmd)

    outDest = subprocess.PIPE if captureOutput else None

    subp = subprocess.Popen(cmd, shell=True,
                            stdout=outDest,
                            stderr=subprocess.STDOUT,
                            **kwargs)

    if background:
        pid = 0
        try:
            pid = subp.pid

            # ensure the process is still running after a little while
            for _ in range(pollDelay):
                if subp.poll():
                    try:
                        # do we have output?
                        output = subp.stdout.read()
                        if output:
                            log.warn("Process terminated, "
                                     "it's last words were: %s" % output)
                    except Exception:
                        pass
                    return ('Terminated', pid)
                time.sleep(1)
            return('Running', pid)
        except OSError as e:
            log.error('OSError raised when running command', e)
            return ('Error', pid)

    output = b''
    newOutput = b''

    while True:
        try:
            newOutput = subp.stdout.readline()
        except AttributeError:
            pass
        if echo:
            if echoEmpty or newOutput.strip():
                sys.stdout.write(newOutput.decode())
                sys.stdout.flush()
        output += newOutput
        if newOutput == b'' and subp.poll() is not None:
            break

    return(subp.returncode if subp.returncode else 0, output.decode())


def printYamlFile(yamlFile):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)

    with open(yamlFile) as fd:
        config = yaml.safe_load(fd)

    pp.pprint(config)


def readYaml(yamlFile):
    with open(yamlFile) as fd:
        config = yaml.safe_load(fd)
    return config


def checkPath(thePath):
    if not os.path.exists(thePath):
        raise Exception('%s not found' % thePath)


def findFile(thePath, theFile):
    for parentDir, subDirs, files in os.walk(thePath, topdown=True, followlinks=False):
        for f in files:
            if f == theFile:
                filePath = os.path.join(parentDir, f)
                return filePath
    return '' 

    
    
    