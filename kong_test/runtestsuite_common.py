import os
from subprocess import call

debugFlag = False # boolean to turn on/off debug log
shcmdIndicator = '===='

class build_exception(Exception):
    pass

def sudovoid(cmd):
    if debugFlag:
        print '%s %s' % (shcmdIndicator, 'sudo ' + cmd)
    os.popen('sudo ' + cmd)

def sudo(cmd):
    if debugFlag:
        print '%s %s' % (shcmdIndicator, 'sudo ' + cmd)
    return os.popen('sudo ' + cmd).readlines()

# replace os.system()
def shcmdvoid(cmd):
    if debugFlag:
        print '%s %s' % (shcmdIndicator, cmd)
    os.system(cmd)

# replace os.popen()
def shcmd(cmd):
    if debugFlag:
        print '%s %s' % (shcmdIndicator, cmd)
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
    if os.path.exists(install_path + '/vxworks-7'):
        if os.path.exists(install_path + '/vxworks-7/pkgs_v2'):
            pkgs_path = install_path + '/vxworks-7/pkgs_v2'
            wrenv_prefix = '%s/wrenv.sh -p vxworks-7' % install_path
        elif os.path.exists(install_path + '/vxworks-7/pkgs'):
            pkgs_path = install_path + '/vxworks-7/pkgs'
            wrenv_prefix = '%s/wrenv.sh -p vxworks-7' % install_path
        else:
            raise BaseException('%s vxworks-7 has neither pkgs_v2 nor pkgs' % install_path)
    elif os.path.exists(install_path + '/helix/guests/vxworks-7'):
        pkgs_path = install_path + '/helix/guests/vxworks-7/pkgs_v2'
        wrenv_prefix = '%s/wrenv.sh -p helix' % install_path
    elif os.path.exists(install_path + '/vxworks-653'):
        pkgs_path = install_path + '/vxworks-653/pkgs'
        wrenv_prefix = '%s/wrenv.sh -p vxworks-653' % install_path
    else:
        raise BaseException('%s not correct since vxworks-7, vxworks-653 and helix/guests/vxworks-7 was not found' % install_path)
    return pkgs_path, wrenv_prefix
