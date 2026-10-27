#!/usr/bin/env python

import argparse
import multiprocessing
import os
import sys
import shutil
sys.path.insert(0,'/home/xli3/pytestAuto')
from utils.util import shCmd, runCmd, readYaml, printYamlFile, checkPath

class BuildException(Exception) : pass

def getVxworksEnv(installPath):
    if os.path.exists(installPath + '/vxworks'):
        wrenvPrefix = '%s/wrenv.sh -p vxworks' % installPath
        # get pkgs_path from $WIND_PKGS
        cmd = wrenvPrefix + ' env | grep WIND_PKGS='
        lines = os.popen(cmd).readlines()
        pkgsPath = lines[0].strip().lstrip('WIND_PKGS=')
    else:
        raise BaseException('%s not correct since vxworks was not found' % installPath)
    return pkgsPath, wrenvPrefix


def getDvdPath(ipnet_dir):
    parent_dir = os.path.dirname(ipnet_dir)
    base_name = os.path.basename(ipnet_dir)
    for e in os.listdir(parent_dir):
        if e == base_name or e.startswith(base_name + '-'):
            return parent_dir + '/' + e
    raise BuildException('cannot find %s' % ipnet_dir)
    return ''


def getDvdFullpath(dvd_path, git_relative_path):
    new_path = dvd_path
    for d in [x for x in git_relative_path.split('/') if x.strip()]:
        new_path = getDvdPath(new_path + '/' + d)
    return new_path


def buildVxworks(cfg, installPath, bsp, tool, smp, m64bit, cpu=None, ipv6=False, module=None, debug=False, spin=True):
    # xiaozhan, debug
    buildVsb(cfg, installPath, bsp, tool, smp, m64bit, cpu, ipv6, debug, spin)
    vipPath = buildVip(cfg, installPath, bsp, tool, smp, m64bit, cpu, ipv6, module, debug, spin)
    return vipPath
    
def buildVxworks2Targets(cfg, installPath, bsp, tool, smp, m64bit, cpu=None, ipv6=False, debug=False):
    vsbPath = buildVsb(cfg, installPath, bsp, tool, smp, m64bit, cpu, ipv6, debug=False)
    
    vipOverrides = {'vxparam' : ["""RTNET_JSON_FILE='"/romfs/25002.json"'""",], }
    vipPath = buildVip(cfg, installPath, bsp, tool, smp, m64bit, cpu, ipv6, debug, overrides=vipOverrides)
    copyVxImage(vipPath + '/default', os.path.dirname(vipPath) + '/vxImage/t0')

    #shutil.rmtree(vipPath)
    vipOverrides = {'vxparam' : ["""RTNET_JSON_FILE='"/romfs/25003.json"'""",], }
    vipPath = buildVip(cfg, installPath, bsp, tool, smp, m64bit, cpu, ipv6, debug, overrides=vipOverrides)
    copyVxImage(vipPath + '/default', os.path.dirname(vipPath) + '/vxImage/t1')


def buildVsb(cfg, installPath, bsp, tool, smp, m64bit, cpu=None, ipv6=False, debug=False, spin=True):
    # xiaozhan, add spin=False to support branch
    _, wrenv = getVxworksEnv(installPath)
    if spin is True:
        wrenvPrefix = "%s LM_LICENSE_FILE=27000@ala-lic4.wrs.com " % wrenv
    else:
        wrenvPrefix = wrenv + '/relx '
    # prjPath = os.getcwd()
    prjPath = '/home/xli3/vxworks'   # xiaozhan, debug
    print('======current prj pat in vsb function=======', prjPath)
    # create VSB
    flag64bit = '-lp64' if m64bit else '-ilp32'
    ipv6Flag = '-inet6' if ipv6 else ''
    smpFlag = '-smp' if smp else '-up'
    cpuFlag = '-cpu %s' % cpu if cpu is not None else ''
    # vsbCreateCmd = 'vxprj vsb create -force -S %s %s %s %s -bsp %s %s_vsb' % (flag64bit, ipv6Flag, cpuFlag, smpFlag, bsp, bsp)
    vsbCreateCmd = 'vxprj vsb create -force -S %s %s %s %s -bsp %s /home/xli3/vxworks/%s_vsb' % (flag64bit, ipv6Flag, cpuFlag, smpFlag, bsp, bsp)  # xiaozhan, debug
    # xiaozhan debug, if you want to build in spin path or branch
    # vsbCreateCmd = 'vxprj vsb create -force -S %s %s %s %s -bsp %s %s/%s_vsb' % (flag64bit, ipv6Flag, cpuFlag, smpFlag, bsp, installPath, bsp)
    runCmd(vsbCreateCmd, wrenvPrefix)

    os.chdir("%s/%s_vsb" % (prjPath, bsp))   # xiaozhan  debug
    # config VSB
    vsbConfigCmd = 'vxprj vsb config -s'
    if 'layer' in cfg['vsb']:
        for c in cfg['vsb']['layer']: 
            vsbConfigCmd += ' -add _WRS_CONFIG_%s=y' % c.upper()
    if 'vxmake' in cfg['vsb']:
        for c in cfg['vsb']['vxmake']: 
            vsbConfigCmd += ' -add _WRS_CONFIG_COMPONENT_%s=y' % c.upper()
    runCmd(vsbConfigCmd, wrenvPrefix)
    
    # config VSB
    vsbConfigCmd = 'vxprj vsb config -s'
    cflags = []
    if 'extra_build_cflags' in cfg['vsb'] and cfg['vsb']['extra_build_cflags']:
        for f in cfg['vsb']['extra_build_cflags']:
            cflags.append(f)
        extra_defines = " ".join(cflags)
        vsbConfigCmd += ' -add _WRS_CONFIG_ADDEDCFLAGS="%s"' % extra_defines
        runCmd(vsbConfigCmd, wrenvPrefix)

    # config VSB --xiaozhan, add
    vsbConfigCmd = 'vxprj vsb config -s'
    cflags = []
    if 'vsboptstr' in cfg['vsb'] and cfg['vsb']['vsboptstr']:
        for f in cfg['vsb']['vsboptstr']:
            cflags.append(f)
        extra_defines = " ".join(cflags)
        vsbConfigCmd += ' -add %s' % extra_defines
        runCmd(vsbConfigCmd, wrenvPrefix)

    # xiaozhan, debug
    # input('-----debug vsb option for CRYPTO option----')


    # RTNET has issue when building with debugging info
    #if debug:
    #    runCmd('vxprj vsb config -s -add _WRS_CONFIG_BUILD_MODE_debug=y', wrenvPrefix)
    #    runCmd('vxprj vsb config -s -add _WRS_CONFIG_DEBUG_FLAG=y', wrenvPrefix)

    runCmd("make -j %s" % multiprocessing.cpu_count(), wrenvPrefix)
    os.chdir(prjPath)
    return os.path.join(prjPath, '%s_vsb' % bsp) 


def buildVip(cfg, installPath, bsp, tool, smp, m64bit, cpu=None, ipv6=False, module=None, debug=False, overrides={}, spin=True):
    # xiaozhan, debug, spin=False to support branch
    pkgsPath, wrenv = getVxworksEnv(installPath)
    if spin is True:
        wrenvPrefix = "%s LM_LICENSE_FILE=27000@ala-lic4.wrs.com " % wrenv
    else:
        wrenvPrefix = wrenv + '/relx '
    # prjPath = os.getcwd()
    prjPath = '/home/xli3/vxworks'  # xiaozhan, debug
    print('======current prj pat in vip function=======', prjPath)
    # create VIP
    os.chdir(prjPath)   # xiaozhan,in current project instead of spin path
    vipPath = prjPath + '/%s_vip' % bsp
    print(shCmd('rm -fr %s' % vipPath))
    vipCreateCmd = 'vxprj create -vsb %s_vsb %s %s %s' % (bsp, bsp, tool, vipPath)
    #if m64bit:
    #    vipCreateCmd += ' -lp64'
    if ipv6:
        vipCreateCmd += ' -inet6'
    for c in cfg['vip']['component']:
        if c.startswith('\\') and c.endswith('\\'):
            vipCreateCmd += ' -c ' + c.replace('\\', '').upper()
        else:
            vipCreateCmd += ' -c INCLUDE_' + c.upper()
    if bsp == 'fsl_imx6':
        vipCreateCmd += ' -c INCLUDE_FSL_IMX6Q_SABRELITE'
    
    # handle overrides for vxparam   xiaozhan, modify to isinstance
    if isinstance(overrides, dict):
        if 'vxparam' in overrides:
            for c in overrides['vxparam']:
                vipCreateCmd += ' -p ' + c
    else:
        if 'vxparam' in cfg['vip']:
            for c in cfg['vip']['vxparam']:
                vipCreateCmd += ' -p ' + c

    runCmd(vipCreateCmd, wrenvPrefix)

    # os.chdir("%s_vip" % bsp)
    os.chdir(vipPath)    # xiao zhan, debug

    # xiaozhan---workaround for FTP parameter
    if module == 'FTP':
        cmd = 'vxprj parameter setstring LOGIN_BANNER_TEXT "Login Banner #1"'
        runCmd(cmd, wrenvPrefix)

    if 'component_remove' in cfg['vip']:
        for c in cfg['vip']['component_remove']:
            runCmd('vxprj component remove INCLUDE_%s' % c, wrenvPrefix)
    
    # add file for VIP
    if 'add_file' in cfg['vip']:
        for f in cfg['vip']['add_file']:
            if f.startswith('/'): # handle absolute path
                checkPath(f)
                runCmd('cp %s ./' % f)
                filePath = os.path.basename(f)
            else:                 # handle relative path to pkgs_v2 
                filePath = getDvdFullpath(pkgsPath, f)
            vxprj = 'vxprj file add %s' % (filePath)
            runCmd(vxprj, wrenvPrefix)

    # replace file for VIP
    if 'replace_file' in cfg['vip']:
        for f in cfg['vip']['replace_file']:
            if f.startswith('/'): # handle absolute path
                checkPath(f)
                filePath = os.path.basename(f)
            else:                 # handle relative path to pkgs_v2 
                filePath = getDvdFullpath(pkgsPath, f)
            print('replace ./%s with %s' % (filePath, f))
            runCmd('cp %s ./' % f)
                
    # add extra_define for VIP
    if 'vx_extra_define' in cfg['vip']:
        for adddefines in cfg['vip']['vx_extra_define']:
            # get EXTRA_DEFINE first to avoid replacing existing EXTRA_DEFINE
            lines = runCmd(' vxprj buildmacro get %s_vip.wpj EXTRA_DEFINE' % bsp, wrenvPrefix)
            extra_defines = "\'" + ' '.join(lines).replace('\n', ' ') + ' ' + adddefines + "\'"
            runCmd('vxprj buildmacro set EXTRA_DEFINE %s' % extra_defines, wrenvPrefix)
            
    # add json configuration file for VIP
    if 'romfs' in cfg['vip']:
        if not os.path.exists('./romfs'):
            runCmd('mkdir -p romfs')
        for f in cfg['vip']['romfs']:
            if f.startswith('/'):  # handle absolute path
                checkPath(f)
                filePath = f
            else:                 # handle relative path to pkgs_v2
                filePath = getDvdFullpath(pkgsPath, f)
            runCmd('cp %s ./romfs/' % filePath)
    
    runCmd('vxprj build', wrenvPrefix)
    # os.chdir(prjPath)
    os.chdir('/home/xli3/pytestAuto')    # xiaozhan, debug
    return vipPath


def copyVxImage(fromPath, toPath):
    # copy vxWorks, uVxWorks and *.dtb
    def isVxImage(filePath):
        fileName = os.path.basename(filePath)
        if fileName in ('vxWorks', 'uVxWorks'):
            return True
        else:
            _, ext = os.path.splitext(fileName)
            if ext == '.dtb':
                return True
            else:
                return False
    
    if not os.path.exists(fromPath):
        print('%s not existed' % fromPath)
        sys.exit(1)
    if not os.path.exists(toPath):
        try:
            os.makedirs(toPath)
        except FileExistsError:
            pass
    
    vxImages = filter(isVxImage, os.listdir(fromPath))
    [shutil.copy(fromPath + '/' + x, toPath) for x in vxImages]

def parseArgument():
    parser = argparse.ArgumentParser(description='VxWorks Build Tool')
    parser.add_argument('-s', '--source', action='store', dest='source', help='spin or git path, required option')
    parser.add_argument('-m', '--module', action='store', dest='module', help='module define in vxBuildConfig.yaml, required option')
    parser.add_argument('-b', '--bsp', action='store', dest='bsp', help='bsp, required option')
    parser.add_argument('-c', '--cpu', action='store', dest='cpu', help='cpu type, default is None')
    parser.add_argument('-t', '--tool', action='store', dest='tool', help='compiler : llvm or gnu, default is llvm')
    parser.add_argument('--up', action='store_false', dest='smp', help='up or smp, default is smp')
    parser.add_argument('--64', action='store_true', dest='m64bit', help='32 or 64 bits, default is 32 bits')
    parser.add_argument('--ipv6', action='store_true', dest='ipv6', help='ipv6 supported, default is ipv6 not supported')
    
    args = parser.parse_args()

    if args.source is None or args.module is None or args.bsp is None:
        parser.print_help()
        exit(1)
    if args.tool is None:
        args.tool = 'llvm'
    return args

def main():
    args = parseArgument()
    print(args)
    
    cfg = readYaml('vxBuildConfig.yaml')
    if args.module not in cfg:
        print('the module %s not found in vxBuildConfig.yaml' % args.module)
        sys.exit(1)
    checkPath(args.source)

    buildVxworks(cfg[args.module], args.source, args.bsp, args.tool, args.smp, args.m64bit, args.cpu, args.ipv6)
    #copyVxImage('./%s_vip/default' % bsp, '/folk/lchen3/tftpboot/t2/')


if __name__ == '__main__':
    main()
    