#############################################################################
#
# Copyright (c) 2020-2021 Wind River Systems, Inc.
#
# The right to copy, distribute, modify or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#
#############################################################################

#
import os
import re
from subprocess import call

debugFlag = False # boolean to turn on/off debug log
shcmdIndicator = '===='

class build_exception(Exception):
    pass

def sudovoid(cmd):
    if debugFlag:
        print '%s %s' % (shcmdIndicator, 'sudo ' + cmd.strip())
    os.popen('sudo ' + cmd)

def sudo(cmd):
    if debugFlag:
        print '%s %s' % (shcmdIndicator, 'sudo ' + cmd.strip())
    return os.popen('sudo ' + cmd).readlines()

# replace os.system()
def shcmdvoid(cmd):
    if debugFlag:
        print '%s %s' % (shcmdIndicator, cmd.strip())
    os.system(cmd)

# replace os.popen()
def shcmd(cmd):
    if debugFlag:
        print '%s %s' % (shcmdIndicator, cmd.strip())
    return os.popen(cmd)

def udo(cmd):
    return call(cmd.split())

def dirname(module, port):
    if port and module == "ipcom":
        lines = os.popen("ls -d -1 %s/%s-%s-* 2> /dev/null" % (port, module, port)).readlines()
        if len(lines) > 0:
            mline = lines[0].rstrip()
            if len(mline) > 0:
                return mline
    else:
        if port:
            lines = os.popen("ls -d -1 %s/%s-* 2> /dev/null" % (port, module)).readlines()
            if len(lines) > 0:
                mline = lines[0].rstrip()
                if len(mline) > 0:
                    return mline
        lines = os.popen("ls -d -1 pkg/%s-* 2> /dev/null" % module).readlines()
        if len(lines) > 0:
            mline = lines[0].rstrip()
            if len(mline) > 0:
                return mline
    lines = os.popen("ls -d -1 cvs/%s 2> /dev/null" % module).readlines()
    if len(lines) > 0:
        mline = lines[0].rstrip()
        if len(mline) > 0:
            return mline
    return module


def get_vxworks_env(install_path):
    subdirEnvs = ( ('vxworks', 'WIND_PKGS='),
                   ('vxworks-7/pkgs_v2', None),
                   ('vxworks-7/pkgs', None),
                   ('helix/guests/vxworks-7', None),
                   ('vxworks-653', None),
               )

    for subdir, env in subdirEnvs:
        wrenv_prefix = '%s/wrenv.sh -p %s' % (install_path, subdir.split('/')[0])
        if env is None:
            pkgs_path = os.path.join(install_path, subdir)
            if os.path.exists(pkgs_path):
                break
        else:
            if os.path.exists(os.path.join(install_path, 'wrenv.sh')):
                cmd = wrenv_prefix + ' env | grep WIND_PKGS='
                lines = os.popen(cmd).readlines()
                pkgs_path = lines[0].strip().lstrip('WIND_PKGS=')
                break
            else:
                # search folders to get pkgs_path
                vxPath = os.path.join(install_path, 'vxworks')
                if os.path.exists(vxPath):
                    pkgs_path = findVxworksPath(vxPath)
                    if pkgs_path:
                        break
                    else:
                        raise BaseException('vxworks pkgs_path not found at installation path %s' % install_path)
                else:
                    raise BaseException('vxworks sub directory not found at installation path %s' % install_path)
    else:
        raise BaseException('pkgs_path and wrenv_prefix not found at installation path %s' % install_path)
    return pkgs_path, wrenv_prefix


def findVxworksPath(fromPath):
    keyword = 'os/net'
    for parentDir, subDirs, files in os.walk(fromPath, topdown=True):
        for subdir in subDirs:
            subPath = os.path.join(parentDir, subdir)
            if subPath.endswith('os/net'):
                return '/'.join(subPath.split('/')[:-1])
    return ''

