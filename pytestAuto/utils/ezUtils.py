import logging
import os
import pprint
import subprocess
import sys
import time
import yaml
sys.path.insert(0, '/home/xli3/pytestAuto')
from utils.log_record import log

def checkPath(thePath):
    if not os.path.exists(thePath):
        raise Exception('%s not found' % thePath)


def readYaml(yamlFile):
    with open(yamlFile) as fd:
        config = yaml.safe_load(fd)
    return config


def readYamlConfig(configYaml, key=None):
    cfg = readYaml(configYaml)
    if key is None:
        return cfg
    else:
        return cfg[key]
    

def printYamlFile(yamlFile, module=None):
    pp = pprint.PrettyPrinter(indent=4)

    with open(yamlFile) as fd:
        config = yaml.safe_load(fd)

    if module is None:
        pp.pprint(config)
    else:
        pp.pprint(config[module])

debugShell = False
shcmdIndicator = '=== '
# log = logging.getLogger(__name__)  # xiaozhan, remove

def runCmd(cmd, background=False, pollDelay=4, captureOutput=True, echo=False,
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

    return subp.returncode if subp.returncode else 0, output.decode()


def shCmd(cmd, retString=True):
    lines = os.popen(cmd).readlines()
    if retString:
        lines = ''.join(lines)
    log.debug('cmd is\n%s' % cmd)
    log.debug(lines)
    return lines

