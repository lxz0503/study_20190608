#!/usr/bin/env python
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
#09apr20,yyl support helix dynamic configuraton for ZCU102, VXWEXEC-48814
#31mar20,clb add test-ipv6 option
#03mar20,yyl add native test support for directly connected target, VXWEXEC-47902
#20may14,h_s enable use_umldev when uml needed in test, V7NET-343.
#29apr14,h_s adapt test script for vx7, US35892.
#

import MimeWriter, StringIO, base64, uu, gzip, tarfile, smtplib #mail related
import getopt
from glob import glob
import os
import re
import sys
import time
import pexpect
import pdb
import traceback
import socket

import lockboard
from runtestsuite_conf import *
from runtestsuite_common import *
from vlmTarget import VLMException, vlmTargetConfigs, loadImageToTarget

class CommandlineArgumentException(Exception):
    pass
class NoMoreTestsException(Exception):
    pass
class BuildException(Exception):
    pass
class TestSuiteException(Exception):
    pass
class TestSilentlySkippedException(Exception):
    pass
class SetupException(Exception):
    pass
class VersionControlException(Exception):
    pass
class ConnectivityException(Exception):
    pass

class BuildOpts:
    # just a list of cflags
    def __init__(self, args = None, cflags = None, vars = None):
        self.vars = []
        self.cflags = []
        self.add(args, cflags, vars)

    def add(self, args = None, cflags = None, vars = None):
        if args:
            self.vars.extend(args.vars)
            self.cflags.extend(args.cflags)
        if cflags:
            if isinstance(cflags, list):
                self.cflags.extend(cflags)
            else:
                self.cflags.append(cflags)
        if vars:
            if isinstance(vars, list):
                self.vars.extend(vars)
            else:
                self.vars.append(vars)

    def cflags_option(self):
        if len(self.cflags) > 0:
            return "IPEXTRACFLAGS='" + " ".join(self.cflags) + "'"

    def vars_options(self, limit = " "):
        return limit.join(self.vars) if len(self.vars) > 0 else ""

    def all(self):
        nopts = BuildOpts(vars = self.vars)
        nopts.add(vars = self.cflags_option())
        return nopts.vars_options()

    def desc(self):
        nopts = BuildOpts(vars = self.vars)
        nopts.add(vars = self.cflags_option())
        return nopts.vars_options(limit = "\r\n")


class Log:
    LEVEL_DEBUG = 0
    LEVEL_INFO  = 1
    LEVEL_ERROR = 2
    def __init__(self, level):
        "level - Lowest level to be shown in the log, must be one of the LEVEL_XXX constants."
        self.level = level

    def __print(self, prefix, message):
        print "[" + localtimeStr() + "] " + prefix + ": " + message

    def debug(self, message):
        if self.level <= Log.LEVEL_DEBUG:
            self.__print("Debug", message)

    def info(self, message):
        if self.level <= Log.LEVEL_INFO:
            self.__print("Info", message)

    def error(self, message):
        if self.level <= Log.LEVEL_ERROR:
            self.__print("Error", message)

    def __call__(self, msg):
        self.info(msg)


class Host(object):
    def __init__(self, log, p):
        self.log = log
        self.p = p

    def moduleToRootDir(self, module):
        "Returns the makefile-macro for the root directory of the cvs module"
        return {'ipnet2': 'IPNET_ROOT',
                'ipssl2': 'IPSSL_ROOT',
                'iplite2': 'IPLITE_ROOT',
                'ipmcrypto': 'IPCRYPTO_ROOT',
                'ipipsec2': 'IPIPSEC_ROOT'}.get(module, module.upper() + '_ROOT')


    def moduleRevision(self, module = "ipcom"):
        return self.p['revision'].get(module, self.p['revision']['default'])


    def create_ipnet_config_c(self, vc_modules):
        class already_configured(Exception):
            pass
        nets = self.p['networks']
        usb_dev_list = self.p['unix_usb_devs']
        if "ipnet2" in vc_modules:
            try:
                fn = '%s/config/ipnet_config.c' % dirname('ipnet2', 'unix')
                lines = open(fn).readlines()
                in_if_conf = 0
                conf = []
                for line in lines:
                    if '/** -- RUNTESTSUITE -- **/' in line:
                        raise already_configured('Already configured')

                    if '*ipnet_conf_interfaces[]' in line:
                        in_if_conf = 1
                        conf.append('/** -- RUNTESTSUITE -- **/\n')
                        conf.append('#ifdef IP_PORT_UNIX\n')
                        conf.append('IP_CONST char *ipnet_conf_interfaces[] =\n')
                        conf.append('{\n')
                        conf.append('    "ifname lo0",\n')
                        conf.append('    "inet 127.0.0.1/8",\n')
                        conf.append('    "inet6 ::1/128",\n')
                        conf.append('    "inet6 ff01::1/16",\n')
                        conf.append('    IP_NULL,\n')
                        for net in range(nets):
                            conf.append('    "ifname eth%d",\n' % net)
                            conf.append('    "inet driver",\n')
                            conf.append('    IP_NULL,\n')

                        if usb_dev_list is not None:
                            conf.append('    "ifname eth%d",\n' % nets)
                            conf.append('    "inet driver",\n')
                            conf.append('    IP_NULL,\n')

                        conf.append('    IP_NULL\n')
                        conf.append('};\n')
                        conf.append('#else /* IP_PORT_UNIX */\n')
                    conf.append(line)
                    if in_if_conf == 1 and line.find('};') != -1:
                        in_if_conf = 0
                        conf.append('#endif /* IP_PORT_UNIX */\n')

                self.log.debug('Creating IPNET configuration file')
                open(fn, 'w').writelines(conf)
            except already_configured, desc:
                pass
            except IOError, desc:
                self.log.debug('%s exception raised: %s' % (desc.__class__.__name__, desc))
                raise

        if "iplite2" in vc_modules:
            try:
                fn = '%s/config/iplite_config.c' % dirname('iplite2', 'unix')
                lines = open(fn).readlines()
                in_if_conf = 0
                conf = []
                for line in lines:
                    if '/** -- RUNTESTSUITE -- **/' in line:
                        raise already_configured('Already configured')
                    if 'iplite_conf_interfaces[]' in line:
                        conf.append('/** -- RUNTESTSUITE -- **/\n')
                        conf.append('#ifdef IP_PORT_UNIX\n')
                        in_if_conf = 1
                        conf.append('iplite_conf_interfaces[] =\n')
                        conf.append('{\n')
                        for net in range(nets):
                            conf.append('    {\n')
                            conf.append('        "eth%d",\n' % net)
                            conf.append('        "driver",\n')
                            conf.append('        IP_NULL\n')
                            conf.append('    },\n')
                        conf.append('    {\n')
                        conf.append('        IP_NULL,\n')
                        conf.append('        IP_NULL,\n')
                        conf.append('        IP_NULL\n')
                        conf.append('    }\n')
                        conf.append('};\n')
                        conf.append('#else /* IP_PORT_UNIX */\n')

                    conf.append(line)
                    if in_if_conf == 1 and '};' in line:
                        in_if_conf = 0
                        conf.append('#endif /* IP_PORT_UNIX */\n')

                self.log.debug('Creating IPLITE configuration file')
                open(fn, 'w').writelines(conf)
            except already_configured, desc:
                pass
            except IOError, desc:
                log.debug('%s exception raised: %s' % (desc.__class__.__name__, desc))
                raise

    def cvs_checkout(self, vc_modules, vports):
        if self.p['checkout']:
            sudovoid('rm -rf ' + self.p['name'])
        shcmdvoid('mkdir %s 2>/dev/null' % self.p['name'])
        os.chdir(self.p['srctree'] if self.p['srctree'] != None else self.p['name'])
        for port in vports:
            shcmdvoid('mkdir %s 2>/dev/null' % port)
        shcmdvoid('mkdir cvs 2>/dev/null')
        shcmdvoid('mkdir pkg 2>/dev/null')
        if self.p['checkout']:
            expanded_modules = []
            for port in vports:
                # markus print port
                nvc = self.expand(vc_modules, vports[port])
                for vc in nvc:
                    if vc not in expanded_modules:
                        expanded_modules.append(vc)
            self.log(",".join(vc_modules) + " => " + ",".join(expanded_modules))
            for vc_module in expanded_modules:
                self.checkout(vc_module, self.moduleRevision(vc_module), vports.keys(), self.p['packages'], self.p['ipv4-only'])
            if 'iplite2' in expanded_modules:
                self.checkout('ipnet2', self.moduleRevision('ipnet2'), vports.keys(), self.p['packages'], self.p['ipv4-only'])


    def findTarBall(self, module, packages, port):
        base = "%s/%s-%s" % (packages, module, port)
        lobj = shcmd("ls -1 %s-*.tgz 2> /dev/null" % base)
        lines = lobj.readlines()
        if len(lines) > 0 and len(lines[0]) > 0:
            pkg = {}
            for line in lines:
                line = line.rstrip()
                if len(line) == 0:
                    continue

                key = 0
                m = re.match("%s-r(\d+)_(\d+)_(\d+).tgz" % base, line)
                if m:
                    major, minor, patch = m.groups()
                    level = 0
                else:
                    m = re.match("%s-p(\d+)_(\d+)_(\d+)_(\d+).tgz" % base, line)
                    if m:
                        major, minor, patch, level = m.groups()
                    else:
                        self.log('Ignoring: %s' % line)
                        continue

                key = int(level) + int(patch) * 100 + int(minor) * 10000 + int(major) * 1000000
                pkg[key] = line

            keys = pkg.keys()
            keys.sort()
            package = pkg[keys[len(keys) - 1]]
            self.log('Selecting: %s' % package)
            return package
        raise VersionControlException('no package found in %s for %s@%s' % (packages, module, port))


    def findPackage(self, module, packages, port, ipv4_only):
        if port and module == "ipcom":
            tar = self.findTarBall(module, packages, port)
        elif ipv4_only and (module == "ipnet2" or module == "iplite2"):
            tar = self.findTarBall(module, packages, 'ipv4-any')
        else:
            tar = self.findTarBall(module, packages, 'any')
        return tar

    def findPatches(self, packages, pkg):
        pkg = os.path.splitext(os.path.split(pkg)[1])[0]
        print pkg
        print "%s/patches/%s*" % (packages, pkg)
        pkgs = glob("%s/patches/%s*" % (packages, pkg))
        if pkgs:
            pkgs.sort()
        print pkgs
        return pkgs

    def portDef(self, module, port, ipv4_only):
        if module == "ipcom":
            return port
        elif module in ("ipnet2", "iplite2"):
            if ipv4_only:
                return "ipv4-any"
        return "any"

    def walk_dir_to_copy(self, dirname, mod_name, vdir):
        elems = sorted( os.listdir(dirname) )
        for e in elems:
            if e == ".":
                continue
            if e == "..":
                continue
            if os.path.isfile(dirname + "/" + e):
                continue
            full_path = dirname + "/" + e
            if mod_name == 'ntp' and full_path.find("sntp") != -1:
                continue # Special case. There is a directory called ntp in the sntp component
            if mod_name == 'radius' and full_path.find("ike") != -1: 
                continue 
            if e == mod_name or e.startswith(mod_name + '-'): # support both git and spin
                if os.path.isdir(full_path + "/test"):
                    print(" >>>>>>>>>>>>>>>>> copy directory " + full_path)
                    shcmd('cp -fr %s %s' % (full_path, vdir))
                    # support spin
                    git_full_path = self.remove_path_version(full_path)
                    if git_full_path != full_path:
                        os.renames(vdir + '/' + os.path.basename(full_path), 
                                   vdir + '/' + os.path.basename(git_full_path))
                    return 2
                else:
                    if mod_name == "ipcrypto":
                        ret = self.walk_dir_to_copy(full_path, mod_name, vdir)
                        if ret > 0:
                            return ret
                    print(" >>>>>>>>>>>>>>>>> failed copy directory " + full_path)
                    #return 1
            if os.path.isdir(full_path):
                ret = self.walk_dir_to_copy(full_path, mod_name, vdir)
                if ret > 0:
                    return ret
        return 0

    def remove_path_version(self, the_path):
        tokens = filter(lambda x: x.strip() != '', the_path.split('/'))
        new_tokens = list(tokens)
        
        for i in xrange(len(tokens)):
            found = re.search('(.*?)-\.*?.\.*?.\.*?.\.*?', tokens[i])
            if found is not None:
                new_tokens[i] = found.groups()[0]
        if the_path[0] == '/':
            return '/' + '/'.join(new_tokens)
        else:
            return '/'.join(new_tokens)
            
    def __get_dvd_path(self, ipnet_dir):
        parent_dir = os.path.dirname(ipnet_dir)
        base_name = os.path.basename(ipnet_dir)
        for e in os.listdir(parent_dir):
            if e == base_name or e.startswith(base_name + '-'):
                return parent_dir + '/' + e
        return ''
        
    def checkout_internal(self, module, revision, vdir = 'cvs'):
        board = self.p['vxworks'].keys()[0]
        pkgs_path, _ = get_vxworks_env(self.p['vxworks'][board]['path'])
        dvd_dirs = [self.__get_dvd_path(pkgs_path + x) for x in testable_packages_search_paths]
 
        for dvd_dir in dvd_dirs:
            if self.walk_dir_to_copy(dvd_dir, module, vdir) == 2:
                break
        else:
            print(">>>>>>>>>>>>> module %s with test subdirectory does not exist!" % module)
            sys.exit(1)
        return

    def convertRevision(self, module, revision, ports):
        """
        This routine exist because there are
        two different branches for the 6.5 release.
        Certain packages like ipcom shall be checked out from
        release6_5-standalone when dealing with the lkm:las ports

        Returns the correct revision to checkout
        """
         # Always use iptestengine from HEAD
        if module == 'iptestengine':
            return 'HEAD'

        rsuffix = ''
        if (revision == 'release6_5') and (module == 'ipcom' or module == 'ipnet2'):
            for port in ports:
                if port == 'lkm' or port == 'las':
                    rsuffix = '-standalone'
        return revision + rsuffix


    def doPatch(self, port, patch):
        ext = os.path.splitext(patch)[1]
        print ext
        if ext == '.zip':
            print "UNZIP %s at %s" % (port, patch)
            shcmdvoid("cd %s && unzip -o %s" % (port, patch))
        elif ext == '.tgz':
            print "UNTAR %s at %s" % (port, patch)
            shcmdvoid("tar -C %s -xf %s" % (port, patch))


    def checkout(self, module, revision, ports, packages, ipv4_only):
        if packages:
            if module == "ipcom":
                for port in ports:
                    try:
                        pkg = self.findPackage(module, packages, port, ipv4_only)
                        shcmdvoid("tar -C %s -xf %s" % (port, pkg))
                        patches = self.findPatches(packages, pkg)
                        if patches:
                            for patch in patches:
                                self.doPatch(port, patch)
                    except:
                        pass
            else:
                try:
                    pkg = self.findPackage(module, packages, None, ipv4_only)
                    shcmdvoid("tar -C pkg -xf %s" % (pkg))
                    patches = self.findPatches(packages, pkg)
                    if patches:
                        for patch in patches:
                            self.doPatch('pkg', patch)
                except:
                    pass
        self.checkout_internal(module, self.convertRevision(module,revision,ports))


    def tag(self, module, tag_name, force=False):
        "cvs tag module"
        if module == "ipcrypto" or module == "ipmcrypto":
            self.tag("ipcrypto", tag_name, force)
            self.tag("ipmcrypto", tag_name, force)
        else:
            cmd = 'cvs -q tag '
            if force == True:
                cmd += '-F '
            cmd += tag_name
            self.log.info('Tagging "%s" with "%s"' % (module, tag_name))
            self.log.debug('Running "%s"' % cmd)
            cwd = os.getcwd()
            os.chdir("cvs")
            os.chdir(module)
            shcmdvoid(cmd)
            os.chdir(cwd)


    def expand(self, omods, expansion):
        modules = list(omods)
        # Deal with substitutes
        if expansion in vc_port_substitute and vc_port_substitute[expansion]:
            for key in vc_port_substitute[expansion]:
                if key in modules:
                    modules.remove(key)
                    for vc in vc_port_substitute[expansion][key]:
                        if not vc in modules:
                            modules.append(vc)

        # Deal with platform specific dependencies
        if expansion in vc_port_dependency and vc_port_dependency[expansion]:
            for key in vc_port_dependency[expansion]:
                if key in modules:
                    for vc in vc_port_dependency[expansion][key]:
                        if not vc in modules:
                            modules.append(vc)

        # Deal with global dependencies
        for key in vc_dependency:
            if key in modules:
                for vc in vc_dependency[key]:
                    if not vc in modules:
                        modules.append(vc)
        return modules


    def build_socktest(self, arch = None, endian = None, static_link = False):
        cflags = ['-DIPCOM_USE_SOCK=IPCOM_SOCK_NATIVE', '-DIPCOM_USE_PACKET']
        vars = []
        if static_link:
            vars.append('IPUML32=yes')
        if endian == 'big':
            cflags.append('-DIP_BIG_ENDIAN')
        elif endian == 'little':
            cflags.append('-DIP_LITTLE_ENDIAN')
        uopts = BuildOpts(vars = vars, cflags = cflags)
        binaries = self.build("unix", '/socktest', '', ["ipcom"], None, self.p['networks'], uopts, True, objroot = 'obj-unix-socktest', arch = arch)
        for binary in binaries:
            elems = binary.split('/')
            if elems[len(elems) - 1] == 'ipout':
                binaries = [binary]
                break
        return  [binaries[0]]


    def build(self, port, xtype, sh, modules, expansion, nets, bopts, rebuild = True, objroot = None, arch = None):
        "Returns The full path of the built binary"
        if not expansion:
            expansion = port

        modules = self.expand(modules, port + xtype)
        root_dir = os.getcwd()
        self.log.info('Building %s binaries using %s' % (port, ",".join(modules)))
        ptype = port + xtype
        if ptype not in platform:
            ptype = port

        mopts = BuildOpts(args = bopts,
                          cflags = platform[ptype]['extra_build_cflags'],
                          vars = platform[ptype]['extra_build_opt'])
        mopts.add(cflags = platform['all']['extra_build_cflags'],
                  vars = platform['all']['extra_build_opt'])
        mopts.add(vars = 'IPPORT=%s' % port)

        pcflags = self.p.get('platform_cflags', None)
        if pcflags:
            bflags = pcflags.get(port + xtype, None)
            if not bflags:
                bflags = pcflags.get(port, None)
            if bflags:
                mopts.add(cflags = bflags)

        if arch:
            mopts.add(vars = 'IPTARGET=%s' % arch)

        cmd = '%smake ' % sh
        configs = []
        mods    = []

        if objroot:
            objroot = '%s/%s/%s' % (root_dir, dirname('ipcom', port), objroot)
            mopts.add(vars = 'IPOBJDIR=%s' % objroot)

        xtra = mopts.desc()
        for module in modules:
            mver = dirname(module, port)
            if mver == 'cvs/' + module:
                modver = self.moduleRevision(module)
            else:
                modver = mver.split('-')
                modver = modver[len(modver) - 1]
            mods.append('%s(%s)' % (module, modver))
            configs.append('%s=%s/%s' % (self.moduleToRootDir(module), root_dir, mver))

        mopts.add(vars = configs)
        cmd += mopts.all()
        lstr = "BUILD PARAMETERS:\r\n"
        lstr += mopts.desc()
        self.log(lstr)
        self.p['build'] += "PORT: %s\r\n" % port
        self.p['build'] += "PACKAGES: " + ",".join(mods)
        self.p['build'] += "\r\n" + xtra + "\r\n"
        if rebuild:
            cmd += ' new'
        else:
            cmd += ' all'
        cmd += ' 2>&1'

        os.chdir(dirname('ipcom', port))
        self.log.debug('Running "%s"' % cmd)
        o = shcmd(cmd)
        os.chdir(root_dir)
        lines = o.readlines()
        open("_".join(('cc_%s%s' % (port, xtype)).split('/')), 'w').writelines(cmd)
        open("_".join(('build_%s%s' % (port, xtype)).split('/')), 'w').writelines(lines)
        binary_name = []
        for line in lines:
            if 'make:' in line:
                raise BuildException(mailBody(None, lines, 'makefile output:'))
            if line.find('gcc -o') != -1:
                binary_name.append(line.split()[2])
            if 'ld' in line and '-o' in line:
                obj = line.split("-o")
                binary_name.append(obj[1].split()[0])
            if 'Linking' in line or 'LD [M]' in line:
                obj = line.split()
                binary_name.append(obj[len(obj) - 1])

        if len(binary_name) == 0:
            if rebuild:
                raise BuildException(mailBody(None, lines, 'no binaries found'))
            self.log.info('No binaries were rebuilt')
        else:
            self.log.info(",".join(binary_name) + ' was successfully built')
        return binary_name



class LinuxHost(Host):
    "Configures a Linux target to be able to host several IPCOM UNIX binaries"
    subnet = '192.168.'

    def __init__(self, log, p):
        super(LinuxHost, self).__init__(log, p)
        import getpass
        self.user = getpass.getuser()
        shcmdvoid('sudo tunctl -d force_module_load_if_req > /dev/null')
        shcmdvoid('sudo chmod a+rw /dev/net/tun')
        self.target_addresses = []
        self.vlm_targets = []
        self.tunnames  = []
        self.lockfiles = []
        self.uml_switches = []
        self.magic_number = 199
        self.bridges = []
        self.brctl = {}
        self.host_ids = {}
        self.wrlinux_setup_complete = False
        if p['ipv6-only']:
            LinuxHost.subnet = 'fc00::'
            self.address_separator = ':'
        else:
            self.address_separator = '.'

    def __del__(self):
        for address in self.target_addresses:
            for pid in shcmd("ps auxww | grep -v awk | awk '/%s/ { print $2 }'" % address):
                shcmdvoid('kill %s > /dev/null 2>&1' % pid)
        # Must wait for all binaries to finish before removing the TUN/TAP devices
        time.sleep(3)
        for uml_switch in self.uml_switches:
            for pid in shcmd("ps auxww | grep -v awk | awk '/%s/ { print $2 }'" % uml_switch.split('/')[-1]):
                shcmdvoid('kill %s > /dev/null 2>&1' % pid)
            shcmdvoid('rm -f %s' % uml_switch)

        # Must wait for all binaries to finish before removing the TUN/TAP devices
        time.sleep(3)
        for bridge in self.bridges:
            shcmdvoid('sudo ifconfig %s down' % bridge)
            shcmdvoid('sudo brctl delbr ' + bridge)
        time.sleep(3)
        if not self.p['buildonly'] and self.p['vxworks'].keys()[0] in simicsTargets:
            #print shcmd('sudo brctl delbr tap0').read()
            print shcmd('sudo pkill simics-common').read()
            print shcmd('sudo pkill uml_switch').read()
            print shcmd('sudo tunctl -d tap0').read()
        for tun in self.tunnames:
            shcmdvoid('sudo tunctl -d %s >/dev/null' % tun)

        # Destroy the lockfiles
        for lock in self.lockfiles:
            lock.close()


    def createHostAddress(self, net_unique_id):
        "Returns a unique host address that is reachable on the network 'net_unique_id'."
        if not self.host_ids.has_key(net_unique_id):
            self.host_ids[net_unique_id] = range(20, 1, -1)
            if self.p['direct']:
                self.host_ids[net_unique_id] = range(20, 2, -1)
        entry = self.host_ids[net_unique_id].pop()
        address = '%s%d%s%d' % (LinuxHost.subnet, net_unique_id, self.address_separator, entry)
        return address, entry

    def getHostNetmask(self):
        return '255.255.255.0'

    def bridgeDevice(self, br_name, dev_name):
        plines = sudo('brctl addif %s %s' % (br_name, dev_name))
        if len(plines) and "is already a member of a bridge; can't enslave it to bridge" in plines[0]:
            raise SetupException(mailBody(None, plines, 'setup error:'))
        sudo('ip link set up dev %s' % dev_name)

    def flushDevice(self, dev_name):
        sudo('ip -4 addr flush dev %s' % dev_name)

    def configDevice(self, dev_name, ipconf):
        sudo('ip link set up dev %s' % dev_name)
        if ':' in self.address_separator:
            sudo('ip -6 addr add %s dev %s' % (ipconf, dev_name))
        else:
            sudo('ip -4 addr add %s dev %s' % (ipconf, dev_name))

    def createBridgeName(self, net, net_unique_id):
        return "rsbr%d%d" % (net, net_unique_id)

    def createTunName(self, net, net_unique_id, extra = ''):
        return "rstap%d%d%s" % (net, net_unique_id, extra)

    def createTunNameR6(self, net, net_unique_id):
        return "unixtap%d%d" % (net, net_unique_id)

    def verifyHostUniqueId(self, unique_id):
        lines = shcmd('ip addr').readlines()
        addr = '%s%d' % (LinuxHost.subnet, unique_id)
        for line in lines:
            if addr in line:
                return False
        tname  = self.createTunName(0, unique_id)
        t6name = self.createTunNameR6(0, unique_id)
        bname  = self.createBridgeName(0, unique_id)

        # Check all existing bridges and tun/tap devices
        lines = shcmd('ip link show').readlines()
        for line in lines:
            if (tname in line or
                t6name in line or
                bname in line):
                return False
        return True


    def createHostUniqueId(self):
        while True:
            lfile = '/tmp/rslock_%d' % self.magic_number
            lfd = open(lfile, "w+")
            try:
                os.chmod(lfile, 0666)
            except:
                pass
            try:
                try:
                    # try to lock it
                    import fcntl
                    fcntl.flock(lfd, fcntl.LOCK_EX|fcntl.LOCK_NB)
                except IOError:
                    raise SetupException(mailBody(None, ["ioerror, unique identifier already occupied"], 'setup error:'))

                # Be compatible with r6
                if not self.verifyHostUniqueId(self.magic_number):
                    raise SetupException(mailBody(None, ["unique identifier already occupied"], 'setup error:'))
                # Store the lockfile
                self.lockfiles.append(lfd)
                return self.magic_number
            except SetupException:
                lfd.close()
                self.magic_number -= 1
                if self.magic_number == 0:
                    raise SetupException(mailBody(None, ["No unique identifiers available"], 'setup error:'))


    def createLinuxAddress(self, net_unique_id):
        return "%s%d%s1" % (LinuxHost.subnet, net_unique_id, self.address_separator)

    def configTunDevice(self, tun_name, br_name, net_unique_id):
        if br_name:
            shcmdvoid('sudo ifconfig %s inet 1.1.1.%d netmask 255.255.255.255 up' % (tun_name, net_unique_id))
            self.bridgeDevice(br_name, tun_name)
        else:
            self.masterAddress = address = self.createLinuxAddress(net_unique_id)
            self.configDevice(tun_name, '%s/28' % address)


    def createTunDev(self, net, provided_unique_id = None, extra = ''):
        # Create a Unique ID unless specified
        if not provided_unique_id:
            unique_id = self.createHostUniqueId()
        else:
            unique_id = provided_unique_id
        line = None
        while True:
            lines = shcmd('sudo tunctl -u %s -t %s' % (self.user, self.createTunName(net, unique_id, extra))).readlines()
            time.sleep(2)
            if len(lines) == 0:
                if provided_unique_id:
                    raise SetupException(mailBody(None, ["unable to create TAP device due to unique ID specified"], 'setup error:'))
                unique_id = self.createHostUniqueId()
            else:
                line = lines[0]
                break
        tun_name = re.match(".*'([^']+)'", line).group(1)
        self.tunnames.append(tun_name)
        return tun_name, unique_id


    def createBridgeDev(self, net, net_unique_id):
        "returns the name of the created device"
        if self.brctl.has_key(net):
            return self.brctl[net]

        # Guard against races
        errstr  = []
        br_name = self.createBridgeName(net, net_unique_id)
        cmd = 'sudo brctl addbr %s 2>&1' % br_name
        errstr.append(cmd)
        lines = shcmd('sudo brctl addbr %s 2>&1' % br_name).readlines()
        errstr += lines
        if len(lines) == 0:
            self.log.debug('Creating 802.1d bridge device named ' + br_name)
            shcmdvoid('sudo brctl sethello %s 10 2>&1' % br_name)
            shcmdvoid('sudo brctl setfd %s 0 2>&1' % br_name)
            self.masterAddress = address = self.createLinuxAddress(net_unique_id)
            shcmdvoid('sudo ifconfig %s inet %s up' % (br_name, address))
            self.brctl[net] = (br_name, net_unique_id, address)
            self.bridges.append(br_name)
            return br_name, address
        errstr.append("Current Network:")
        errstr += shcmd("ip link show").readlines()
        raise SetupException(mailBody(None, errstr, 'network setup error:'))


    def createUmlSwitch(self, tap_name, net_unique_id):
        ctl_fn = "/tmp/uml_ctl_%d_%d" % (os.getpid(), net_unique_id)
        sudo("rm -f %s" % ctl_fn)
        self.uml_switches.append(ctl_fn)
        shcmdvoid("uml_switch -unix %s -hub -tap %s > /dev/null 2>&1 &" % (ctl_fn, tap_name))
        return ctl_fn


    def createNetwork(self, use_bridge = True):
        nets = self.p['networks']
        for net in range(nets):
            if not self.umlswitch.has_key(net):
                tun_name, net_unique_id = self.createTunDev(net)
                if use_bridge:
                    br_name, br_address = self.createBridgeDev(net, net_unique_id)
                else:
                    br_name = None
                    br_address = None

                self.configTunDevice(tun_name, br_name, net_unique_id)
                uml_ctl_fn  = self.createUmlSwitch(tun_name, net_unique_id)
                self.umlswitch[net] = {'name': br_name, 'magic': net_unique_id, 'uml_ctl': uml_ctl_fn, 'address': br_address}


    def ping_one(self, target_address):
        for i in range(1, 10):
            if ':' in self.address_separator :
                o = shcmd('ping6 -c 1 ' + target_address)
            else:
                o = shcmd('ping -c 1 ' + target_address)
            for line in o.readlines():
                if (('64 bytes from %s:' % target_address) in line or
                    ('%s bytes=64' % target_address) in line):
                    return True
            time.sleep(0.5)
        return False


    def ping(self, mobj = None):
        self.log.debug('Checking connectivity to all targets')
        for target_address in self.getTargetAddresses():
            if self.ping_one(target_address):
                self.log.info('Target at address %s is running' % target_address)
            else:
                print('ping %s failed' % target_address)
                if self.p['noconn']:
                    self.log.info('Target at address %s is dead' % target_address)
                else:
                    lines = [ 'Could not contact %s over the network: ' % target_address ]
                    lines += shcmd("ip link show").readlines()
                    lines += shcmd("ip -4 addr show").readlines()
                    lines += shcmd("brctl show").readlines()
                    if mobj:
                        mailBody(mobj, lines, 'network connectivity error:')
                    raise ConnectivityException('network connectivity error:')


    def start(self):
        self.host_array = []
        self.conf = []
        self.native = []
        self.umlswitch = {}


    def runAnvlTestSuite(self, targets):
        self.log.info('Running Ixia ANVL test suite')
        root_dir = os.getcwd()
        manual = self.p['manual']
        mobj = mailObject()

        if manual:
            raw_input('Press enter to continue')
        else:
            # Wait for IPv6 Duplicate Address Detection
            time.sleep(2)
            root_dir = os.getcwd()
            os.chdir('cvs/ipanvl/script')
            cmd = './run_suite.sh'
            for if_name in self.tunnames:
                cmd += ' ' + if_name

            for line in shcmd(cmd):
                m = re.match("Logfile: ([^\s]+)", line)
                if m:
                    mobj.addFileAttachment(m.group(1), m.group(1))
            os.chdir(root_dir)
        return mobj


    def runTestSuite(self, targets):       # xiaozhan this is to run suite
        self.log.info('Running test suite')
        root_dir = os.getcwd()
        suite_name  = ",".join(self.p['testengine_name'])
        loops       = self.p['permutations']
        manual      = self.p['manual']
        mobj        = mailObject()
        addresses   = self.target_addresses
        iptestopts  = ['-t %s' % suite_name]
        if self.p['ipv4-only'] and not self.p['ipv6-only']:
            iptestopts.append('-4')
        if self.p['ipv6-only'] and not self.p['ipv4-only']:
            iptestopts.append('-6')
        if self.p['test-ipv6'] and not self.p['ipv4-only']:
            iptestopts.append('-6')
            
        if self.p['loop']:
            iptestopts.append('--permute')
        if 'layout_net' in self.p:
            iptestopts.append('--layout_net ' + self.p['layout_net'])

        self.p['tinderbox_vars']['status']        = 'test_failed'
        self.p['tinderbox_vars']['tests_failed']  = "1"
        self.p['tinderbox_vars']['tests_ok']      = "0"
        self.p['tinderbox_vars']['tests_skipped'] = "0"
        self.p['tinderbox_vars']['tests_total']   = "1"

        ok        = 0
        failed    = 0
        skipped   = 0
        total     = 0

        # Do some permutations of the host file, so different nodes are LAS
        icwd = dirname('iptestengine', None)
        self.log.info("Using iptestengine: %s" % icwd)
        host_array  = list(self.host_array)
        conf        = list(self.conf)
        test_suites = True
        try:
            for i in range(loops):
                hosts = "groups = {'default': ("
                hosts += ",".join(host_array)
                if len(self.native) > 0:
                    hosts += "," + ",".join(self.native)
                elif len(host_array) == 1:
                    hosts += ","

                self.ping(mobj)
                self.log.info("%d/%d: Test setup: " % (i + 1, loops) + hosts + ")");
                conf.append(hosts + ')}\n')
                open('%s/config/hosts.py' % icwd, 'w').writelines(conf)
                
                if self.p['name'] == 'RTNET_RTP' and self.vlm_targets:
                    # RTNet rtp needs the target console for iptestengine.py
                    for t in self.vlm_targets:
                        print ('quit vlm board %s console %s %s' % (t.id, t.Terminal_Server, 2000 + int(t.Terminal_Server_Port)))
                        self.quitTelnet(t)

                if manual:
                    raw_input('Press enter to continue with next configuration')
                else:
                    os.chdir('%s/src' % icwd)
                    shcmdvoid('rm -f log/test*')
                    print '=== current dir:%s' % os.getcwd()
                    test_cmd = './iptestengine.py ' + " ".join(iptestopts)      # xiaohan  real test: ./iptestengine.py -t ipipsec.ipipsec.esp_transport_aesctr_none

                    if self.p['vxworks'].keys()[0] in simicsTargets:
                        if self.p['codecoverage']:
                            print '=== start simics code coverage'
                            test_cmd += ' --timeout 600'
                            self.target_addresses[0]
                            sendCmdSimicsConsole(getIpPrefix(self.target_addresses[0], self.address_separator) + '1', 
                                                 simicsTargets[self.p['vxworks'].keys()[0]]['console-port'], 
                                                 startCodeCov)
                        else:
                            test_cmd += ' --timeout 50'
                    
                    print '=== %s' % test_cmd
                    o = shcmd(test_cmd)    # xiaozhan   execute test command  and return is o, need to analyze o

                    # Run the test suite
                    test_suite_success = False
                    lines = [("** CONFIGURATION %d " % i) + ",".join(host_array) + " **\n"]
                    lines += o.readlines()
                    mobj.addBody("".join(lines))

                    # Indicate one error in case we fail parsing
                    s = 0
                    o = 0
                    f = 1
                    t = 1
                    for line in lines:
                        if 'A target is dead' in line:
                            files = shcmd('ls -1 log/test*').readlines()
                            if len(files) > 0:
                                mobj.addGZipFileAttachment('iptestengine-%d-%s-%s.txt.gz' % (i, self.p['name'], suite_name), files[0].rstrip())
                            raise ConnectivityException('A target is dead')

                        if 'tests_ok' in line:
                            m = re.search(r'tests_ok:\s+(\d+).\s+tests_fail:\s+(\d+).\s+tests_skipped:\s+(\d+)', line)
                            if m:
                                o,f,s = m.groups()
                                o       = int(o)
                                f       = int(f)
                                s       = int(s)
                                t       = o + f + s

                                ok      += o
                                failed  += f
                                skipped += s
                                total   += t

                            if failed == 0:
                                test_suite_success = True
                            break

                    if self.p['codecoverage']:
                        print '=== end simics code coverage'
                        sendCmdSimicsConsole(getIpPrefix(self.target_addresses[0], self.address_separator) + '1', 
                                             simicsTargets[self.p['vxworks'].keys()[0]]['console-port'], 
                                             endCodeCov)
                        time.sleep(60*1)
                                             
                    if f != 0:
                        files = shcmd('ls -1 log/test*').readlines()
                        if len(files) > 0:
                            mobj.addGZipFileAttachment('iptestengine-%d-%s-%s.txt.gz' % (i, self.p['name'], suite_name), files[0].rstrip())

                    os.chdir(root_dir)
                    if f != 0:
                        self.log.info('%d/%d: Test suite failed' % (i + 1, loops))
                    else:
                        if s == t:
                            self.log.info('%d/%d: Test suite skipped' % (i + 1, loops))
                        else:
                            self.log.info('%d/%d: Test suite finished successfully' % (i + 1, loops))

                if self.p['counterclockwise']:
                    entry = host_array.pop(0)
                    host_array.append(entry)
                else:
                    host_array = host_array[len(host_array) - 1:] + host_array[:len(host_array) - 1]
            else:
                # We've completed the loop; do setup the values.
                self.p['tinderbox_vars']['tests_failed']  = str(failed)
                self.p['tinderbox_vars']['tests_ok']      = str(ok)
                self.p['tinderbox_vars']['tests_skipped'] = str(skipped)
                self.p['tinderbox_vars']['tests_total']   = str(total)

                # If the test has failed; do add logfiles
                if failed != 0 or self.p['save_logs']:
                    for target in targets:
                        target.addLogfiles(mobj)
                    if failed != 0:
                        raise TestSuiteException(mobj)

                # We've skipped all tests
                if skipped == total:
                    self.p['tinderbox_vars']['status'] = 'test_skipped'
                    raise TestSilentlySkippedException(mobj)
                self.p['tinderbox_vars']['status'] = 'success'

            return mobj
        except ConnectivityException, inst:
            # Need to restore the path; or the logfiles wont work.
            os.chdir(root_dir)
            for target in targets:
                target.terminalError(mobj)
            # We go target dead.
            self.p['tinderbox_vars']['status'] = 'target_died'
            # A target has died
            for target in targets:
                target.addLogfiles(mobj)
            raise TestSuiteException(mobj)


    def quitTelnet(self, vlm_target):
        vlm_target.conn.terminate()
        """ # the following code will create a defunct telnet
        vlm_target.conn.sendcontrol(']')
        vlm_target.conn.expect('telnet> ')
        vlm_target.conn.sendline('q')
        vlm_target.conn.expect('Connection closed.')
        """
        
    def getTargetAddresses(self):
        return self.target_addresses


class zipLogFile:
    def __init__ (self, name, fil):
        self.name = name
        self.file = fil

    def add(self, mobj):
        try:
            mobj.addGZipFileAttachment(self.name, self.file)
        except:
            mobj.addBody("Failed to add attachment: %s -> %s\r\n" % (self.name, self.file))

    def cleanup(self):
        pass


import threading
class fdLogFile(threading.Thread):
    def __init__ (self, name, fd, log, verbose = False):
        threading.Thread.__init__(self)
        self.name = name
        self.fd   = fd
        self.log  = log
        self.cont = True
        self.verbose = verbose

    def run(self):
        while self.cont:
            try:
                import select
                rdfds, wrfds, xfds = select.select([self.fd], [], [], 1.0)
                if self.fd in rdfds:
                    x = os.read(self.fd, 10000)
                    self.log += x
                    if self.verbose:
                        print x
            except:
                pass

    def add(self, mobj):
        self.cont = False
        self.join()
        try:
            mobj.addGZipAttachment(self.name, self.log)
        except:
            mobj.addBody("Failed to add attachment: %s\r\n" % self.name)

    def cleanup(self):
        self.cont = False
        self.join()
        os.close(self.fd)


class build(object):
    def __init__(self, host, log, p):
        self.host       = host
        self.log        = log
        self.p          = p
        self.logfiles   = []


class wrlinuxTarget(build):
    def __init__(self, host, board, type, log, p):
        super(wrlinuxTarget, self).__init__(host, log, p)
        self.ipcfg         = self.p['wrlinuxconf']
        self.wropts        = self.p['wrlinux'][type][board]
        self.started       = []
        self.pkgs          = []
        self.type          = type
        self.board         = board
        self.system        = 'wrlinux'
        self.tftpdir       = '/tftpboot'
        self.exportdir     = '/export'
        self.linuxprompt   = 'root@%s' % self.board
        self.yamonprompt   = 'YAMON>'
        self.ubootprompt   = '=>'
        self.redbootprompt = 'RedBoot>'
        self.grubprompt    = 'grub>'

        # The first one must be the linux console prompt
        self.supported_prompts = [self.linuxprompt, self.yamonprompt, self.ubootprompt, self.grubprompt, self.redbootprompt]
        # Force bridge creation
        self.p['use_extdev'] = True
        # Extend timeout when using pexpect
        self.timeout = 100
        # Check the distro path
        if not os.path.exists(self.p['wrpath']):
            raise SetupException(mailBody(None, ["Invalid path to the Wind River Linux Distro (%s)" % self.p['wrpath']]))
        # Do some sanity checks
        if not self.wropts['qemu']:
            if not self.wropts['tty']:
                raise SetupException(mailBody(None, ["No tty specified"]))
            if not self.wropts['stty']:
                raise SetupException(mailBody(None, ["No stty (baudrate) specified"]))
            if not self.wropts['interface']:
                raise SetupException(mailBody(None, ["No interface specified"]))


    def get_ports(self):
        return {'lkm': 'lkm',
                'las': 'las',
                'unix': 'unix/socktest'}

    def wrlog(self, s):
        return self.log.info('%s:%s :: %s' % (self.system, self.board, s))

    def wrbase(self):
        return self.wrdir

    def wrproject(self, project):
        return os.path.join(self.wrbase(), project)

    def wrbuild(self, project):
        return os.path.join(self.wrproject(project), 'build')

    def wrcvs(self):
        return os.path.join(self.wrbase(), 'cvs-repository')

    def wrimage(self):
        return self.p['wrpath']

    def wrinstall(self):
        return self.wrimage()

    def rpms(self, arch = None):
        rpmdir = os.path.join(self.wrimage(), 'RPMS')
        if not arch:
            return rpmdir
        return os.path.join(rpmdir, arch)


    def wrlinux(self):
        return os.path.join(self.wrinstall(), 'wrlinux')

    def wrpatches(self, project):
        return os.path.join(self.wrproject(project), 'workarounds')

    def prefix(self):
        return "usr/lastools"

    def las_prefix(self):
        return "/root"

    def version(self, modpath):
        modext = modpath.split('-')
        if len(modext) == 1:
            return "r6_6_100"
        else:
            return modext[len(modext) - 1]

    def patched(self, project, patch):
        patch_file = os.path.join(self.wrpatches(project), patch)
        shcmdvoid('touch %s' % patch_file)

    def is_patched(self, project, patch):
        patch_file = glob(os.path.join(self.wrpatches(project), patch))
        return len(patch_file) != 0

    def wrproperties(self, file):
        properties = {}
        lines = open(file)
        for line in lines:
            if '=' in line:
                params = line.split('=')
                if len(params) >= 2:
                    properties[params[0].strip()] = "=".join(params[1:]).strip()
        return properties

    def build_extra_tools(self, project, install_stage):
        "Build the patched ip tool and the ipcom_socktest tool"
        olddir = os.getcwd()
        print self.properties['TARGET_CROSS_COMPILE']
        os.putenv('CROSS_COMPILE', '%s' % self.properties['TARGET_CROSS_COMPILE'])
        os.putenv('WIND_HOME', self.wrinstall())

        hosttool = "%s/host-cross/bin" % self.wrproject(project)
        crosspath = "%s/host-cross/%s/bin" % (self.wrproject(project), self.properties['TARGET_TOOLCHAIN'])

        path = os.getenv('PATH')
        os.putenv('PATH','%s:%s:%s' % (crosspath, hosttool, path))
        libc_include = '%s/usr/include' % install_stage['glibc']
        os.chdir(olddir)

        self.wrlog('Building IPROUTE2 command')
        os.chdir(dirname('iproute2', None))

        # Do the translation of the more important variables.
        sed = 'sed -e \'s:KERNEL_INCLUDE=.*$:KERNEL_INCLUDE=%s/include:\' ' % install_stage['linux']
        sed += '-e \'s:LIBC_INCLUDE=.*$:LIBC_INCLUDE=%s:\' ' % libc_include
        sed += '-e \'s:SBINDIR=.*$:SBINDIR=:\' '
        sed += '-e \'s:DESTDIR=.*$:DESTDIR?=:\' '
        sed += '-e \'s:SUBDIRS=.*$:SUBDIRS=lib ip:\' '
        sed += '-e \'s:CC =.*$:CC=$(CROSS_COMPILE)gcc:\' '
        shcmdvoid('cat Makefile | %s | tee Makefile.lkm' % sed)
        shcmdvoid("cat Makefile | %s | tee Makefile.lkm" % sed)
        file = open('Makefile.lkm','a')
        file.write('install-lkm:\n')
        file.write('\t@for i in $(SUBDIRS); do $(MAKE) -C $$i install; done\n')
        file.close()

        shcmdvoid("make clean")
        shcmdvoid("make -f Makefile.lkm clean")
        self.build_and_store("make -f Makefile.lkm", "%s/cc_build_iproute" % self.wrproject(self.board))
        if shcmdvoid('cp -f ip/ip %s/sbin' % os.path.join(install_stage['ipnet'], self.prefix())) != 0:
            raise BuildException(mailBody(None, ['Failed to install ip tool in %s' %  os.path.join(install_stage['ipnet'], self.prefix())]))
        if shcmdvoid('cp -f ip/rtmon %s/sbin' % os.path.join(install_stage['ipnet'], self.prefix())) != 0:
            raise BuildException(mailBody(None, ['Failed to install rtmon tool in %s' %  os.path.join(install_stage['ipnet'], self.prefix())]))

        # Build the ipcom_socktest tool
        os.chdir(olddir)
        self.wrlog('Building UTELNETD daemon')
        os.chdir(dirname('utelnetd', None))

        # Do the translation of the more important variables.
        shcmdvoid("make clean")
        self.build_and_store("make", "%s/cc_build_utelnetd" % self.wrproject(self.board))

        if shcmdvoid('cp -f utelnetd %s/sbin' % os.path.join(install_stage['ipnet'], self.prefix())) != 0:
            raise BuildException(mailBody(None, ['Failed to install utelnetd tool in %s' %  os.path.join(install_stage['ipnet'], self.prefix())]))

        # Build the ipcom_socktest tool
        os.chdir(olddir)
        self.wrlog('Building VSFTPD daemon')
        os.chdir(dirname('vsftpd', None))

        # Do the translation of the more important variables.
        shcmdvoid("make clean")
        self.build_and_store("make", "%s/cc_build_vsftpd" % self.wrproject(self.board))

        if shcmdvoid('cp -f vsftpd %s/sbin' % os.path.join(install_stage['ipnet'], self.prefix())) != 0:
            raise BuildException(mailBody(None, ['Failed to install vsftpd tool in %s' %  os.path.join(install_stage['ipnet'], self.prefix())]))
        if shcmdvoid('cp -f vsftpd.conf %s/sbin' % os.path.join(install_stage['ipnet'], self.prefix())) != 0:
            raise BuildException(mailBody(None, ['Failed to install vsftpd.conf in %s' %  os.path.join(install_stage['ipnet'], self.prefix())]))

        # Build the ipcom_socktest tool
        os.chdir(olddir)
        ipcom_socktest = self.host.build_socktest(endian = self.wropts['endian'], arch = self.wropts['arch'])

        # If it was rebuilt.
        if len(ipcom_socktest):
            # Copy ipcom_socktest tool to destdir
            self.wrlog('cp -vf %s %s/bin/ipcom_socktest' % (ipcom_socktest[0], os.path.join(install_stage['ipnet'], self.prefix())))
            shcmdvoid('cp -vf %s %s/bin/ipcom_socktest' % (ipcom_socktest[0], os.path.join(install_stage['ipnet'], self.prefix())))
        else:
            self.wrlog('No binary built')

        #Reset these environment variables
        os.putenv('CROSS_COMPILE', '')
        os.putenv('WIND_HOME', '')
        os.chdir(olddir)


    def resolve_install_stage(self, cwd, wrbuild, install_stage, module, build_dir = False):
        lslines = glob("%s/INSTALL_STAGE/%s-*" % (wrbuild, module))
        if len(lslines) > 0 and len(lslines[0]) > 0:
            # Use absolute path
            install_stage[module] = os.path.join(cwd, lslines[0].strip())
            if build_dir:
                lslines = glob(install_stage[module] + "/build")
                if len(lslines) > 0:
                    install_stage[module] += '/build'
        else:
            raise BuildException(mailBody(None, ['Unable to locate INSTALL_STAGE %s directory' % module]))


    def resolve_build_stage(self, cwd, wrbuild, install_stage, module):
        lslines = glob("%s/%s-*" % (wrbuild, module))
        if len(lslines) > 0 and len(lslines[0]) > 0:
            # Use absolute path
            install_stage[module] = os.path.join(cwd, lslines[0].strip())
        else:
            raise BuildException(mailBody(None, ['Unable to locate BUILD %s directory' % module]))

    def run_and_store(self, cmd, output):
        self.wrlog('Running "%s"' % cmd)
        start_time = time.time()
        compiles = shcmd("%s 2>&1" % cmd)
        compiles = compiles.readlines()
        stop_time = time.time()
        self.wrlog('Completed after %d seconds' % int(stop_time - start_time))
        open(output, 'w').writelines(compiles)
        return compiles, stop_time - start_time


    def build_and_store(self, cmd, output):
        compiles, elapsed = self.run_and_store(cmd, output)
        for line in compiles:
            if line.find('make:') != -1 and line.find('Nothing to be done for') == -1 and line.find('is up to date') == -1:
                raise BuildException(mailBody(None, compiles, 'makefile output:'))
        return elapsed


    def build_all(self, project):
        i = 0
        while True:
            i = i + 1
            try:
                extravars = ''
                if self.wropts['qemucc']:
                    extravars += ' qemu_cc=%s' % self.wropts['qemucc']
                if self.wropts['qemuccopts']:
                    extravars += ' qemu_EXCONF="OS_CFLAGS=%s"' % self.wropts['qemuccopts']
                self.build_and_store("make %s IPEXTRACFLAGS='-DIPTESTENGINE -DIPCOM_LAS_SYSLOG_FACILITY=LOG_LOCAL7' all" % extravars, "%s/cc_build_all%d" % (self.wrproject(self.board), i))
                self.patched(project, 'all')
                break
            except:
                self.wrlog("Updating configuration ... %d" % i)
                updates = 0
                if not self.is_patched(project, 'rpmmacros'):
                    macros = glob("%s/host-cross/lib/rpm/*/macros" % self.wrproject(project))
                    if len(macros) != 0:
                        self.wrlog("Patching RPM macros -- check_files workaround")
                        shcmdvoid("sed -i -e 's:^%%__check_files:#%%__check_files:' %s" % macros[0])
                        updates = updates + 1
                        self.patched(project, 'rpmmacros')

                if not self.is_patched(project, 'tcpdump'):
                    specs = glob("%s/build/tcpdump*/SPECS/tcpdump.spec" % self.wrproject(project))
                    if len(specs) != 0:
                        self.wrlog("Patching TCPDUMP -- SPEC file dependency")
                        shcmdvoid("sed -i -e 's:Requires.*shadow-utils::' %s" % specs[0])
                        os.chdir(self.wrbuild(project))

                        ## Recreate the RPM.
                        self.build_and_store("make tcpdump.install", "%s/cc_build_tcpdump_install" % self.wrproject(self.board))
                        self.build_and_store("make tcpdump.rpm", "%s/cc_build_tcpdump_rpm" % self.wrproject(self.board))
                        os.chdir(self.wrproject(project))
                        updates = updates + 1
                        self.patched(project, 'tcpdump')

                if not self.is_patched(project, 'klibc'):
                    file = glob("%s/build/klibc*/.config" % self.wrproject(project))
                    if len(file) != 0:
                        self.wrlog("Patching KLIBC -- .config update")
                        shcmdvoid("touch %s" % file[0])
                        updates = updates + 1
                        self.patched(project, 'klibc')
                if updates == 0:
                    raise


    def build_setup_base(self):
        if self.host.wrlinux_setup_complete:
            self.wrlog('Skipping base setup, since it has already been done')
            return

        self.wrlog('Rebuilding the wrlinux project')
        cwd = os.getcwd()
        shcmdvoid("rm -rf %s" % self.wrbase())
        shcmdvoid("mkdir %s 2> /dev/null" % self.wrbase())
        shcmdvoid("mkdir %s 2> /dev/null" % self.wrcvs())

        # Setup the cvs modules for both ports
        expanded_modules = []
        expansions = [ 'lkm', 'las' ]
        lkmpath = None
        for expansion in expansions:
            modules = self.host.expand(self.p['vc'], expansion)
            for module in modules:
                if module == 'ipcom':
                    fmod = dirname(module, expansion)
                    if fmod != module:
                        modpath = "%s/ipcom-%s-%s" % (self.wrcvs(), expansion, self.version(fmod))
                        if module == 'ipcom' and expansion == 'lkm':
                            lkmpath = modpath
                        print "CVS %s -> %s" % (fmod, modpath)
                        shcmdvoid("ln -s %s/%s %s" % (cwd, fmod, modpath))
                        shcmdvoid("rm -rf %s/obj-%s-*" % (fmod, expansion))
                    else:
                        raise SetupException(mailBody(None, [ 'no ipcom for %s located' % expansion ]))
                else:
                    if module in expanded_modules:
                        continue

                    expanded_modules.append(module)
                    fmod = dirname(module, None)
                    if fmod != module:
                        npath = "%s/%s-any-%s" % (self.wrcvs(), module, self.version(fmod))
                        print "CVS %s -> %s" % (fmod, npath)
                        shcmdvoid("ln -s %s/%s %s" % (cwd, fmod, npath))
                    else:
                        print "No module %s found" % module

        # Setup the WRLINUX setup
        shcmdvoid("cd %s && sh setup" % (lkmpath + "/port/wrlinux/2_0"))
        self.host.wrlinux_setup_complete = True


    def store_rpm(self, arch, export):
        self.wrlog('Store RPM binaries')
        mylock = lockboard.Lock('wrlinux_internal')
        lfd = mylock.lock(True)
        self.wrlog('Lock "wrlinux" acquired')

        # setup the export directories
        rpmdir = self.rpms()
        if len(glob(rpmdir)) == 0:
            shcmdvoid("mkdir %s 2> /dev/null" % rpmdir)
        rpmdir = self.rpms(arch)
        if len(glob(rpmdir)) == 0:
            shcmdvoid("mkdir %s 2> /dev/null" % rpmdir)

        for pkg in self.pkgs:
            rpmbins = glob("%s/%s/%s-*" % (export, arch, pkg))
            for rpmbin in rpmbins:
                shcmdvoid('cp -vuf %s %s' % (rpmbin, rpmdir))

        ## We're done
        mylock.unlock(lfd)
        self.wrlog('Lock "wrlinux" released')


    def build_wrlinux(self, _):
        "Sets up a Wind River Linux host."
        ## Create the project directory.
        cwd = os.getcwd()
        ## nice to haves
        self.pkgs.append('libcap')
        self.pkgs.append('gawk')
        self.pkgs.append('sed')
        self.pkgs.append('bash')
        self.pkgs.append('mktemp')
        self.pkgs.append('sudo')
        self.pkgs.append('vlan')
        self.pkgs.append('iputils')
        self.pkgs.append('acl')
        self.pkgs.append('attr')
        self.pkgs.append('coreutils')
        self.pkgs.append('e2fsprogs')
        self.pkgs.append('device-mapper')
        self.pkgs.append('util-linux')

        if self.wropts['pkgdbg']:
            self.pkgs.append('readline')
            self.pkgs.append('ncurses')
            self.pkgs.append('procps')
            self.pkgs.append('libpcap')
            self.pkgs.append('openssl')
            self.pkgs.append('zlib')
            self.pkgs.append('flex')
            self.pkgs.append('syslog-ng')
            self.pkgs.append('gdb')
            self.pkgs.append('strace')
            self.pkgs.append('net-tools')

        if self.p['rebuild']:
            shcmdvoid("mkdir %s 2> /dev/null" % self.wrproject(self.board))
            shcmdvoid("mkdir %s 2> /dev/null" % self.wrpatches(self.board))

            # Create the kernel config file
            # " --enable-build=product|debug"
            configparams =  " --disable-dependency-tracking --enable-rpmdatabase=no --enable-board=%s --enable-rootfs=glibc_small --enable-kernel=standard" % self.board
            configparams += " --enable-jobs=4 --with-layer=%s/wrlinux-2.0,%s/iptestengine" % (self.wrcvs(), self.wrproject(self.board))
            configparams += " --with-rpm-dir=%s" % self.rpms()
            shcmdvoid("mkdir %s/iptestengine 2> /dev/null" % self.wrproject(self.board))
            shcmdvoid("mkdir %s/iptestengine/extra 2> /dev/null" % self.wrproject(self.board))
            shcmdvoid('echo "CONFIG_NE2K_PCI=y" >> %s/iptestengine/extra/knl-base.cfg' % (self.wrproject(self.board)))
            #SMP Support
            if self.p['smp']:
                shcmdvoid('echo "CONFIG_SMP=y" >> %s/iptestengine/extra/knl-base.cfg' % (self.wrproject(self.board)))
            # Enable support for IXDP425
            if self.board == 'intel_ixdp4xx':
                shcmdvoid('echo "CONFIG_ARCH_IXDP425=y" >> %s/iptestengine/extra/knl-base.cfg' % (self.wrproject(self.board)))

            # Do the template for this project
            configparams += " --with-template=%s,iptestengine/extra" % self.ipcfg
            if not self.p['speed']:
                configparams += ",extra/ipnet/debug"
            configparams = "%s/configure %s" % (self.wrlinux(), configparams)

            # Create the project
            mylock = lockboard.Lock('wrlinux_internal')
            lfd = mylock.lock(True)
            self.wrlog('Lock "wrlinux" acquired')
            open("%s/configure_line" % self.wrproject(self.board), 'w').writelines([ configparams ])
            os.chdir(self.wrproject(self.board))
            shcmdvoid(configparams +  " > %s/configure_output 2>&1" % self.wrproject(self.board))
            # We're done
            mylock.unlock(lfd)
            self.wrlog('Lock "wrlinux" released')
            for pkg in self.pkgs:
                shcmdvoid('echo "%s"   >> pkglist' % pkg)

            self.build_and_store("make reconfig", "%s/cc_build_reconfig" % self.wrproject(self.board))
            self.build_all(self.board)
            self.properties = self.wrproperties("%s/config.properties" % self.wrproject(self.board))
            print self.properties
            crosstools = glob("export/host-tools.tar.bz2")
            if len(crosstools):
                mylock = lockboard.Lock('wrlinux_internal')
                lfd = mylock.lock(True)
                self.wrlog('Lock "wrlinux" acquired')
                self.wrlog("Host tools package located")
                tools = glob("%s/wrlinux/host-tools" % self.wrimage())
                if len(tools) == 0:
                    self.wrlog("Host tools package not available in base install -- updating")
                    shcmdvoid("cd %s/wrlinux && tar jxf %s" % (self.wrimage(), os.path.join(self.wrproject(self.board), crosstools[0])))

                #We're done
                mylock.unlock(lfd)
                self.wrlog('Lock "wrlinux" released')

            #rpm install
            self.store_rpm(self.properties['TARGET_CPU_VARIANT'], 'export/RPMS')
        else:
            os.chdir(self.wrproject(self.board))
            if not self.is_patched(self.board, 'all'):
                self.build_all(self.board)
            os.chdir(self.wrbuild(self.board))
            shcmdvoid("rm .stamp/ipnet.compile; rm .stamp/linux.compile; rm .stamp/linux.rpm; rm .stamp/linux.install")
            shcmdvoid('rm .stamp/ipnet-usr.compile; rm .stamp/ipnet-usr.install; rm .stamp/ipnet-usr.rpm; rm .stamp/ipnet-usr.sysroot')

            self.build_and_store("make IPEXTRACFLAGS='-DIPTESTENGINE -DIPCOM_LAS_SYSLOG_FACILITY=LOG_LOCAL7'  ipnet.compile", "%s/cc_build_ipnet" % self.wrproject(self.board))
            self.build_and_store("make linux.compile", "%s/cc_build_linux" % self.wrproject(self.board))
            self.build_and_store("make linux.rpm", "%s/cc_rpm_linux" % self.wrproject(self.board))
            self.build_and_store("make IPEXTRACFLAGS='-DIPTESTENGINE -DIPCOM_LAS_SYSLOG_FACILITY=LOG_LOCAL7' ipnet-usr.compile", "%s/cc_build_ipnet-usr" % self.wrbase())
            self.properties = self.wrproperties("%s/config.properties" % self.wrproject(self.board))
            print self.properties
            #rpm install
            os.chdir(self.wrproject(self.board))
            self.store_rpm(self.properties['TARGET_CPU_VARIANT'], 'export/RPMS')
        os.chdir(cwd)
        install_stage = {}
        self.resolve_install_stage(cwd, self.wrbuild(self.board), install_stage, 'ipnet')
        self.resolve_install_stage(cwd, self.wrbuild(self.board), install_stage, 'glibc', self.wropts['pkgdbg'])
        self.resolve_build_stage(cwd, self.wrbuild(self.board), install_stage, 'linux')
        print install_stage

        # Do the EXTRA tools
        self.build_extra_tools(self.board, install_stage)

        # Do the repackage
        os.chdir(self.wrbuild(self.board))
        shcmdvoid("rm .stamp/ipnet-usr.install; rm .stamp/ipnet-usr.rpm; rm .stamp/busybox.install; rm .stamp/busybox.rpm")
        self.build_and_store("make ipnet-usr.rpm", "%s/cc_rpm_ipnet-usr" % self.wrproject(self.board))
        self.build_and_store("make busybox.rpm", "%s/cc_rpm_busybox" % self.wrproject(self.board))
        os.chdir(self.wrproject(self.board))
        self.build_all(self.board)

        # Create some startup scripts if they dont already exist
        self.wrlog("Creating startup scripts")
        f = open("export/dist/etc/rcS.d/Stestengine",'w')
        if self.wropts['pkgdbg']:
            f.write('#!/bin/bash\n')
            f.write('ulimit -c unlimited\n')
        else:
            f.write('#! /bin/sh\n')
        f.write('/usr/lastools/sbin/vsftpd /usr/lastools/sbin/vsftpd.conf\n')
        if self.wropts['pkgdbg']:
            f.write('/usr/lastools/sbin/utelnetd -d -l /bin/sh\n')
            f.write('syslog-ng\n')
        else:
            f.write('/usr/lastools/sbin/utelnetd -d -l /bin/sh\n')

        # Setup the las prefix directory
        f.write('ln -s /%s/bin/* %s\n' % (self.prefix(), self.las_prefix()))
        f.write('ln -s /%s/sbin/* %s\n' % (self.prefix(), self.las_prefix()))
        f.write('ln -s /%s/sbin/ip /sbin/ip\n' % (self.prefix()))
        f.write('/usr/lastools/sbin/sockrun &> /dev/null &\n')
        f.close()
        shcmdvoid("chmod a+rwx export/dist/etc/rcS.d/Stestengine")
        f = open("export/dist/usr/lastools/sbin/sockrun",'w')
        f.write('#! /bin/sh\n')
        f.write('while `/bin/true`; do /usr/lastools/bin/ipcom_socktest &> /dev/null; sleep 1; done\n')
        f.close()
        if self.wropts['pkgdbg']:
            ipdcmd = "export/dist/%s/ipd" % self.las_prefix()
            f = open(ipdcmd,'w')
            f.write('#!/bin/bash\n')
            f.write('ulimit -c unlimited\n')
            f.write('/%s/bin/ipd $*\n' % self.prefix())
            f.close()
            shcmdvoid("chmod a+rwx %s" % ipdcmd)
        shcmdvoid("chmod a+rwx export/dist/usr/lastools/sbin/sockrun")
        os.chdir(cwd)


    def build(self, bopts):
        "bopts - boot options"
        if self.p['networks'] != 1:
            raise SetupException(mailBody(None, [ "When using LAS, only one network is currently allowed" ]))
        cwd = os.getcwd()
        self.wrdir = "%s/wrlinux" % cwd
        if self.wropts['quickstart']:
            return
        os.putenv('IPNET_USR_PREFIX', self.prefix())
        if self.p['rebuild']:
            self.build_setup_base()
        self.build_wrlinux(bopts)


    def start_qemu(self, num, force_bridge):
        self.p['tinderbox_vars']['board']         = '%s/qemu' % self.board
        self.p['tinderbox_vars']['port']          = 'WRLinux'
        self.p['tinderbox_vars']['port_version']  = '2.0'
        self.p['tinderbox_vars']['compiler']      = 'gcc'
        self.host.createNetwork(True)
        cwd = os.getcwd()
        os.chdir(self.wrproject(self.board))

        #If number of instances of this board type has been specified, then let it override
        if  self.wropts['qemunum']:
            num_instances =  int(self.wropts['qemunum'])
        else:
            num_instances = num

        for i in range(num_instances):
            address, _ = self.host.createHostAddress(self.host.umlswitch[0]['magic'])
            diskname   = "bootdisk%d" % i
            configfile = "config%d.sh" % i
            extsize = 25
            if self.wropts['pkgdbg']:
                extsize = 100
            if (shcmdvoid('./scripts/fakestart.sh ./host-cross/bin/genext2fs -z -b `du -sk export/dist | awk \'{print $1+1024*%d}\'` -d export/dist %s' % (extsize, diskname)) != 0) :
                raise BuildException(mailBody(None, [ 'Failed to build Wind River Linux QEMU root image in %s' %  os.getcwd() ]))

            if glob(diskname) == []:
                raise BuildException(mailBody(None, [ 'Could not find QEMU root image in %s' %  os.getcwd() ]))

            # Create a tap interface to use with QEMU
            qemu_tap_name, qemu_tap_id = self.host.createTunDev(0, provided_unique_id = self.host.umlswitch[0]['magic'], extra = '_%d%s' % (i,self.board))

            self.host.configTunDevice(qemu_tap_name, self.host.umlswitch[0]['name'] , 0)
            shcmdvoid('cp config.sh %s' % configfile)

            f = open(configfile,'a')
            f.write('TARGET_VIRT_BOOT_TYPE="%s"\n' % 'disk')
            f.write('TARGET_VIRT_ENET_TYPE="%s"\n' % 'tuntap')
            f.write('TARGET_TAP_DEV="%s"\n' % qemu_tap_name)
            f.write('TARGET_VIRT_IP="%s"\n' % address)
            f.write('TARGET_VIRT_GATEWAY=""\n')
            f.write('TARGET_TAP_ROOTACCESS="echo"\n')
            f.write('TARGET_VIRT_DISK="%s"\n' % os.path.join(self.wrproject(self.board), diskname))
            f.write('TARGET_QEMU_ENET_MODEL="auto"\n')
            if not self.wropts['qemudebug']:
                f.write('TARGET_QEMU_DEBUG_PORT="0"\n')

            if self.p['smp'] or not self.wropts['qemuconsole']:
                f.write('TARGET_QEMU_OPTS="')
                if self.p['smp']:
                    f.write('-smp 2 ')
                if not self.wropts['qemuconsole']:
                    f.write('-daemonize ')
                f.write('"\n')

            f.write('TARGET_VIRT_MAC="00:00:00:12:34:56"\n')
            if not self.wropts['nokqemu']:
                f.write('TARGET_QEMU_USE_KQEMU="yes"\n')
            f.close()
            tgtscript = "target%d.sh" % i
            f = open(tgtscript, 'w')
            f.write('TOPTS="-in %d" TARGET_CONFIG_FILE="%s" make $*' % (i, os.path.join(self.wrproject(self.board), configfile)))
            f.close()

            # add configuration entry
            self.host.conf.append("wrlinux_%s_%d = { 'type' : 'lkm', 'name' : '%s_%d', 'ip' : '%s', 'speed' : %s, 'os' : 'lkm', 'user' : 'root', 'passwd' : 'root', 'las-prefix' : '%s', 'login' : 'telnet', 'port' : 23" % (self.board, i, self.board, i, address, self.p['target-speed'], self.las_prefix()))
            self.host.conf.append("}\n")
            self.host.host_array.append('wrlinux_%s_%d' % (self.board,i))
            self.host.target_addresses.append(address)
            if self.wropts['qemuconsole']:
                shcmdvoid("xterm -T %s-%d -e sh %s start-target &" % (self.board,i, tgtscript))
            else:
                shcmdvoid("sh %s start-target > /dev/null 2>&1 < /dev/null" % tgtscript)
            self.wrlog("Starting QEMU target %d with address %s" % (i, address))
            self.started.append(tgtscript)

        os.chdir(cwd)
        #raw_input('press enter')
        return num - num_instances, True


    def ttyread(self, fd, log, matches, bufsize=100000):
        i = 0
        nl = 0
        cread = ""
        while i < 60:
            try:
                x = os.read(fd, bufsize)
                if len(x) > 0:
                    cread += x
                    if self.wropts['stdout']:
                        print x
                    for m in range(len(matches)):
                        if matches[m] in cread:
                            log += cread
                            return m
                    i = 0
                else:
                    time.sleep(5)
            except: #!!!fix
                time.sleep(5)
                i = i + 1
                nl = nl + 1
                if nl == 5:
                    os.write(fd, "\r")
                    nl = 0
        log += cread
        raise SetupException(mailBody(None, [log], 'boot error:'))


    def ttywrite(self, fd, cmd, slow=None):
        for c in cmd:
            os.write(fd,c)
            if self.wropts['stdout']:
                print c
            if slow:
                time.sleep(0.8)
            else:
                time.sleep(0.1)


    def bootmonitor(self, log, fd, bootfile, address, server, netmask, rootpath):
        self.wrlog('Connecting to the boot monitor')
        # get to the bootmonitor prompt
        self.ttywrite(fd, "\r")
        what = self.ttyread(fd, log, self.supported_prompts)
        if what == 0:
            # Linux still running...
            raise SetupException(mailBody(None, [log], 'boot error:'))

        if what == 1:
            # Configure YAMON monitor
            prompt = self.yamonprompt
            self.wrlog('Configuring for YAMON boot monitor')
            self.ttywrite(fd,'setenv bootfile %s\r' % bootfile)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'setenv bootserver %s\r' % server)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'setenv ipaddr %s\r' % address)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'setenv subnetmask %s\r' % netmask)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'load\r')

            # Let target load image and check if it was loaded OK.
            self.wrlog('Loading kernel image')
            time.sleep(60)
            what = self.ttyread(fd, log, ['Error', self.yamonprompt])
            if what == 0:
                raise SetupException(mailBody(None, [log], 'boot error:'))
            self.wrlog('Booting kernel')
            self.ttywrite(fd, 'go . root=/dev/nfs rw nfsroot=%s:%s \\\r' % (server,rootpath), slow = True)
            self.ttywrite(fd, 'ip=%s:%s::%s:%s:eth0:off\r' % (address,server,netmask,self.board), slow = True)

        if what == 2:
            # Configure U-boot monitor
            prompt = self.ubootprompt
            self.wrlog('Configuring for U-BOOT boot monitor')
            self.ttywrite(fd,'setenv serverip %s\r' % server)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'setenv bootfile %s\r' % bootfile)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'setenv ipaddr %s\r'   % address)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'setenv rootpath %s\r' % rootpath)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'setenv netmask %s\r'  % netmask)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'setenv hostname %s\r' % self.board)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'\r')
            self.ttyread(fd, log, prompt)
            self.wrlog('Booting target')
            self.ttywrite(fd,'boot\r')

        if what == 3:
            #Configure GRUB monitor
            prompt = self.grubprompt
            self.wrlog('Configuring for GRUB boot monitor')
            self.ttywrite(fd,'terminal --dumb serial\r', slow = True)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'ifconfig --address=%s  --mask=%s  --server=%s\r' % (address,netmask,server), slow = True)
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'root (nd)\r', slow = True)
            self.ttyread(fd, log, prompt)

            bootcmd =  'kernel /%s ' % bootfile
            bootcmd += 'root=/dev/nfs nfsroot=%s:%s ' % (server,rootpath)
            bootcmd += 'ip=%s:%s::%s:%s:eth0:off ' % (address, server, netmask, self.board)
            bootcmd += 'console=ttyS0,115200 '

            self.wrlog('GRUB boot line :: %s' % bootcmd)
            self.wrlog('Loading kernel image')
            self.ttywrite(fd,bootcmd + '\r', slow = True)
            self.ttyread(fd, log, prompt)
            self.wrlog('Booting target')
            self.ttywrite(fd,'\r')
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'boot\r', slow = True)

        if what == 4:
            # Configure RedBoot monitor
            # This sequence assumes that the netmask has been configured
            # properly in flash. RedBoot does not support setting netmask
            # in runtime
            prompt = self.redbootprompt
            self.wrlog('Configuring for RedBoot boot monitor')
            self.ttywrite(fd,'ip_address -l %s -h %s\r' % (address, server))
            self.ttyread(fd, log, prompt)
            self.ttywrite(fd,'\r')
            self.ttyread(fd, log, prompt)
            self.wrlog('Loading kernel image')
            self.wrlog('load -v -r -b %%{FREEMEMLO} %s\r' %  bootfile)
            self.ttywrite(fd,'load -v -r -b %%{FREEMEMLO} %s\r' %  bootfile)
            self.ttyread(fd, log, ['error', prompt])

            if what == 0:
                raise SetupException(mailBody(None, [log], 'boot error:'))

            self.ttyread(fd, log, prompt)
            self.wrlog('Booting target')
            bootcmd  = 'exec -c "console=ttyS0,115200 root=/dev/nfs '
            bootcmd += 'nfsroot=%s:%s ' % (server,rootpath)
            bootcmd += 'ip=%s::%s:%s:%s:eth0:off"' % (address, server, netmask, self.board)
            self.ttywrite(fd,bootcmd + '\r')

        what = self.ttyread(fd, log, ['Welcome to Wind River Linux',self.linuxprompt,prompt,'panic'])
        if what > 1:
            raise SetupException(mailBody(None, [log], 'boot error:'))
        self.wrlog('Target has now booted properly')


    def start_target(self, num, force_bridge):
        self.p['tinderbox_vars']['board']         = self.board
        self.p['tinderbox_vars']['port']          = 'WRLinux'
        self.p['tinderbox_vars']['port_version']  = '2.0'
        self.p['tinderbox_vars']['compiler']      = 'gcc'
        sttys = [ '-hupcl', 'ignbrk', '-icrnl', '-ixon', '-opost', '-onlcr',
                  '-isig', '-icanon', '-iexten', '-echo', '-echoe', '-echok',
                  '-echoctl', '-echoke', 'time=5', 'cols=200' ]
        log = ""

        # Setup serial terminal
        sudo("chmod a+rw %s" % self.wropts['tty'])
        for stty in sttys:
            sudo("stty --file=%s %s" % (self.wropts['tty'], " ".join(stty.split('='))))
        for stty in self.wropts['stty']:
            sudo("stty --file=%s %s" % (self.wropts['tty'], " ".join(stty.split('='))))
        self.fd = os.open(self.wropts['tty'], os.O_RDWR | os.O_NONBLOCK | os.O_NOCTTY)

        # Prepare boot files
        cwd = os.getcwd()
        os.chdir('%s/export' % self.wrproject(self.board))
        bootfile = '%s-default_kernel_image-WR2.0zz_standard' % self.board
        distfile = '%s/%s-glibc_small-standard-dist.tar.bz2' % (os.getcwd(), self.board)
        rootdir  = '%s/%s' % (self.exportdir,self.board)
        rcsfile  = '%s/dist/etc/rcS.d/Stestengine' % os.getcwd()
        sockrun  = '%s/dist/usr/lastools/sbin/sockrun' % os.getcwd()

        if glob(bootfile) == []:
            raise BuildException(mailBody(None, [ 'Could not find WRLinux boot file in %s' %  os.getcwd() ]))
        if glob(distfile) == []:
            raise BuildException(mailBody(None, [ 'Could not find WRLinux file system image file in %s' % os.getcwd() ]))

        self.wrlog('Setting up boot image and root file system')
        # Copy boot image to tftp boot directory and rename it to board name
        sudo('cp %s %s/%s' % (bootfile, self.tftpdir, self.board))
        # Setup root file system
        shcmdvoid('rm -rf %s' % rootdir)
        shcmdvoid('mkdir %s' % rootdir)
        os.chdir(rootdir)
        sudo('tar xfjp %s' % distfile)
        sudo('cp %s etc/rcS.d/' % rcsfile)
        sudo('chmod a+x etc/rcS.d/Stestengine')
        sudo('cp %s usr/lastools/sbin' % sockrun)
        sudo('mv etc/bashrc etc/bashrc.x')
        os.chdir(cwd)

        # Setup network connections
        self.host.createNetwork(True)
        address, _ = self.host.createHostAddress(self.host.umlswitch[0]['magic'])
        br_address = self.host.umlswitch[0]['address']
        netmask    = self.host.getHostNetmask()

        # Bridge me in.
        self.host.bridgeDevice(self.host.umlswitch[0]['name'], self.wropts['interface'])

        # Connect to boot monitor and boot
        self.bootmonitor(log, self.fd, self.board, address, br_address, netmask, rootdir)
        self.wrlog("Started WRLINUX target %s with address %s" % (self.board, address))

        # add configuration entry
        self.host.conf.append("wrlinux_%s = { 'type' : 'lkm', 'name' : '%s', 'ip' : '%s', 'speed' : %s, 'os' : 'lkm', 'user' : 'root', 'passwd' : 'root', 'las-prefix' : '%s', 'login' : 'telnet', 'port' : 23" % (self.board, self.board, address, self.p['target-speed'], self.las_prefix()))
        self.host.conf.append("}\n")
        self.host.host_array.append('wrlinux_%s' % self.board)
        self.host.target_addresses.append(address)
        os.chdir(cwd)
        return num - 1, True


    def start(self, num, force_bridge):
        if self.wropts['qemu']:
            return self.start_qemu(num, force_bridge)
        else:
            return self.start_target(num, force_bridge)

    def addLogfiles(self, mobj):
        pass
    def terminalError(self, mobj):
        pass

    def cleanup(self):
        cwd = os.getcwd()
        if self.wropts['qemu']:
            for scr in self.started:
                try:
                    os.chdir(self.wrproject(self.board))
                    shcmdvoid("sh %s stop-target" % scr)
                except:
                    pass
                os.chdir(cwd)
        else:
            self.ttywrite(self.fd,'\rreboot\r')
            time.sleep(15)


class vxworks_target(build):
    def __init__(self, host, board, log, p):
        super(vxworks_target, self).__init__(host, log, p)
        import time
        self.vx = self.p['vxworks'][board]
        self.vx['tool'] = self.p['toolchain']
        self.taps = []
        if not self.vx['tool']:
            if self.vx['board'] == 'vxsim_linux':
                self.vx['tool'] = 'gnu'
            else:
                self.vx['tool'] = 'sfgnu'
        _, wrenv_prefix = get_vxworks_env(self.p['vxworks'][board]['path'])
        self.globalwrenv = wrenv_prefix + ' LM_LICENSE_FILE=27000@ala-lic4.wrs.com '
        self.vlmConns = []

    def get_ports(self):
        return {'vxworks': self.vx['vc']}

    def doLogFile(self, log, vxname, fd, address):
        if self.p['attach'] and self.vx['console']:
            logfile = vxname + "_".join(address.split(".")) + ".txt.gz"
            fdlog = fdLogFile(logfile, fd, log, self.p['verbose'])
            fdlog.start()
            self.logfiles.append(fdlog)
        else:
            os.close(fd)

    def vxread(self, fd, log, matches):
        i = 0
        nl = 0
        cread = ""
        while i < 60:
            try:
                x = os.read(fd, 10000)
                if len(x) > 0:
                    cread += x
                    if self.vx['stdout']:
                        print x
                    for m in range(len(matches)):
                        if matches[m] in cread:
                            log += cread
                            return m
                    i = 0
                else:
                    time.sleep(5)
            except:
                time.sleep(5)
                i = i + 1
                nl = nl + 1
                if nl == 5:
                    os.write(fd, "\r")
                    nl = 0
        log += cread
        raise SetupException(mailBody(None, [log], 'boot error:'))


    def bootprompt(self, log, fd, vxname, address, br_address):
        # get to the bootmonitor prompt
        os.write(fd, "\r")
        what = self.vxread(fd, log, ['[VxWorks Boot]:', '->', '[vxWorks]#'])
        if what > 0:
            os.write(fd, "reboot\r")
            what = self.vxread(fd, log, ['[VxWorks Boot]:', 'Press any key to stop auto-boot'])
            if what == 1:
                os.write(fd, '\r')
                what = self.vxread(fd, log, ['[VxWorks Boot]:'])

        # I'm at the boot prompt
        # Create the boot command.
        if self.vx['ftp']:
            # boot device and tftp file target
            bootcmd = "%s:%s f=0x04 u=%s pw=%s " % (self.vx['bootdev'], self.vx['tftpfile'], self.vx['ftp']['user'], self.vx['ftp']['passwd'])
        else:
            # boot device and tftp file target
            bootcmd = "%s:%s f=0x84 " % (self.vx['bootdev'], self.vx['tftpfile'])

        # Own configuration
        bootcmd += "e=%s:ffffff00 " % address

        # TFTP server
        bootcmd += "h=%s " % br_address

        # Newline
        bootcmd += "\r"
        os.write(fd, bootcmd)
        self.log.info('Target %s booting using boot command "%s"' % (vxname, bootcmd))


    def start(self, num, force_bridge):
        nets = self.p['networks']
        if 'ipnet2' in self.p['vc']:
            stack_type = 'ipnet'
        elif 'rtnet' in self.p['vc']:
            stack_type = 'rtnet'
        else:
            stack_type = 'iplite'

        # simics boards, see runtestsuite_conf.py to see what simics is supported
        if self.vx['board'] in simicsTargets:
            return self.startSimicsTarget(num, force_bridge)
        elif self.vx['board'] in vlmTargets:
            return self.startVlmTarget(num, force_bridge)
        elif self.vx['board'] != 'vxsim_linux':
            sttys = [ '-hupcl', 'ignbrk', '-icrnl', '-ixon', '-opost', '-onlcr',
                      '-isig', '-icanon', '-iexten', '-echo', '-echoe', '-echok',
                      '-echoctl', '-echoke', 'time=5' ]
            self.host.createNetwork(True)
            vxname = "vx%s0" % self.vx['board']
            address, _ = self.host.createHostAddress(self.host.umlswitch[0]['magic'])
            br_address = self.host.umlswitch[0]['address']
            sudo("chmod a+rw %s" % self.vx['tty'])
            for stty in sttys:
                sudo("stty --file=%s %s" % (self.vx['tty'], " ".join(stty.split('='))))
            for stty in self.vx['stty']:
                sudo("stty --file=%s %s" % (self.vx['tty'], " ".join(stty.split('='))))

            # Bridge me in.
            self.host.bridgeDevice(self.host.umlswitch[0]['name'], self.vx['interface'])
            log = ""
            if self.vx.get('power1'):
                print shcmd("/usr/local/bin/pdu1.py reboot " + self.vx['power1']).read()
            if self.vx.get('power2'):
                print shcmd("/usr/local/bin/pdu2.py reboot " + self.vx['power2']).read()
            if self.vx.get('power3'):
                print shcmd("/usr/local/bin/pdu3.py reboot " + self.vx['power3']).read()
            if self.vx.get('power6'):
                print shcmd("/usr/local/bin/pdu6.py reboot " + self.vx['power6']).read()
            time.sleep(60)
            fd = os.open(self.vx['tty'], os.O_RDWR | os.O_NONBLOCK | os.O_NOCTTY)
            self.bootprompt(log, fd, vxname, address, br_address)

            # Let the configuration complete
            if self.vx['console']:
                self.log.info('Booting in console mode')
                accepted_results = [ '[VxWorks Boot]:', '->', '[vxWorks]#' ]
                for i in range(2):
                    what = self.vxread(fd, log, accepted_results)
                    if what == 0:
                        if i != 0:
                            raise SetupException(mailBody(None, [log], 'boot error:'))
                        self.bootprompt(log, fd, vxname, address, br_address)
                    else:
                        self.doLogFile(log, vxname, fd, address)
                        time.sleep(40)
                        break
            else:
                self.log.info('Booting in debug/single channel mode')
                accepted_results = ['[VxWorks Boot]:', 'Starting at']
                for i in range(2):
                    what = self.vxread(fd, log, accepted_results)
                    if what == 0:
                        if i != 0:
                            raise SetupException(mailBody(None, [log], 'boot error:'))
                        self.bootprompt(log, fd, vxname, address, br_address)
                    else:
                        self.doLogFile(log, vxname, fd, address)
                        time.sleep(60)
                        break

            self.host.target_addresses.append(address)
            self.host.conf.append("%s= {'type': '%s', 'name': '%s', 'ip': '%s', 'os': '%s', 'speed': %s, 'port': 2323, 'user':'ftp', 'passwd':'interpeak' }\n" % (vxname, stack_type, address, address, 'vxworks', self.p['target-speed']))
            self.host.host_array.append("%s" % vxname)
            self.log.info('Target started using IP address %s (%s)' % (address, vxname))
            return num - 1, True
        else: # vxsim
            # cleanup leftovers
            self.cleanShareMem()
            self.cleanSemaphore()
            
            sudo("pkill vxsimnetd")
            sudo("pkill -f rs_vxsim")
            time.sleep(2)
            sudo("pkill -9 vxsimnetd")
            sudo("pkill -9 -f rs_vxsim")
            sudo('pkill -9 wtxregd.ex')
            time.sleep(2)
            sudo('rm -f /var/lock/subsys/wtxregd')

#            sudovoid(self.globalwrenv + 'wtxregd.ex -d /tmp/&')
            time.sleep(4)

            # create unconfigured bridge to get unique magic
            if force_bridge:
                self.host.createNetwork(True)
                net_unique_id = self.host.umlswitch[0]['magic']
            else:
                _, net_unique_id = self.host.createTunDev(0)

            # start the vxsimnet daemon
            vxworks_simnet_config = """
            SUBNET_START default {
                SUBNET_EXTERNAL     = yes;
                SUBNET_EXTPROMISC   = yes;
                SUBNET_ADDRESS      = "%s%d%s0";
                SUBNET_MACPREFIX    = "7c:7a";
                SUBNET_MAXBUFFERS   = 1000;
            };
            """ % (self.host.subnet, net_unique_id, self.host.address_separator)
            shcmdvoid("echo '%s' > simnet.cfg" % vxworks_simnet_config)

            # Adding support for multiple interfaces in simlinux
            for i in range(1,nets):
                netid = net_unique_id - i
                if netid > 0:
                    vxworks_simnet_extra = """
                    SUBNET_START subnet%s {
                        SUBNET_ADDRESS      = "%s%d%s0";
                        SUBNET_EXTERNAL     = no;
                        SUBNET_MAXBUFFERS   = 1000;
                    };
                    """ % (netid, self.host.subnet, netid, self.host.address_separator)
                    shcmdvoid("echo '%s' >> simnet.cfg" % vxworks_simnet_extra)

            sudovoid(self.globalwrenv + "vxsimnetd -f simnet.cfg -force  > vxsimnet_log 2>&1 &")
            time.sleep(4)

            if ':' in self.host.address_separator:
                sudovoid(self.globalwrenv + "sudo ifconfig tap0 inet6 add %s%d%s1" % (self.host.subnet, net_unique_id, self.host.address_separator))
                sudovoid(self.globalwrenv + "sudo ip route add %s%d%s0/96 dev tap0" % (self.host.subnet, net_unique_id, self.host.address_separator))
            else:
                sudovoid(self.globalwrenv + "sudo ifconfig tap0 add %s%d%s1" % (self.host.subnet, net_unique_id, self.host.address_separator))
                sudovoid(self.globalwrenv + "sudo ip route add %s%d%s0 dev tap0" % (self.host.subnet, net_unique_id, self.host.address_separator))

            # Let it start up in peace.
            time.sleep(4)

            for a in range(num):
                address, _ = self.host.createHostAddress(net_unique_id)
                binname = "vxsim%d" % a
                bindir = binname
                shcmdvoid('rm -rf %s' % bindir)
                shcmdvoid('mkdir %s' % bindir)
                cwd = os.getcwd()
                os.chdir(bindir)

                # Adding support for multiple interfaces in simlinux
                network_init = "-d simnet -e %s" % address
                if nets > 1:
                    network_init += " -ni \""
                    for i in range (1, nets):
                        extra_net_id = net_unique_id - i
                        if extra_net_id > 0:
                            extra_address, _ = self.host.createHostAddress(extra_net_id)
                            network_init += "simnet%d=%s" % (i, extra_address)
                            if i < nets-1:
                                network_init += ";"
                            else:
                                network_init += "\""

                if ':' in self.host.address_separator:
                    vxsim_config = "cmd" + "\nifconfig eth0 inet6 add %s" % address
                else:
                    vxsim_config = "cmd" + "\nifconfig eth0 inet add %s" % address

                shcmdvoid("echo '%s' > startup.cfg" % vxsim_config)
                self.binary_name = '%s/%s_vip/default/vxWorks' % (cwd, self.vx['board'])
                if not os.path.exists(self.binary_name):
                    print 'ERROR: binary file %s not existed' % self.binary_name
                    exit(1)
                sudovoid(self.globalwrenv + "vxsim %s -memsize 800M -s startup.cfg -f %s -p %s -tn rs_vxsim%s -lc -l vxsimlog 2>&1 > /dev/null &" % (network_init, self.binary_name, a,a))

                time.sleep(4)
                # Add debugger support.
                # sudovoid(self.globalwrenv + "tgtsvr -n rs_vxsim%s -B wdbpipe -p %s -RW -Bt 3 -A rs_vxsim%s rs_vxsim%s 2>&1 > /dev/null &" % (a,a,a,a))
                os.chdir(cwd)
                if self.p['attach']:
                    logfile = "_".join(bindir.split(".")) + ".txt.gz"
                    self.logfiles.append(zipLogFile(logfile, bindir + "/vxsimlog"))

                self.host.target_addresses.append(address)
                port = 23 if 'RTNET' in self.p.get('vxconf', []) else 2323
                self.host.conf.append("%s= {'type': '%s', 'name': '%s', 'ip': '%s', 'os': '%s', 'speed': %s, 'port': %s, 'user':'ftp', 'passwd':'interpeak'  }\n" % (binname, stack_type, address, address, 'vxworks', self.p['target-speed'], port))
                self.host.host_array.append(binname)
                self.log.info('Target started using IP address %s (%s)' % (address, binname))

            if force_bridge:
                self.host.flushDevice('tap0')
                self.host.bridgeDevice(self.host.umlswitch[0]['name'], 'tap0')
                
            self.__waitTargetReady(self.host, timeout=90, interval=1)
            
            if self.p['helix']:
                print('=== force_bridge:%s' % force_bridge)
                self.host.conf, self.host.target_addresses = self.startHelixTarget(self.vx['helixhost'], self.host.umlswitch[0]['name'], '%s%d' % (self.host.subnet, net_unique_id), self.host.conf, self.host.target_addresses)
            
            # if self.vx['directbsp'] in directTargets:
            if self.p['direct']:
                print('=== begin to boot direct connected board')
                self.host.conf, self.host.target_addresses = self.startDirectTarget(self.vx['directhost'], self.host.umlswitch[0]['name'], '%s%d' % (self.host.subnet, net_unique_id), self.host.conf, self.host.target_addresses)

            return 0, False


    def startHelixTarget(self, helixHost, bridge, subnet, hostConfs, hostTargetAddresses):
        def getSubnet(ipAddr):
            return '.'.join(ipAddr.split('.')[:-1])
            
        vmIp = helixHosts[helixHost]['vm'][0]
        if getSubnet(vmIp) != subnet:
            raise SetupException('vm ip %s not match current subnet %s' % (vmIp, subnet))
        
        helixBsp = self.vx['helixbsp']
        target = helixHosts[helixHost]['target'][0]
        directEthernet = helixHosts[helixHost]['direct_ethernet'][0]
        tftpServer = helixHosts[helixHost]['tftp_server']
        tftpClient = helixHosts[helixHost]['tftp_client']
        
        if helixEnableImageCopy:
            tftpPath = '%s/%s' % (helixHosts[helixHost]['tftp_path'], helixBuild[helixBsp]['image'])
            if helixBuild[helixBsp]['dtb'] is not None:
                dtbPath  = '%s/%s' % (helixHosts[helixHost]['tftp_path'], helixBuild[helixBsp]['dtb'])
            else:
                dtbPath  = None
        else:
            # try to use the current directory
            findPath = os.getcwd()
            tftpPath, dtbPath = self.__findHelixImage(findPath, helixBuild[helixBsp]['image'], helixBuild[helixBsp]['dtb'])
            if not tftpPath:
                raise SetupException('image %s not found under %s' % (helixBuild[helixBsp]['image'], findPath))
            
        # add 24bits netmask to fix image load issue on pek-kong-04
        sudovoid('sudo ifconfig %s %s/24 up' % (directEthernet, tftpServer))
        # Helix static config will go to VM console directly, however, there is no osPrompt(-> ) shown up
        # at the VM console if the user management turns on
        oldOsInitDone = vlmTargetConfigs[target]['osInitDone']
        if helixBuild[helixBsp]['dynamic']:
            doneFlag = 'network-kong-dynamic-config-done'
            self.__updateBoardOsInitDone(target, doneFlag)
        else:
            if 'vxconf' in self.p and 'USER_MANAGEMENT' in self.p['vxconf']:
                self.__updateBoardOsInitDone(target, 'login:')
                    
        ipAddr, tgt = loadImageToTarget(target, tftpServer, tftpClient, tftpPath, dtbPath)

        if helixBuild[helixBsp]['dynamic']:
            self.__updateBoardOsInitDone(target, oldOsInitDone)
        else:
            if 'vxconf' in self.p and 'USER_MANAGEMENT' in self.p['vxconf']:
                self.__updateBoardOsInitDone(target, oldOsInitDone)

        sudovoid('sudo brctl addif %s %s' % (bridge, directEthernet))
        sudovoid('sudo ifconfig %s down' % directEthernet)
        sudovoid('sudo ifconfig %s 0.0.0.0 up' % directEthernet)

        if self.p['name'] in ('USERAUTH_LDAP', 'QOS', 'MCP', 'IPNET'):
            print('waiting 360 seconds')
            time.sleep(360)
            
        # replace 1st vxsim with vm0
        newHostConfs, newHostTargetAddresses = [], []
        for line in hostConfs:
            if line.startswith('vxsim0'):
                line = line.replace('%s.2' % subnet, vmIp)
            newHostConfs.append(line)
        for line in hostTargetAddresses:
            if line.startswith('%s.2' % subnet):
                line = line.replace('%s.2' % subnet, vmIp)
            newHostTargetAddresses.append(line)
                    
        return newHostConfs, newHostTargetAddresses


    def startDirectTarget(self, directHost, bridge, subnet, hostConfs, hostTargetAddresses):
        def getSubnet(ipAddr):
            return '.'.join(ipAddr.split('.')[:-1])

        boardIp = directHosts[directHost]['addr'][0]
        directBsp = self.vx['directbsp']
        target = directHosts[directHost]['target'][0]
        directEthernet = directHosts[directHost]['direct_ethernet'][0]

        tftpPath = directHosts[directHost]['tftp_path'] + '/default/' + directTargets[directBsp]['image']
        dtbPath = directHosts[directHost]['tftp_path'] + '/default/' + directTargets[directBsp]['dtb']

        oldOsInitDone = vlmTargetConfigs[target]['osInitDone']
        if 'vxconf' in self.p and 'USER_MANAGEMENT' in self.p['vxconf']:
            self.__updateBoardOsInitDone(target, 'login:')

        sudovoid('sudo brctl addif %s %s' % (bridge, directEthernet))
        sudovoid('sudo ifconfig %s down' % directEthernet)
        sudovoid('sudo ifconfig %s 0.0.0.0 up' % directEthernet)

        # tftpboot with bridge IP and vxsim0 ip to direct target
        tftpServer = "%s.1" % subnet
        tftpClient = boardIp
        ipAddr, tgt = loadImageToTarget(target, tftpServer, tftpClient, tftpPath, dtbPath)
        address = tftpClient
        host_type = 'ipnet'
        port = 2323
        # update host config info
        binname = 'vlm%s' % target
        self.host.target_addresses.insert(0, address)
        self.host.vlm_targets.append(tgt)
        self.host.conf.insert(0, "%s= {'type': '%s', 'name': '%s', 'ip': '%s', 'os': '%s', 'speed': %s, 'port': %s, 'user':'ftp', 'passwd':'interpeak' }\n" \
                             % (binname, host_type, binname, address, 'vxworks', self.p['target-speed'], port))
        self.host.host_array.insert(0, binname)
        self.log.info('Target started using IP address %s (%s)' % (address, binname))

        return self.host.conf, self.host.target_addresses


    def startSimicsTarget(self, num, force_bridge):
            if not self.p['codecoverage']:
                simicsScript = self.p['vxworks'][self.vx['board']]['path'] + \
                               '/vxworks-7/pkgs/net/ipnet/coreip/src/ipcom/util/scripts/' + \
                               simicsTargets[self.vx['board']]['script'] 
            else:
                if 'cov-script' in simicsTargets[self.vx['board']]:
                    simicsScript = self.p['vxworks'][self.vx['board']]['path'] + \
                                   '/vxworks-7/pkgs/net/ipnet/coreip/src/ipcom/util/scripts/' + \
                                   simicsTargets[self.vx['board']]['cov-script']
                else:
                    raise SetupException('simics %s code coverage not supported' % self.vx['board'])
                
            # create unconfigured bridge to get unique magic
            if force_bridge:
                self.host.createNetwork(True)
                net_unique_id = self.host.umlswitch[0]['magic']
            else:
                _, net_unique_id = self.host.createTunDev(0)

            # start the simics
            print '--- cwd=', os.getcwd()            
            if not self.p['codecoverage']:
                print shcmd('sudo tunctl -u %s -t tap0' % self.host.user).read()
                
                if ':' in self.host.address_separator:
                    sudovoid("sudo ifconfig tap0 inet6 %s%d%s1" % (self.host.subnet, net_unique_id, self.host.address_separator))
                    sudovoid("sudo ip route add %s%d%s0/96 dev tap0" % (self.host.subnet, net_unique_id, self.host.address_separator))
                else:
                    sudovoid("sudo ifconfig tap0 %s%d%s1 netmask 255.255.255.0 up" % (self.host.subnet, net_unique_id, self.host.address_separator))
                    sudovoid("sudo ip route add %s%d%s0 dev tap0" % (self.host.subnet, net_unique_id, self.host.address_separator))
    
                # wait simics to start up in peace.
                # change simics ip address
                self.__copySimicsScript(simicsScript, self.p['vxworks'][self.vx['board']]['simicspath'])
                runningSimicsScript = self.p['vxworks'][self.vx['board']]['simicspath'] + '/' \
                                      + simicsTargets[self.vx['board']]['script']
                print '--- ', runningSimicsScript

                simicsCmdTpl = """{simicsPath}/bin/simics -license-file 27000@churchill.wrs.com \
                -no-gui \
                -no-win \
                -e '$ip_prefix={ipPrefix}' \
                -e '$board_num={boardNum}' \
                -e '$name=my_simics' \
                -e '$logFolder={logPath}'  \
                -e disable-reverse-execution \
                -e disable-debugger \
                -e 'delete-bookmark -all' \
                -e '$image_path={imagePath}/uVxWorks' \
                -e '$image_directory={imagePath}'  \
                -e 'telnet-frontend -non-interactive {consolePort}' \
                -e '$mac_address = "00:7f:f7:f9:f3:37"' \
                -e '$kernel_image={imagePath}/uVxWorks' \
                -x {simicsPath}/{script} \
                -e '$system.console.switch-to-telnet-console 2323' \
                -e enable-real-time-mode \
                -e continue 2>&1 > /dev/null &"""
                
                simicsCmd = simicsCmdTpl.format(ipPrefix='%s%d%s' % (self.host.subnet, net_unique_id, self.host.address_separator),
                                                boardNum=self.p.get('targets', 6),
                                                simicsPath=self.p['vxworks'][self.vx['board']]['simicspath'], 
                                                imagePath=self.p['vxworks'][self.vx['board']]['imagepath'],
                                                consolePort=simicsTargets[self.vx['board']]['console-port'],
                                                script=simicsTargets[self.vx['board']]['script'],
                                                logPath='./')
                shcmdvoid(simicsCmd)
                time.sleep(30)
            else:
                for i in xrange(self.p.get('targets', 6)):
                    boardIp = '%s%d%s%d' % (self.host.subnet, net_unique_id, self.host.address_separator, i+2)
                    tapName = 'tap%s' % i
                    self.taps.append(tapName)
                    print shcmd('sudo tunctl -u %s -t %s' % (self.host.user, tapName)).read()
                    
                    # first use fake ip address and ip net address to set up N simics targets
                    if ':' in self.host.address_separator:
                        sudovoid("sudo ifconfig %s inet6 %s%d%s1" % (tapName, self.host.subnet, net_unique_id-i, self.host.address_separator))
                        sudovoid("sudo ip route add %s%d%s0/96 dev %s" % (self.host.subnet, net_unique_id-i, self.host.address_separator, tapName))
                    else:
                        sudovoid("sudo ifconfig %s %s%d%s1 netmask 255.255.255.0 up" % (tapName, self.host.subnet, net_unique_id-i, self.host.address_separator))
                        sudovoid("sudo ip route add %s%d%s0 dev %s" % (self.host.subnet, net_unique_id-i, self.host.address_separator, tapName))
        
                    # wait simics to start up in peace.
                    # change simics ip address
                    self.__copySimicsScript(simicsScript, self.p['vxworks'][self.vx['board']]['simicspath'])
                    runningSimicsScript = self.p['vxworks'][self.vx['board']]['simicspath'] + '/' \
                                          + simicsTargets[self.vx['board']]['script']
                    print '--- ', runningSimicsScript
                    
                    # secondly use correct boardIp to set up simics console after booting up              
                    simicsCmdTpl = """{simicsPath}/bin/simics -stall -license-file 27000@churchill.wrs.com \
                    -no-gui \
                    -no-win \
                    -e '$board_ip={boardIp}' \
                    -e '$board_num={boardNum}' \
                    -e '$tap_name={tapName}' \
                    -e '$target=t2080qds' \
                    -e '$script=targets/qoriq-t2/t2080qds-vxworks-7.simics' \
                    -e '$kernel_image='{imagePath}/uVxWorks \
                    -e '$dtb_image='{imagePath}/t2080qds.dtb \
                    -e '$symbol='{imagePath}/vxWorks \
                    -e '$test_name={testName}' \
                    -e '$pathmap_src='{srcDir} \
                    -e '$pathmap_dst='{dstDir} \
                    -e '$simics_path='{simicsPath} \
                    -e 'telnet-frontend -non-interactive {consolePort}' \
                    -x {simicsPath}/{script} 2>&1 > /buildarea3/lchen3/simics5-workspace/cov.log &"""
        
                    simicsCmd = simicsCmdTpl.format(boardIp=boardIp,
                                                    boardNum=i,
                                                    tapName=tapName,
                                                    simicsPath=self.p['vxworks'][self.vx['board']]['simicspath'], 
                                                    imagePath=self.p['vxworks'][self.vx['board']]['imagepath'],
                                                    testName='t2080qds-cov',
                                                    srcDir='/buildarea3/lchen3/vxworks/vxworks-7/pkgs',
                                                    dstDir='/buildarea3/lchen3/vxworks/vxworks-7/pkgs',
                                                    consolePort=simicsTargets[self.vx['board']]['console-port'] + i,
                                                    script=simicsTargets[self.vx['board']]['cov-script'],
                                                   )
                
                    shcmdvoid(simicsCmd)
                    
                time.sleep(30)

            # update host config info
            for i in xrange(num):
                binname = '%s%d' % (self.vx['board'], i)
                address, _ = self.host.createHostAddress(net_unique_id)
                self.host.target_addresses.append(address)
                self.host.conf.append("%s= {'type': '%s', 'name': '%s', 'ip': '%s', 'os': '%s', 'speed': %s, 'port': 2323, 'user':'ftp', 'passwd':'interpeak'  }\n" % (binname, 'ipnet', binname, address, 'vxworks', self.p['target-speed']))
                self.host.host_array.append(binname)
                self.log.info('Target started using IP address %s (%s)' % (address, binname))

            if force_bridge:
                for tap in self.taps:
                    self.host.flushDevice(tap)
                    self.host.bridgeDevice(self.host.umlswitch[0]['name'], tap)

            # sleep for a while to wait for all simics targets to bring up and set up ethernet ip
            self.__waitTargetReady(self.host)
            
            return 0, False                


    def startVlmTarget(self, num, force_bridge):
        # not support uml target so far
        # set up target and load image
        # make the target accessiable
        # create hosts.py file
        from vlmTarget import VLMException, vlmTargetConfigs, loadImageToTarget
        
        if num != len(self.p.get('vlmtargets')):
            raise CommandlineArgumentException('command line arguments targets not match vlmtargets')
        
        for i in xrange(num):
            target_id = self.p.get('vlmtargets')[i]
            if target_id not in vlmTargetConfigs:
                raise CommandlineArgumentException('command line arguments %s in vlmtargets not supported' % target_id)
            
            board_name = self.p.get('vxworks').keys()[0]
            imagePath = tftp_path + '/t%d/' % i + vlmTargets[board_name]['image']
            if vlmTargets[board_name]['dtb'] is not None:
                dtbPath = tftp_path + '/t%d/' % i + vlmTargets[board_name]['dtb']
            else:
                dtbPath = None
            
            try:
                if self.p['name'] == 'RTNET':
                    # pinging target cannot work until after pinging from target to host
                    address, vlm_target = loadImageToTarget(target_id, tftp_server, None, imagePath, dtbPath)
                    runPingFromTarget(vlm_target, 'ping4', tftp_server)
                elif self.p['name'] == 'RTNET_RTP':
                    address, vlm_target = loadImageToTarget(target_id, tftp_server, None, imagePath, dtbPath)
                    if self.p['vxworks'].keys()[0] == 'fsl_imx6':
                        # work around to avoid the error "memPartAlloc: block too big 512 bytes (0x100 aligned) in"
                        print 'work around for %s' % self.p['vxworks'].keys()[0]
                        vlm_target.sendAndExpect('putenv("HEAP_INITIAL_SIZE=0x1000000")', '-> ', timeout=20)
                        vlm_target.sendAndExpect('putenv("HEAP_MAX_SIZE=0x10000000")', '-> ', timeout=20)
                    cmd = 'cmd rtp exec -i -e RTNET_FILE=/romfs/%srtp.json /romfs/%s' % (target_id, os.path.basename(self.p['rtpvxe'][0]))
                    expected = "Process .*?%s' .*? launched\." % os.path.basename(self.p['rtpvxe'][0])
                    vlm_target.sendAndExpect(cmd, expected, timeout=20)
                    runPingFromTarget(vlm_target, 'ping', tftp_server, prompt='RTNET> ', interruptCmd='enter')
                else:
                    raise CommandlineArgumentException('RTNET or RTNET_RTP only supports VLM targets')
                self.vlmConns.append(vlm_target)
            except VLMException, inst:
                raise SetupException('%s exception raised: %s' % (inst.__class__.__name__, inst))
            
            if self.p['name'] == 'RTNET_RTP':
                # RTNet rtp needs the target console for iptestengine.py
                host_type = 'rtnet'
                port = 2000 + int(vlm_target.Terminal_Server_Port)
                address = vlm_target.Terminal_Server
            elif self.p['name'] == 'RTNET':
                host_type = 'rtnet'
                port = 23
            else:
                host_type = 'ipnet'
                port = 2323
            
            # update host config info
            binname = 'vlm%s' % target_id
            self.host.target_addresses.append(address)
            self.host.vlm_targets.append(vlm_target)            
            self.host.conf.append("%s= {'type': '%s', 'name': '%s', 'ip': '%s', 'os': '%s', 'speed': %s, 'port': %s  }\n" \
                                  % (binname, host_type, binname, address, 'vxworks', self.p['target-speed'], port))            
            self.host.host_array.append(binname)
            self.log.info('Target started using IP address %s (%s)' % (address, binname))

        return 0, False                


    def __updateBoardOsInitDone(self, board, newOsInitDone):
        oldOsInitDone = vlmTargetConfigs[board]['osInitDone']
        vlmTargetConfigs[board]['osInitDone'] = newOsInitDone
        newOsInitDone = vlmTargetConfigs[board]['osInitDone']
        print('old os init done=%s, new os init done=%s' % (oldOsInitDone, newOsInitDone))
            
            
    def __waitTargetReady(self, host, timeout=600, interval=5):
        start_time = time.time()
        i = 0
        board1 = host.target_addresses[0]
        
        print 'waiting target ready ...'
        while True:
            if (time.time() - start_time) >= timeout:
                raise ConnectivityException('%s seconds timeout due to network connectivity error:' % timeout)
                break
            if not host.ping_one(board1):
                print '.',
                time.sleep(interval)
                i += 1
            else:
                print 'waited target ready for %s seconds' % round(time.time() - start_time, 2)
                break

    def __copySimicsScript(self, simicsScript, simicsPath):
        import shutil
        shutil.copy(simicsScript, simicsPath)

    def __findHelixImage(self, thePath, imageFile, dtbFile):
        print(thePath, imageFile, dtbFile)
        imageFound = ''
        dtbFound = ''
        maxImageSize = 0
        for parentDir, subDirs, files in os.walk(thePath, topdown=True):
            for f in files:
                if f == imageFile:
                    filePath = os.path.join(parentDir, f)
                    if os.path.getsize(filePath) > maxImageSize:
                        imageFound = filePath
                        maxImageSize = os.path.getsize(filePath)
        if imageFound:
            if dtbFile is not None:
                dtbFilePath = os.path.join(os.path.dirname(imageFound), dtbFile)
                if os.path.exists(dtbFilePath):
                    dtbFound = dtbFilePath
                else:
                    raise Exception('%s not found at %s' % (dtbFile, thePath))
            else:
                dtbFound = None
        else:
            imageFound = ''
        return imageFound, dtbFound
        
        
    def addLogfiles(self, mobj):
        for f in self.logfiles:
            f.add(mobj)

    def terminalError(self, mobj):
        pass

    def cleanShareMem(self):
        shmids = []
        lines = filter(lambda x: x.startswith('0x'), shcmd('ipcs -m').readlines())
        for line in lines:
            fields = filter(lambda x: x.strip() != '', line.split(' '))
            if fields[5] == '0':
                shmids.append(fields[1])
        
        map(lambda x: sudovoid('ipcrm -m %s' % x), shmids)

    def cleanSemaphore(self):
        sems = []
        lines = filter(lambda x: x.startswith('0x'), shcmd('ipcs -s').readlines())
        for line in lines:
            fields = filter(lambda x: x.strip() != '', line.split(' '))
            sems.append(fields[1])
        
        map(lambda x: sudovoid('ipcrm -s %s' % x), sems)

    def cleanup(self):
        print "VxWorks Cleanup"
        try:
            for f in self.logfiles:
                f.cleanup()
        except:
            pass

        try:
            if not self.p['buildonly'] and self.vx['board'] in simicsTargets:
                if self.taps:
                    for tap in self.taps:
                        print shcmd('sudo ifconfig %s down' % tap).read()
                else:
                    print shcmd('sudo ifconfig tap0 down').read()
            elif self.vx['board'] != 'vxsim_linux':
                if self.vx['board'] in vlmTargets.keys() + directTargets.keys():
                    print '=== vxworks_target vlmTarget cleanup()'
                    for conn in self.vlmConns:
                        conn.close()
                if self.vx.get('power1'):
                    print shcmd("/usr/local/bin/pdu1.py off " + self.vx['power1']).read()
            else:
                if not self.p['buildonly']:
                    sudo("pkill vxsimnetd")
                    sudo("pkill -f rs_vxsim")
                    time.sleep(1)
                    sudo("pkill -9 -f rs_vxsim")
                    sudo("pkill -9 vxsimnetd")
                    sudo('pkill -9 wtxregd.ex')
                    time.sleep(2)
                    sudo('rm -f /var/lock/subsys/wtxregd')
                    time.sleep(3)
        except:
            pass


def runPingFromTarget(ubootTarget, pingCmd, ip4Addr, prompt='-> ', interruptCmd='ctrl+c'):
    #assert interruptCmd in ('ctrl+c', 'enter')
    #ubootTarget.sendAndExpect('%s "%s"' % (pingCmd, ip4Addr), 
    #                          '\d+ bytes from %s: seq=\d+ time=' % ip4Addr, timeout=120)

    #if interruptCmd == 'ctrl+c':
    #    cmd = '\003'
    #elif interruptCmd == 'enter':
    #    cmd = '\r'
    #lines = ubootTarget.sendAndReturnAll(cmd, prompt)

    # use 'rtt min/max/avg' as expected string instead of os.prompt since it's more robust
    lines = ubootTarget.sendAndReturnAll('%s "%s",8' % (pingCmd, ip4Addr), 'rtt min/max/avg \d+/\d+/\d+ ms')
    found = re.search('received,(.*?)% packet loss', '\n'.join(lines))
    if found is not None:
        if found.groups()[0].strip() == '100':
            return False
        else:
            return True
    else:
        return False    


class unixTarget(build):
    def __init__(self, host, log, p):
        super(unixTarget, self).__init__(host, log, p)
        self.bindirs = []
        self.unix = self.p['unix']

    def get_ports(self):
        return {'unix': 'unix'}

    def build(self, bopts):
        # We're using the UML TAP device device
        self.p['use_umldev'] = True
        uopts = BuildOpts(args = bopts)
        if self.unix:
            uopts.add(cflags = self.unix['cflags'], vars = self.unix['vars'])
            if self.unix['coverage']:
                uopts.add(vars = 'IPCODECOVERAGE=yes')
        self.binary_name = self.host.build('unix', '', '', self.p['vc'], None, self.p['networks'], uopts, self.p['rebuild'])[0]
        self.footprint = shcmd(("size %s" % self.binary_name) + " 2>&1").readlines()
        if not self.p['tinderbox_vars'].has_key('footprint_dec'):
            if len(self.footprint) == 2:
                titles = re.split("[\t ]*", self.footprint[0].strip())
                values = re.split("[\t ]*", self.footprint[1].strip())
                if len(titles) == len(values):
                    for ix in range(len(titles) - 1):
                        if titles[ix] in ('text', 'data', 'bss', 'dec'):
                            self.p['tinderbox_vars']['footprint_' + titles[ix]] = values[ix]

    def start(self, num, force_bridge):
        self.host.createNetwork(force_bridge)
        if 'board' not in self.p['tinderbox_vars']:
            self.p['tinderbox_vars']['board']           = 'unix'
            self.p['tinderbox_vars']['port']            = 'unix'
            self.p['tinderbox_vars']['port_version']    = '1.0'
            self.p['tinderbox_vars']['compiler']        = 'gcc'

        nets = self.p['networks']
        serial_dev_list = self.p['unix_serial_devs']
        usb_dev_list = self.p['unix_usb_devs']
        for i in range(num):
            unix_ifs = '"unix_ifs='
            config = ''

            if usb_dev_list is not None and len(usb_dev_list) > i:
                if i == 0:
                    usb_dev_net = self.host.createHostUniqueId()
                host_addr, entry = self.host.createHostAddress(usb_dev_net)
                unix_ifs += "%s," % usb_dev_list[i]
                config += " eth_inet=%s " % (host_addr)

            for net in range(nets):
                # Create the tun device for the specified bridge.
                host_addr, entry = self.host.createHostAddress(self.host.umlswitch[net]['magic'])
                # Append the tun device.
                if net != 0:
                    # Second append, do add delimiter
                    unix_ifs += ","
                    config   += " "
                else:
                    # Only first 'eth' is propagated; that is seen
                    # outside and used for connections.
                    address = host_addr
                    self.host.target_addresses.append(address)

                # Add to configuration strings
                unix_ifs += "daemon{0:0:0:0:0:%d|%s}" % (entry, self.host.umlswitch[net]['uml_ctl'])

                if usb_dev_list is not None and len(usb_dev_list) > i:
                    config += "eth%d=%s,255.255.255.0" % (net+1, host_addr)
                else:
                    if self.p['ipv6-only']:
                        config += "eth%d_inet6=%s" % (net, host_addr)
                    else:
                        config += "eth%d=%s" % (net, host_addr)


            unix_ifs += '"'
            if serial_dev_list is not None and len(serial_dev_list) > i:
                config += " serial_dev=%s" % serial_dev_list[i]

            binname = "unix%d" % i
            fullname = binname + "-" + address
            self.bindirs.append(binname)
            shcmdvoid('rm -rf %s' % binname)
            shcmdvoid('mkdir %s' % binname)
            cwd = os.getcwd()
            os.chdir(binname)

            if usb_dev_list is not None and len(usb_dev_list) > i:
                print 'sudo %s %s %s >/dev/null &' % (self.binary_name, unix_ifs, config)
                sudo('%s %s %s >/dev/null &' % (self.binary_name, unix_ifs, config))
            else:
                print '%s %s %s >/dev/null &' % (self.binary_name, unix_ifs, config)
                shcmdvoid('%s %s %s >/dev/null &' % (self.binary_name, unix_ifs, config))

            os.chdir(cwd)
            if self.p['attach']:
                logfile = "_".join(fullname.split(".")) + ".txt.gz"
                self.logfiles.append(zipLogFile(logfile, binname + "/syslog"))

            self.log.info('Target started using IP address %s (%s)' % (address, unix_ifs))
            if 'ipnet2' in self.p['vc']:
                stack_type = 'ipnet'
            else:
                stack_type = 'iplite'

            self.host.conf.append("%s= {'type': '%s', 'name': '%s', 'ip': '%s', 'os': '%s', 'speed' : %s }\n" % (binname, stack_type, address, address, "unix", self.p['target-speed']))
            self.host.host_array.append(binname)
        return 0, force_bridge


    def terminalError(self, mobj):
        # Check for CORE file
        for bindir in self.bindirs:
            self.log.info("looking in %s" % bindir)
            fobj = shcmd('ls -1 %s/core.* 2> /dev/null' % bindir)
            cores = fobj.readlines()
            if len(cores) > 0 and len(cores[0]) > 0:
                # Found a coredump.
                # Get me a backtrace
                corefile = cores[0].rstrip()
                lines = ["** CORE DUMP '%s' **\n" % corefile]
                fobj = shcmd('gdb %s --core %s --quiet --batch --ex "set height 0" -ex "thread apply all bt full" -ex "quit" 2> /dev/null' % (self.binary_name, corefile))
                lines += fobj.readlines()
                mobj.addTextAttachment("_".join(bindir.split('.')) + '_coredump.txt', "\r\n".join(lines))

    def addLogfiles(self, mobj):
        for fil in self.logfiles:
            fil.add(mobj)

    def cleanup(self):
        try:
            for fil in self.logfiles:
                fil.cleanup()
        except:
            pass


class umlTarget(build):
    def __init__(self, host, log, p, ext):
        super(umlTarget, self).__init__(host, log, p)
        self.uml = self.p[ext]
        self.prompt = 'UML>'
        self.escprompt = re.escape(self.prompt)
        self.ipv4 = p['ipv4-only']


    def get_ports(self):
        return {'las': 'las',
                'unix': 'unix/socktest'}

    def build(self, bopts):
        # We're using the UML TAP device device
        self.p['use_umldev'] = True
        # Build the UNIX socktest binaries
        binaries = self.host.build_socktest(static_link=True)
        shcmdvoid("cp %s ipcom_socktest" % binaries[0])


    def start(self, num, force_bridge):
        umlSettingWaitTime = 0.5
        self.host.createNetwork(force_bridge)
        for _ in range(3):
            self.address, self.entry = self.host.createHostAddress(self.host.umlswitch[0]['magic'])
            # Remove any old COW fs'
            sudo("rm -f cow_fs%s" % self.entry)
            cmd = "%s ubd0=cow_fs%s,%s eth0=daemon,0:0:0:0:0:%s,unix,%s 2> /dev/null" % (self.uml['kernel'], self.entry, self.uml['root'], self.entry, self.host.umlswitch[0]['uml_ctl'])
            self.log.info("***** " + cmd + " *****")
            try:
                self.s = pexpect.spawn(cmd)
            except:
                print "setup error?"
                raise SetupException(mailBody(None, [], 'UML startup error error:'))

            try:
                i = self.s.expect([r'sh-3',
                                  'login:',
                                  ], timeout = 300)

                if i == 1:
                    self.s.sendline('root')

                self.s.logfile = open('outfile', 'w')
                wait_time_out = 420
                self.s.expect('#', timeout = wait_time_out)
                self.s.sendline("")
                self.s.expect('#', timeout = wait_time_out) # add
                self.s.sendline("")
                self.s.expect('#', timeout = wait_time_out)
                self.s.sendline("reset")
                self.s.expect('#', timeout = wait_time_out) # add 
                self.s.sendline("")
                self.s.expect('#', timeout = wait_time_out)
                self.s.expect('#', timeout = wait_time_out)
                cwd = os.getcwd()
                self.s.sendline("mkdir /hostroot > /bootfile 2>&1")
                self.s.expect('#', timeout = wait_time_out) # add
                self.s.sendline("mount -t hostfs none -o %s /hostroot >> /bootfile 2>&1" % cwd)
                self.s.expect('#', timeout = wait_time_out) # add
                self.s.sendline("cp /hostroot/ipcom_socktest /socktest >> /bootfile 2>&1")
                self.s.expect('#', timeout = wait_time_out) # add
                if self.ipv4:
                    self.s.sendline("ip addr add %s/24 broadcast + dev eth0 >> /bootfile 2>&1" % (self.address))
                    self.s.expect('#', timeout = wait_time_out) # add
                    self.s.sendline("ip link set up dev eth0 >> /bootfile")
                    self.s.expect('#', timeout = wait_time_out) # add
                    self.s.sendline('ip route add default via %s >> /bootfile' % self.host.masterAddress)
                    self.s.expect('#', timeout = wait_time_out) # add
                    self.s.sendline('echo "%s master master.interpeak.se" >> /etc/hosts' % self.host.masterAddress)
                    self.s.expect('#', timeout = wait_time_out) # add
                else:
                    # Link up must preceed adding addresses in ipv6
                    self.s.sendline("ip link set up dev eth0 >> /bootfile")
                    self.s.expect('#', timeout = wait_time_out) # add
                    self.s.sendline("ip addr add %s/24 dev eth0 >> /bootfile 2>&1" % (self.address))
                    self.s.expect('#', timeout = wait_time_out) # add
                    self.s.sendline('ip route add %s/96 dev eth0 >> /bootfile' % self.host.masterAddress)
                    self.s.expect('#', timeout = wait_time_out) # add
                self.s.sendline('echo "DONE CONFIGURATION')
                self.s.expect('DONE CONFIGURATION', timeout = 300)
                os.close(self.s.fileno())
                if not self.host.ping_one(self.address):
                    print "ping fail -- retry UML start"
                    self.cleanup()
                else:
                    self.host.target_addresses.append(self.address)
                    self.host.conf.append("uml%s = { 'type' : 'linux', 'name' : 'linux', 'ip' : '%s', 'speed' : %s, 'os' : 'linux', 'user' : '%s', 'passwd' : '%s', 'login' : 'telnet', 'port' : 23, 'native' : 'yes' }\n" % (self.entry, self.address, self.p['target-speed'], self.uml['user'], self.uml['password']))
                    self.host.native.append('uml%s' % self.entry)
                    break
            except:
                traceback.print_exc()
                raise SetupException(mailBody(None, [self.s.before], 'boot error:'))
        else:
            raise SetupException(mailBody(None, ['unable to start UML targets'], 'boot error:'))
        return num, force_bridge

    def terminalError(self, mobj):
        pass

    def addLogfiles(self, mobj):
        pass

    def cleanup(self):
        try: #!!!?
            if not self.s:
                return
        except:
            return
        try:
            sudo("pkill -9 -P %d" % self.s.pid)
            sudo("kill -9 %d" % self.s.pid)
            for i in range(20):
                lines = sudo('ps -p %d' % self.s.pid)
                if len(lines) < 2:
                    break
                if "<defunct>" in lines[1]:
                    break
                print lines
                print lines[1]
                time.sleep(1)
            try:
                self.s.wait()
            except:
                try:
                    self.s.close()
                except:
                    pass
            sudo("rm -f cow_fs%s" % self.entry)
            self.s = None
        except:
            traceback.print_exc()
            print "UML cleanup failed"



def usage(argv):
    print """
Usage: %s [switches] <package>

    <package>   The name of the package to test.

    switches
    -4,--ipv4-only    Only use v4.
    -6,--ipv6-only    Only use v6.
    -b,--no-rebuild   do not rebuild everything (not recommended)
    -c,--checkout     checkout all modules
    --speed           Speed build
    --bridge          Force the final setup to use a bridge
    -p <dir>,--packages=<dir>
                      use packages located in <dir>
    -t,--tag          tag all modules if the test is successful
    -L, --loop        Loop the test the number of permutations specified
                      in the test.
    -l <config>,--lkm=<config>
                      <config> is a comma separated list of configuration
                      parameters in the form of key=value.
                      Currently supported and recognized keys are:
                          ip=<ip to target>
                          remote_interface=<remote interface to use in testing>
                          interface=<local interface to use for network setup>
                          user=<user to use when logging in>
                          password=<password to use when logging in>
                          kgdb=<directory to store binaries>
                          las-prefix=<las prefix>
                      ip,remote_interface,interface and user are required.
    -r <rev>,--revision=<rev>
                      the tag/branch to checkout
    -m <recipient>,--mail-notification=<recipient>
                      send a report to the specified recipient
    -d ,--dry         setup the network, but do not run tests. Tests may be
                      run manually.
    -T ,--local-tree  Run the tests in the local/current tree.
    --tree=<path>     Run the tests in the specified tree.
    -n <name>, --test-enginename=<name>
                      specify the name of the test to run in the testengine
    --supports=<features>
                      Comma separated list of features that is supported
                      in this particular configuration. Some tests has a
                      'requires' clause and those tests will only run if all
                      required features are listed in this option.
                      Supported features are:
                      Name           Description
                      serialdev      The target has at least 1 serial port
                                     that can be used by test cases.
                      sec2           The target has the sec2 security engine.
                      fwctrl         The target has the 'fwctrl' command, i.e. HW offload
                      cop2           The target has the octeon co-processor 2
    --unix-serial-devs=<devs>
                      Comma separated list of absolute path to serial device
                      nodes. Each started unix target will take one serial
                      device node from the list (left-to-right) until the list
                      has been exhausted or all targets has been started.
    --unix-usb-devs=<devs>
                      comma separated list of usb interfaces. Each started unix
                      target will take one usb interface from the list (left-to-right)
                      until the list has been exhausted or all targets has been started.
    --unix=<config>
                      <config> is a comma separated list of configuration
                      parameters in the form of key=value.
                      Currently supported and recognized keys are:
                          cflags=extra compile flags
                          vars=extra compile variables
    --uml=<config>
                      <config> is a comma separated list of configuration
                      parameters in the form of key=value. Uml's are used
                      to provice test cases with native linux resources.
                      Currently supported and recognized keys are:
                          type=Type of UML
                          root=Path to root file system
                          user=username to login on the uml
                          password=password for the above mentioned user
                          kernel=path to uml kernel.
    --lkm=<config>
                      <config> is a comma separated list of configuration
                      parameters in the form of key=value.
                      Currently supported and recognized keys are:
                          ip=Login ip
                          remote_if=Interface on the LKM machine to be used
                                    for testing communication
                          user=username to login on the uml
                          password=password for the above mentioned user
                          localif=Local interface to be used when mapping
                                  the LKM into the testing system
                          las-prefix=Path on the LKM machine where the LAS
                                     binaries are stored
    --vxworks=<config>
                      <config> is a comma separated list of configuration
                      parameters in the form of key=value.
                      Currently supported and recognized keys are:
                          cflags=extra compile flags
                          vars=extra compile variables
                          path=<path to vxworks installation>
                          version=<version - 6.5, etc>
                          board=<board - linux, malta4kc_mips32sf, etc>
                          tty=<serial port>
                          target=<cpu - mips, ppc etc>
                          interface=<interface to reach an external board>,
                          network=<network used for tftp and end debug>,
                          debug=<mode=[end|serial],[device=serial device],
                                 [address=end debug address]>
                          simicpath=simics workspace
                          imagepath=the path of vxworks image, including *.dtb
                          tftpserver=the tftp server
                          tftppath=the tftp path which the vxworks image will copy to
                          targets=the number of targets used for this module
                          codecoverage : indicate if it runs codecoverage
                            note: only fsl_t1t2 supports code coverage
                      For a simulator, path version and board are mandatory.
                      For a simics target, simicpath and imagepath are mandatory.
                      For an external target, all must be specified
    --wrlinux=<config>
                     <config> is comma separated list of configuration
                     parameters in the form of key=value.
                     Currently supported and recognized keys are:
                          board=<board type mti_malta32_be, etc>
                          tty=<serial port> not relevant with qemu
                          ttys=<baudrate> not relevant with qemu
                          interface=interface to reach an external board>
                          stdout <print output from serial console>
                          pkgdbg <build & include some additional packages>
                          qemu <emulate target with qemu>
                          qemucc <qemu compiler specifics>
                          qemuccflags <qemu compiler flags>
                          qemuconsole <start a xterm for each qemu emulated target>
                          qemudebug <prepare qemu for attaching a gdb to it>
                          qemunum <number of qemu emulated target instances>

     Known packages:""" % (argv[0])
    package_list = testable_packages.keys()
    package_list.sort()
    for package in package_list:
        print "    * " + package
    sys.exit(1)

def optSplit(arg):
    eopt = "ESCAPED_OPTION_COMMA"
    earg = arg.replace("\,", eopt)
    options = earg.split(',')
    return [part.replace(eopt, ',') for part in options]

def splitConfig(cfg, arg):
    lines = optSplit(arg)
    for line in lines:
        elem = line.split('=', 1)
        key = elem[0]
        if len(elem) > 2:
            raise CommandlineArgumentException('%s was erronously formatted' % line)
        if len(elem) == 1:
            value = True
        else:
            value = elem[1]
        cfg[key.lower()] = value

def verifyConfig(cfg, opt, options):
    for option in options:
        if option not in cfg:
            raise CommandlineArgumentException('%s must specify option "%s="' % (opt, option))

def arrayConfig(cfg, options):
    for option in options:
        if option in cfg and cfg[option]:
            cfg[option] = optSplit(cfg[option])
        else:
            cfg[option] = []

def noneConfig(cfg, options):
    for option in options:
        if option not in cfg:
            cfg[option] = None

def keyConfig(cfg, options):
    noneConfig(cfg, options)
    for option in options:
        optstr = cfg[option]
        if optstr:
            cfg[option] = {}
            splitConfig(cfg[option], optstr)

def parseArguments(args, ntest):
    """
    Returns:     { 'name'            : '<test name>',
                   'vc'              : (tuple of all version control modules),
                   'testengine_name' : '<name of the test in the test engine>',
                   'mail_notify'     : True | False
                   'mailto_success'  : '<recipient of success report>',
                   'mailto_failure'  : '<recipient of failure report>',
                   'checkout'        : True | False,
                   'revision'        : 'revision to checkout',
                   'tag'             : 'tag to put on the modules if success',
                   '4'               : 'v4 only',
                   '6'               : 'v6 only',
                   ''
                 }
    """
    mail_notify     = False
    mail_on_failure = False
    # Default values for all tests
    p = {
          '64bit'               : False,
          'attach'              : True,  # Attach the logs to the notificaiton mail
          'save_logs'           : False,  # Attach the logs to the notificaiton mail
          'build'               : '',    #
          'buildonly'           : False, # Build everything and run a dummy test that does nothing
          'capable'             : {},    # OS:es that can run the specific test (UNIX can run all tests)
          'checkout'            : False, # False=use build from local tree, True=checkout tree from version control
          'counterclockwise'    : False,
          'codecoverage'        : False,
          'domains'             : ['inet', 'inet6'], # List of address domains supported by testsuite
          'direct'              : False, # Indicate if it's a directly connected target & test for native
          'extensions'          : [],
          'extra_build_cflags'  : None,  # Extra flags that will be passed to the compiler when building the images
          'extra_build_opt'     : [],    # Extra defines that will be used when building
          'helix'               : False, # Indicate if it's a helix build & test
          'ipv4-only'           : False, # Build the IPv4-only configuration of the images
          'ipv6-only'           : False, # Build the IPv6-only configuration of the images
          'test-ipv6'           : False, # Use the option to bring up targets with IPv4, then set up IPv6 environment and execute IPv6 tests
          'lkm'                 : None,  # Configuration for LKM targets, no LKM target will be used if this is None
          'srctree'             : None, # False: requires a file structure created by this program
          'mailto_success'      : None,  # Recipient of success notification mail
          'manual'              : False, # True: build, configure everything and notify the user when its done
          'networks'            : 1,     # Number of independent networks that will be created (UNIX only feature)
          'packages'            : False, # List of path to tgz packages used to build the images
          'permutations'        : 1,     #
          'loop'                : False,     #
          'rebuild'             : True,  # Rebuild LKM/LAS binaries (safe but potentially slow)
          'requires'            : [],    # List of non-standard features required by this test suite (see 'supports')
          'revision'            : {'default': 'HEAD'}, # Revision to checkout by default
          'smp'                 : False,
          'speed'               : False, # True: build images with compiler optimizations enabled
          'supports'            : [],    # List of non-standard features supported by the current test setup  (see 'requires')
          'tag'                 : False,
          'targets'             : 6,
          'target-speed'        : '1',
          'vlmtargets'          : '',
          'tinderbox'           : False, # Set to True if the result should be reported to
          'toolchain'           : None,  # Toolchain used to build the binaries [gnu, diab, sfgnu, sfdiab, ...]
          'unix'                : None,  # Configuration for UNIX targets, they will be built with default configuration otherwise
          'unix_serial_devs'    : None,  # List of serial device nodes that can be used by the test case
          'unix_usb_devs'       : None,  # List of usb interfaces that can be used by the test case
          'unsupported'         : None,  # Revisions that is not supported by this test case
          'use_extdev'          : False, # True: Use external devices
          'use_simdev'          : False, # True: Use VxWorks simulator (vxsim)
          'use_umldev'          : False, # True: Use User Mode Linux device
          'verbose'             : False, # True: Enable verbose logging mode
          'vxworks'             : None,  #
          'vxprj'               : [], # VXPRJ INCLUDE statements
          'vxparam'             : [], # VXPRJ PARAM statements
          'noconn'              : None,
          'simics'              : None,  # simics qsp-arm
          'wrlinux'              : None,  # Configuration for WRLinux targets.
          'wrpath'              : None,
          'when'                : 'DAILY',
          'exclude_from_all'    : False,
          'tinderbox_vars'      : {
                                    'cci'       : 'no',
                                    'hwcrypto'  : 'no',
                                    'msp'       : 'no',
                                  },
          }

    shorts = 'L46p:Tdbcm:tr:n:M:S:N:'
    longs = [
        '64bit',
        'no-connectivity',
        'buildonly',
        'bridge',
        'checkout',
        'counterclockwise',
        'codecoverage',        
        'dry',
        'direct',
        'helix',
        'ipv4-only',
        'ipv6-only',
        'test-ipv6',
        'lkm=',
        'local-tree',
        'tree=',
        'loop',
        'mail-from=',
        'mail-header=',
        'mail-notification=',
        'mail-on-failure',
        'mail-success=',
        'no-rebuild',
        'packages=',
        'revision=',
        'smp',
        'up',
        'smtp-server=',
        'speed',
        'supports=',
        'tag',
        'targets=',
        'target-speed=',
        'vlmtargets=',
        'testengine-name=',
        'tinderbox',
        'tinderbox_args=',
        'toolchain=',
        'uml=',
        'unix=',
        'unix-serial-devs=',
        'unix-usb-devs=',
        'verbose',
        'vxworks=',
        'wrlinux=',
        'wrpath=',
        ]

    try:
        opts, args = getopt.gnu_getopt(args,
                                       shorts,
                                       longs)
    except getopt.GetoptError, desc:
        raise CommandlineArgumentException(desc)

    if len(args) == 0:
        raise CommandlineArgumentException('Too few arguments')

    if len(args) <= ntest:
        raise NoMoreTestsException('No more tests available')

    package = args[ntest]
    if package not in testable_packages:
        raise CommandlineArgumentException('"%s" is not a valid test name' % package)

    # Add the test specific argument overrides
    p['name'] = package
    for key in testable_packages[package]:
        p[key] = testable_packages[package][key]

    loop = False
    for opt, arg in opts:
        if opt in ('--wrpath'):
            p['wrpath'] = arg
        if opt in ('--toolchain',):
            if not arg in ('gnu', 'sfgnu', 'diab', 'sfdiab', 'gnube', 'diabbe', 'llvm'):
                raise CommandlineArgumentException('--toolchain must specify gnu, sfgnu, diab, sfdiab, gnube, diabbe', 'llvm')
            p['toolchain'] = arg
        if opt in ('--speed',):
            p['speed'] = True
        if opt in ('--smp',):
            p['smp'] = True
        if opt in ('--up',):
            p['smp'] = False            
        if opt in ('--64bit',):
            p['64bit'] = True
        if opt in ('--codecoverage',):
            p['codecoverage'] = True
        if opt in ('--counterclockwise',):
            p['counterclockwise'] = True
        if opt in ('--supports',):
            print arg
            p['supports'].extend(optSplit(arg))
        if opt in ('--verbose',):
            p['verbose'] = True
        if opt in ('--buildonly',):
            p['buildonly'] = True
            p['testengine_name'] = ['iptestengine.nop']
        if opt in ('--targets',):
            p['targets'] = int(arg)
        if opt in ('--target-speed',):
            p['target-speed'] = arg
        if opt in ('--vlmtargets'):
            p['vlmtargets'] = [x.strip() for x in arg.split(',')]
        if opt in ('-L', '--loop'):
            loop = True
        if opt in ('--helix',):
            p['helix'] = True
        if opt in ('--direct',):
            p['direct'] = True
        if opt in ('--dynamic',):
            p['dynamic'] = True
        if opt in ('-4', '--ipv4-only') and not p['ipv6-only']:
            p['ipv4-only'] = True
        if opt in ('-6', '--ipv6-only') and not p['ipv4-only']:
            p['ipv6-only'] = True
        if opt in ('--test-ipv6', ) and not p['ipv4-only']:
            p['test-ipv6'] = True
        if opt in ('-p', '--packages'):
            p['packages'] = arg
        if opt in ('-T', '--local-tree'):
            p['srctree'] = "../../.."
        if opt in ('--tree',):
            p['srctree'] = arg
        if opt in ('--no-connectivity',):
            p['noconn'] = True
        if opt in ('-b', '--no-rebuild'):
            p['rebuild'] = False
        if opt in ('-c', '--checkout'):
            p['checkout'] = True
        if opt in ('-N', '--mail-success'):
            if p['mailto_success']:
                if arg not in p['mailto_success']:
                    p['mailto_success'] += "," + arg
            else:
                p['mailto_success'] = arg
        if opt in ('-m', '--mail-notification'):
            mail_notify = True
            p['mailto_failure'] = arg
        if opt in ('--mail-on-failure',):
            mail_on_failure = True
        if opt in ('-M', '--mail-from',):
            mail['instance'] = arg
        if opt in ('-r', '--revision',):
            lines = arg.split(",");
            for line in lines:
                items = line.lstrip().split("=");
                if len(items) > 1:
                    p['revision'][items[0]] = items[1]
                else:
                    p['revision']['default'] = items[0]
        if opt in ('-t', '--tag'):
            p['tag'] = True
        if opt in ('-n', '--testengine-name'):
            p['testengine_name'] = [arg]
        if opt in ('-d', '--dry'):
            p['manual'] = True
        if opt in ('--tinderbox',):
            p['tinderbox'] = True
        if opt in ('--bridge',):
            p['use_extdev'] = True
        if opt in ('--tinderbox_args',):
            lines = arg.split(",")
            for line in lines:
                targ = line.split(":")
                if len(targ) != 2:
                    continue
                p['tinderbox_vars'][targ[0]] = targ[1]
        if opt in ('--unix',):
            unixconfig = {}
            splitConfig(unixconfig, arg)
            arrayConfig(unixconfig, ['cflags', 'vars'])
            noneConfig(unixconfig, ['coverage'])
            p['unix'] = unixconfig
        if opt in ('--unix-serial-devs',):
            p['unix_serial_devs'] = optSplit(arg)
        if opt in ('--unix-usb-devs',):
            p['unix_usb_devs'] = optSplit(arg)
        if opt in ('--lkm',):
            lkmconfig = {}
            splitConfig(lkmconfig, arg)
            arrayConfig(lkmconfig, ['cflags', 'vars'])
            verifyConfig(lkmconfig, opt, ['ip', 'remote_interface', 'user', 'interface'])
            noneConfig(lkmconfig, ['password', 'kgdb'])
            p['lkm'] = lkmconfig
        if opt in ['--wrlinux']:
            if not p['wrlinux']:
                p['wrlinux'] = {}
                p['wrlinux']['hw'] = {}
                p['wrlinux']['qemu'] = {}

            wrlinuxconfig = {}
            splitConfig(wrlinuxconfig, arg)
            arrayConfig(wrlinuxconfig, [ 'cflags', 'vars' ,'stty'])

            verifyConfig(wrlinuxconfig, opt, ['board'])
            noneConfig(wrlinuxconfig, ['tty','interface','pkgdbg','endian','arch','qemu','qemuconsole','qemucc', 'qemuccopts', 'qemudebug', 'nokqemu','qemunum','quickstart','stdout'])

            if wrlinuxconfig['qemu']:
                p['wrlinux']['qemu'][wrlinuxconfig['board']] = wrlinuxconfig
            else:
                p['wrlinux']['hw'][wrlinuxconfig['board']] = wrlinuxconfig

        if opt in ('--uml',):
            umlconfig = {}
            splitConfig(umlconfig, arg)
            verifyConfig(umlconfig, opt, ['type', 'kernel', 'root', 'user', 'password'])
            p['uml/' + umlconfig['type']] = umlconfig
        if opt in ('--vxworks',):
            if not p['vxworks']:
                p['vxworks'] = {}
            vxconfig = {}
            splitConfig(vxconfig, arg)
            verifyConfig(vxconfig, opt, ['board', 'version', 'path'])
            if not os.path.exists(vxconfig['path']):
                raise CommandlineArgumentException(vxconfig['path'] + ' doesnt exist')
            noneConfig(vxconfig, ['stdout', 'cci', 'shell', 'wrenv', 'cvs', 'noedr'])
            arrayConfig(vxconfig, ['cflags', 'vars', 'stty'])
            vxconfig['product'] = "_".join(vxconfig['version'].split("."))
            vxconfig['ipver'] = int("".join(vxconfig['version'].split('.')))
            vxconfig['vc'] = 'vxworks'
            if vxconfig['cci']:
                p['tinderbox_vars']['cci']      = 'yes'
                p['tinderbox_vars']['hwcrypto'] = 'yes'
                if vxconfig['ipver'] == 65:
                    vxconfig['vc'] += '-cci'

            if vxconfig['cvs']:
                vxconfig['vc'] += '-cvs'

            if vxconfig['shell']:
                if vxconfig['shell'] not in ('native', 'ipcom'):
                    raise CommandlineArgumentException('--vxworks "shell" must specify native or ipcom')
            else:
                vxconfig['shell'] = 'ipcom'

            p['tinderbox_vars']['shell'] = vxconfig['shell']
            # Simics
            if vxconfig['board'] in simicsTargets:
                verifyConfig(vxconfig, vxconfig['board'], ['simicspath', 'imagepath'])
                keyConfig(vxconfig, ['debug', 'ftp'])
                if vxconfig['debug']:
                    noneConfig(vxconfig['debug'], ['mode', 'device', 'address', 'num_tty'])
                if vxconfig['ftp']:
                    verifyConfig(vxconfig['ftp'], 'ftp', ['user', 'passwd'])            
            elif vxconfig['board'] != 'vxsim_linux':
                verifyConfig(vxconfig, vxconfig['board'], ['bootdev', 'tty', 'target', 'interface', 'imagepath', 'tftpserver', 'tftppath'])
                keyConfig(vxconfig, ['debug', 'ftp'])
                if vxconfig['debug']:
                    noneConfig(vxconfig['debug'], ['mode', 'device', 'address', 'num_tty'])
                if vxconfig['ftp']:
                    verifyConfig(vxconfig['ftp'], 'ftp', ['user', 'passwd'])
            else:
                noneConfig(vxconfig, ['debug'])

            if not vxconfig['wrenv']:
                vxconfig['wrenv'] = vxconfig['version']
            p['vxworks'][vxconfig['board']] = vxconfig

            #these 2 env variants are used for IPSYSVIEW
            pkg_path, wrenv_prefix = get_vxworks_env(vxconfig['path'])
            os.putenv('WIND_VX_HOME', vxconfig['path'])
            os.putenv('WIND_VX_BASE', os.path.dirname(pkg_path))
            os.putenv('WIND_VX_PLATFORM', wrenv_prefix.split(' ')[-1])
            
        if opt in ('-S', '--smtp-server'):
            mail['server'] = arg

    # If loops aren't allowed, force the permutations to be 1.
    if not loop or p['loop']:
        p['permutations'] = 1
    if not loop:
        p['loop'] = False

    if not mail_notify:
        if not mail_on_failure:
            p['mailto_success'] = None
            p['mailto_failure'] = None
            p['attach']         = False
        else:
            p['mailto_failure'] = p['mailto_success']
            p['mailto_success'] = None

    if p['speed']:
        p['extra_build_opt'].append('IPBUILD=speed')
    else:
        p['extra_build_opt'].append('IPBUILD=debug')
    if p['checkout'] and p['srctree']:
        raise CommandlineArgumentException('You may not specify both source tree and checkout')

    if p['helix']:
        if not 'vxsim_linux' in p['vxworks']:
            raise CommandlineArgumentException('helix must use vxsim_linux for vxworks')
        if not 'helixbsp' in p['vxworks']['vxsim_linux']:
            raise CommandlineArgumentException('helix must have the argument helixbsp at vxworks configuration')
        if not 'helixcpu' in p['vxworks']['vxsim_linux']:
            raise CommandlineArgumentException('helix must have the argument helixcpu at vxworks configuration')
        if not 'helixhost' in p['vxworks']['vxsim_linux']:
            raise CommandlineArgumentException('helix must have the argument helixhost at vxworks configuration')
        if not p['buildonly']:
            helixHost = p['vxworks']['vxsim_linux']['helixhost']
            host = socket.gethostname().split('.')[0]
            if helixHost != host:
                raise SetupException('runtestsuite.py must be running at the helix host %s' % helixHost)
            if helixHost not in helixHosts:
                raise SetupException('%s not supported by runtestsuite_conf.py' % helixHost)
            # set up this argument to force to use uml and bridge
            p['extensions'] = ['uml/generic']
        
    if p['direct']:
        if not 'vxsim_linux' in p['vxworks']:
            raise CommandlineArgumentException('direct must use vxsim_linux for vxworks')
        if not 'directbsp' in p['vxworks']['vxsim_linux']:
            raise CommandlineArgumentException('direct must have the argument directbsp at vxworks configuration')
        if not 'directcpu' in p['vxworks']['vxsim_linux']:
            raise CommandlineArgumentException('direct must have the argument directcpu at vxworks configuration')
        if not 'directhost' in p['vxworks']['vxsim_linux']:
            raise CommandlineArgumentException('direct must have the argument directhost at vxworks configuration')
        directHost = p['vxworks']['vxsim_linux']['directhost']
        if not p['buildonly']:
            directHost = p['vxworks']['vxsim_linux']['directhost']
            host = socket.gethostname().split('.')[0]
            if directHost != host:
                raise SetupException('runtestsuite.py must be running at the direct host %s' % helixHost)
            if directHost not in directHosts:
                raise SetupException('%s not supported by runtestsuite_conf.py' % directHost)
            # set up this argument to force to use uml and bridge
            p['extensions'] = ['uml/generic']


    bopts = BuildOpts(cflags = p['extra_build_cflags'], vars = p['extra_build_opt'])
    return p, bopts


def localtimeStr():
    return '%d-%02d-%02d %02d:%02d:%02d' % time.localtime()[:6]

def writeBody(body, p, mobj):
    body.write('Test was run on "' + socket.gethostname() + '"\r\n'
                'started at : ' + p['start_time'] + '\r\n'
                + 'ended at   : ' + localtimeStr() + '\r\n')
    body.write(mobj.body)

def sendMailNotification(p, to, subject, mobj):
    send_mail = True
    if to is None:
        to = "not_sent"
        send_mail = False
    else:
        tos = to.split(",")
        if len(tos) > 1:
            for to in tos:
                sendMailNotification(p, to, subject, mobj)
            return

    message = StringIO.StringIO()
    writer = MimeWriter.MimeWriter(message)
    writer.addheader('MIME-Version', '1.0')
    writer.addheader('Subject', '%s:%s' % (mail['instance'], subject))
    writer.addheader('To', to )

    # get ready to send attachment
    writer.startmultipartbody('mixed')
    # start off with a text/plain part
    part = writer.nextpart()
    body = part.startbody('text/plain')
    writeBody(body, p, mobj)

    for attachment in mobj.attachments:
        part = writer.nextpart()
        part.addheader('Content-Transfer-Encoding', 'base64')
        body = part.startbody(attachment.type)
        body.write(attachment.bdata)
    # finish off
    writer.lastpart()

    if send_mail:
        try:
            mail_server = smtplib.SMTP(mail['server'])
            mail_server.sendmail(mail['from'], to, message.getvalue())
            mail_server.quit()
        except:
            traceback.print_exc()
    else:
        print mobj.body


def sendTinderbox(p, tree, host, subject, mobj):
    message = StringIO.StringIO()
    writer = MimeWriter.MimeWriter(message)
    writer.addheader('MIME-Version', '1.0')
    writer.addheader('Subject', '%s:%s' % (mail['instance'], subject))
    writer.addheader('To', tinderbox['to'])

    # get ready to send attachment
    writer.startmultipartbody('mixed')
    # start off with a text/plain part
    part = writer.nextpart()
    body = part.startbody('text/plain')

    # Grab the attachemnt
    attachment = mobj.archiveAttachment()

    # Write the tinkerbox variables.
    body.write('tinderbox: tree: %s\r\n' % tree)
    for var in p['tinderbox_vars']:
        body.write('tinderbox: %s: %s\r\n' % (var, p['tinderbox_vars'][var]))

    # Send the attachments
    if attachment:
        body.write('tinderbox: binaryname: logfiles%d.tgz\r\n' % int(time.time()))

    body.write('tinderbox: timenow: %d\r\n' % int(time.time()))
    body.write('tinderbox: END\r\n\r\n')

    # Write the ordinary body.
    writeBody(body, p, mobj)

    # Write the configuration
    body.write(p['build'])

    # Print the tinderbox message without the attachments
    print message.getvalue()
    if attachment:
        part = writer.nextpart()
        part.addheader('Content-Transfer-Encoding', 'uuencode')
        body = part.startbody(attachment.type)
        body.write(attachment.bdata)

    # finish off
    writer.lastpart()
    try:
        mail_server = smtplib.SMTP(tinderbox['server'])
        mail_server.sendmail(tinderbox['from'], tinderbox['to'], message.getvalue())
        mail_server.quit()
    except:
        traceback.print_exc()


def mailNotify(p, host, result, tinderboxOnly, mobj):
    # Resolve the subject
    if p['tinderbox_vars'].has_key('status'):
        status = 'test(%s)' % p['tinderbox_vars']['status']
    else:
        status = 'test'

    if result:
        subject = 'SUCCESS: Automatic test of "%s" on branch "%s"' % (productName(p), host.moduleRevision())
        to      = p['mailto_success']
    else:
        subject = 'FAILED: Automatic %s of "%s" on branch "%s"' % (status, productName(p), host.moduleRevision())
        to      = p['mailto_failure']

    if not tinderboxOnly:
        sendMailNotification(p, to, subject, mobj)

    if p['tinderbox'] and mail['instance'] != 'UNIX':
        tree = p['name']
        sendTinderbox(p, tree, host, subject, mobj)
    else:
        for key in p['tinderbox_vars']:
            host.log("tinderbox: %s: %s" % (key, p['tinderbox_vars'][key]))


class mailAttachment:
    def __init__(self, name, bdata):
        self.name  = name
        self.type  = 'application/octet-stream; name="%s"' % name
        self.bdata = bdata

class mailObject:
    def __init__(self):
        self.body = ""
        self.attachments = []
        self.tario       = StringIO.StringIO()
        self.archive     = tarfile.open(name = 'logfile.tgz', mode = 'w:gz', fileobj = self.tario)

    def addBody(self, text):
        if isinstance(text, list):
            self.body += "\r\n".join(text)
        else:
            self.body += text

    def uuencode(self, name, uuin):
        uuout = StringIO.StringIO()
        uu.encode(in_file = uuin, out_file = uuout, name = name)
        result =  uuout.getvalue()
        uuout.close()
        uuin.close()
        return result

    def addBufferToArchive(self, name, str):
        info       = tarfile.TarInfo(name)
        info.size  = len(str)
        info.mtime = int(time.time())
        mstr       = StringIO.StringIO(str)
        self.archive.addfile(info, fileobj = mstr)
        mstr.close()

    def addFileToArchive(self, name, file):
        self.archive.add(file, arcname = name, recursive = False)

    def addTextAttachment(self, name, text):
        self.addBufferToArchive(name, text)
        self.attachments.append(mailAttachment(name, base64.encodestring(text)))

    def addFileAttachment(self, name, file):
        self.addFileToArchive(name, file)
        contents = StringIO.StringIO()
        base64.encode(open(file, 'rb'), contents)
        self.attachments.append(mailAttachment(name, contents.getvalue()))
        contents.close()

    def addGZipAttachment(self, name, buffer):
        zip_out = StringIO.StringIO()
        gzfile = gzip.GzipFile(None, 'wb', 9, zip_out)
        gzfile.write(buffer)
        gzfile.close()
        self.addBufferToArchive(name, zip_out.getvalue())
        self.attachments.append(mailAttachment(name, base64.encodestring(zip_out.getvalue())))
        zip_out.close()

    def addGZipFileAttachment(self, name, file):
        in_file = open(file, 'rb')
        contents = in_file.read()
        in_file.close()
        self.addGZipAttachment(name, contents)

    def archiveAttachment(self):
        if len(self.attachments) > 0:
            if self.archive:
                self.archive.close()
                self.archive = None
            bin = StringIO.StringIO(self.tario.getvalue())
            return mailAttachment('logfiles.tgz', self.uuencode('logfiles.tgz', bin))
        return None

    def __str__(self):
        return self.body


def mailBody(mail, lines, prefix = None, suffix = None):
    """
    Converts the list of lines of output from a process to something that can be appended to a e-mail
    lines - List of lines from shcmd().readlines()
    """
    if not mail:
        mail = mailObject()

    if prefix == None:
        text = ''
    else:
        text = prefix + '\r\n'

    for line in lines:
        text += line[:-1] + '\r\n'

    if suffix != None:
        text += suffix + '\r\n'
    mail.addBody(text)
    return mail


def productName(p):
    name = p['name']
    if p['ipv4-only']:
        name += '-v4only'
    if p['ipv6-only']:
        name += '-v6only'
    if p['speed']:
        name += '-speed'
    if p['toolchain']:
        name += "-"
        name += p['toolchain']
    return name


startCodeCov = 'board1.console1.con.input "cmd echo kong-code-coverage-start\\n"'
endCodeCov   = 'board1.console1.con.input "cmd echo kong-code-coverage-end\\n"'

def sendCmdSimicsConsole(ipAddress, port, cmd):
    tcmd = "telnet %s %s" % (ipAddress, port)
    prompt = 'running> '
    s = pexpect.spawn(tcmd, timeout=20)
    s.logfile = sys.stdout

    expect_array = [prompt,
                    'Connection refused',
                    'Name or service not known',
                   ]
                   
    i = s.expect(expect_array, timeout = 30)

    if i == 0:
        s.send(cmd + '\n')
        s.expect(prompt)
        s.send('exit -d\n')
        s.expect('running> Connection closed by foreign host.')
    elif i == 1 or i == 2:
        raise SetupException('failed to connect to simics console')
    else:
        raise SetupException('telnet expect returns %s' % i)


def getIpPrefix(ipAddr, addrSeparator):
    tokens = ipAddr.split(addrSeparator)
    return addrSeparator.join(tokens[:-1]) + addrSeparator


def copyImageToFtpServer(p, imagePath, tftpPath):
    if not os.path.exists(imagePath):
        raise SetupException('imagepath:%s not existed' % imagePath)
    if not os.path.exists(tftpPath):
        raise SetupException('tftp_path:%s not existed' % tftpPath)
    boardName = p['vxworks'].keys()[0]
    if p['direct']:
        boardName = p['vxworks']['vxsim_linux']['directbsp']
    if boardName in vlmTargets.keys() + directTargets.keys():  # only vlmTargets and directTargets need to copy image to tftp server
        print shcmd('rm -fr %s/*' % tftpPath).readlines()
        print shcmd('cp -fr %s/* %s' % (imagePath, tftpPath)).readlines()
        print shcmd('chmod -R 777 %s' % tftpPath).readlines()


def createHelixMIPName(kongModuleName):
    return 'HELIX_%s' % kongModuleName


def testOneProduct(argv, log, ntest):
    lhost = None
    targets = []
    cwd = os.getcwd()
    try:
        try:
            p, bopts = parseArguments(argv, ntest)     # p 是字典类型

            if debugFlag:
                import pprint as pp
                print '=== p=', pp.pprint(p)
            #sys.exit(0)

            board = p['vxworks'].keys()[0]     # 在python3里面需要转化为list才能使用下标来查找元素
            if board in vlmTargets:
                global tftp_server, tftp_path
                tftp_server = p['vxworks'][board]['tftpserver']
                tftp_path = p['vxworks'][board]['tftppath']                
                print 'tftp_server:%s, tftp_path:%s' % (tftp_server, tftp_path)
            
            log.info('Start automatic testing of "%s"' % p['name'])
            if (p['name'] == 'IPCCI' or p['name'] == 'IPCCI_PERF' ) and not p['speed']:
                log.info('package %s does not support debug builds ' % p['name'])
                return

            p['start_time'] = localtimeStr()
            lhost = LinuxHost(log, p)


            #tinderbox
            p['tinderbox_vars']['starttime'] = int(time.time())
            buildname = "%s-%s-%s" % (mail['instance'], lhost.moduleRevision().partition(':')[0], productName(p))
            buildname = "_".join(buildname.split('/'))
            p['tinderbox_vars']['buildname']   = buildname
            p['tinderbox_vars']['errorparser'] = 'void'
            p['tinderbox_vars']['status']      = 'success'
            p['tinderbox_vars']['release']     = lhost.moduleRevision().partition(':')[0]
            p['tinderbox_vars']['codebase']        = lhost.moduleRevision().partition(':')[2]
            if p['toolchain']:
                p['tinderbox_vars']['toolchain'] = p['toolchain']
            if p['buildonly']:
                p['tinderbox_vars']['buildonly'] = 'yes'
            if p['ipv4-only']:
                p['tinderbox_vars']['v4only'] = 'yes'
            else:
                p['tinderbox_vars']['v4only'] = 'no'
            if p['ipv6-only']:
                p['tinderbox_vars']['v6only'] = 'yes'
            else:
                p['tinderbox_vars']['v6only'] = 'no'
            if p['speed']:
                p['tinderbox_vars']['speed'] = 'yes'
            else:
                p['tinderbox_vars']['speed'] = 'no'
            if p['packages']:
                dire = p['packages'].rstrip("/ ")
                dire = os.path.split(dire)
                dire = dire[len(dire) - 1]
                p['tinderbox_vars']['package'] = dire
            if 'patchlevel' not in p['tinderbox_vars']:
                p['tinderbox_vars']['patchlevel'] = 'undefined'


            #bail
            if p['unsupported'] and lhost.moduleRevision() in p['unsupported']:
                log.info('package %s does not support revision %s' % (p['name'], lhost.moduleRevision()))
                return
            if p['ipv4-only'] and not 'inet' in p['domains']:
                log.info('package %s does not support ipv4only' % p['name'])
                return
            for require in p['requires']:
                if require not in p['supports']:
                    log.info('package %s requires "%s"' % (p['name'], require))
                    return

            #list different build-functions (but uml needs one per instance(?))
            if p['vxworks'] and 'vxsim_linux' in p['vxworks']:
                # markus print "aaaaaa %s" % p['vxworks']
                if 'vxworks' not in p['capable']:
                    log.info('vxworks not supported by package ' + p['name'])
                    return
                if 'minver' in p['capable']['vxworks']:
                    if p['capable']['vxworks']['minver'] > p['vxworks']['linux']['ipver']:
                        log.info('package %s requires vxworks revision %d' % (p['name'], p['capable']['vxworks']['minver']))
                        return
                targets.append(vxworks_target(lhost, 'vxsim_linux', log, p))

                if p['direct']:
                    directboard = p['vxworks']['vxsim_linux']['directbsp']

            else:
                if p['lkm'] != None:
                    if 'las' not in p['capable']:
                        log.info('las not supported by package ' + p['name'])
                        return
                    # lkm must be processed before unix
                    targets.append(lkmTarget(lhost, log, p))

                if p['wrlinux'] != None:
                    if 'las' not in p['capable']:
                        log.info('las not supported by package ' + p['name'])
                        return

                    # wrlinux must be processed before unix
                    for type in ('hw', 'qemu'):
                        for board in p['wrlinux'][type]:
                            targets.append(wrlinuxTarget(lhost, board, type, log, p))

                if p['vxworks']:
                    if 'vxworks' not in p['capable']:
                        log.info('vxworks not supported by package ' + p['name'])
                        return
                    for board in p['vxworks']:
                        if 'minver' in p['capable']['vxworks']:
                            if p['capable']['vxworks']['minver'] > p['vxworks'][board]['ipver']:
                                log.info('package %s requires vxworks revision %d' % (p['name'], p['capable']['vxworks']['minver']))
                                return
                        targets.append(vxworks_target(lhost, board, log, p))

                if p['vxworks'].keys()[0] not in simicsTargets and \
                   p['vxworks'].keys()[0] not in vlmTargets:
                    targets.append(unixTarget(lhost, log, p))
                    
            if not p['buildonly']:
                for ext in p['extensions']:
                    if ext in p and 'uml' in ext:
                        targets.append(umlTarget(lhost, log, p, ext))


            vc_modules = p['vc']
            if 'testengine_name' in p:
                vc_modules.append('iptestengine')

            if p['ipv4-only'] and not p['ipv6-only']:
                bopts.add(vars = "IPCOM_USE_INET6=no")

            if p['ipv6-only'] and not p['ipv4-only']:
                bopts.add(vars = "IPCOM_USE_INET=no")

            mports = {}
            for target in targets:
                mports.update(target.get_ports())

            lhost.cvs_checkout(vc_modules, mports)

            p['tinderbox_vars']['errorparser'] = 'unix'
            try:
                for target in targets:
                    if isinstance(target, vxworks_target):
                        # tinderbox
                        p['tinderbox_vars']['board'] = target.vx['board']
                        p['tinderbox_vars']['port'] = 'VXWORKS'
                        p['tinderbox_vars']['port_version'] = target.vx['version']
                        p['tinderbox_vars']['compiler'] = 'gcc' if target.vx['tool'] in ('gnube', 'gnu', 'sfgnu') else 'diab'
                        p['tinderbox_vars']['vxprj'] = 'yes'
                        p['tinderbox_vars']['cvs'] = 'yes' if target.vx['cvs'] else 'no'
                        p['tinderbox_vars']['smp'] = 'yes' if target.p['smp'] else 'no'
                        p['tinderbox_vars']['64bit'] = 'yes' if target.p['64bit'] else 'no'

                        import runtestsuite_build
                        logpath = '%s/%s_vip' % (os.getcwd(), target.vx['board'])
                        if target.p['rebuild']:
                            mopts = BuildOpts(args = bopts)
                            pcflags = target.p.get('platform_cflags', None)
                            if pcflags:
                                bflags = pcflags.get('vxworks/' + target.vx['board'], None)
                                if not bflags:
                                    bflags = pcflags.get('vxworks', None)
                                if bflags:
                                    mopts.add(cflags = bflags)
                            cextra = target.vx.get('cflags', None)
                            cvars = target.vx.get('vars', None)
                            mopts.add(cflags = cextra, vars = cvars)
                            bridgeports = target.vx.get('bridgeports',None)
                            
                            print '=== start build vxworks at %s' % time.asctime()
                            runtestsuite_build.vxworks(testable_packages[target.p['name']],
                                                       mopts.cflags,
                                                       target.log.info,
                                                       target.vx['board'],
                                                       target.vx['path'],
                                                       target.vx['cvs'],
                                                       logpath,
                                                       target.vx['wrenv'],
                                                       target.p['smp'],
                                                       target.p['64bit'],
                                                       target.p['speed'],
                                                       target.vx['shell'],
                                                       target.vx['debug'],
                                                       target.p['ipv4-only'],
                                                       target.p['ipv6-only'],
                                                       target.vx['target'],
                                                       target.vx['tool'],
                                                       not target.vx['noedr'],
                                                       bridgeports
                                                       )
                        target.binary_name = "%s/default/vxWorks" % logpath
                        print '*** target.binary_name=', target.binary_name

                        # TTY mode?
                        target.vx['console'] = True
                        if target.vx['debug'] and target.vx['debug']['mode'] == 'tty':
                            target.vx['console'] = False
                        if target.vx['board'] != 'vxsim_linux':
                            if target.vx['board'] in vlmTargets:
                                target.p['use_simdev'] = False
                                boardName = target.vx['board']
                                tftp_path = p['vxworks'][boardName]['tftppath']
                                copyImageToFtpServer(p, p['vxworks'][boardName]['imagepath'], tftp_path)
                            else:
                                # legacy code
                                target.p['use_simdev'] = True
                                target.vx['tftpfile'] = target.vx['board'] + "_vxWorks.st"
                                shcmdvoid("mkdir -p /tftproot")
                                if not os.path.exists(target.binary_name):
                                    raise BuildException(mailBody(None, ['Could not find image file in %s' % target.binary_name]))
                                sudo("cp %s /tftproot/%s" % (target.binary_name, target.vx['tftpfile']))
                        else:
                            target.p['use_simdev'] = True

                        target.wrenv = "%s/wrenv.linux -p vxworks-%s " % (target.vx['path'], target.vx['wrenv'])
                        #tinderbox
                        footprint = sudo("size %s 2>&1" % target.binary_name)
                        p['build'] += "\r\n" + "".join(footprint) + "\r\n"
                        if len(footprint) == 2:
                            titles = footprint[0].split()
                            values = footprint[1].split()
                            if len(titles) == len(values):
                                for ix in range(len(titles) - 1):
                                    if titles[ix] in ('text', 'data', 'bss', 'dec'):
                                        p['tinderbox_vars']['footprint_' + titles[ix]] = values[ix]

                        if p['helix'] and p['rebuild']:
                            import vxBuild, commands, shutil
                            installPath = target.vx['path']
                            helixBsp = target.vx['helixbsp']
                            helixHost = target.vx['helixhost']
                            helixCpu = target.vx['helixcpu']
                            tool = p['toolchain']
                            helixSmp, helixM64bit = True, False
                            mipModule = helixBuild[helixBsp]['MIP']
                            overrides = { 'kong_build' : p['name'], }
                            if helixBuild[helixBsp]['dynamic']:
                                mipPath = vxBuild.buildHelixDynamic(mipModule, installPath, helixBsp, helixCpu, tool, helixSmp, helixM64bit, overrides)
                            else:
                                mipPath = vxBuild.buildHelixStatic(mipModule, installPath, helixBsp, helixCpu, tool, helixSmp, helixM64bit, overrides)
                                
                            if helixEnableImageCopy:
                                fromDir = '%s/default' % mipPath
                                if helixBsp.find('_hvsafe') != -1 or helixBsp.find('_dynamic') != -1:
                                    fromDir = mipPath
                                toDir   = helixHosts[helixHost]['tftp_path']
                                shutil.copyfile('%s/%s' % (fromDir, helixBuild[helixBsp]['image']), '%s/%s' % (toDir, helixBuild[helixBsp]['image']))
                                if helixBuild[helixBsp]['dtb'] is not None:
                                    shutil.copyfile('%s/%s' % (fromDir, helixBuild[helixBsp]['dtb']), '%s/%s' % (toDir, helixBuild[helixBsp]['dtb']))

                        if p['direct'] and p['rebuild']:
                            import vxBuild, commands, shutil
                            installPath = target.vx['path']
                            directBsp = target.vx['directbsp']
                            directHost = target.vx['directhost']
                            directCpu = target.vx['directcpu']
                            tool = p['toolchain']

                            logpath = '%s/%s_vip' % (os.getcwd(), directBsp)
                            print('=== start build vxworks for bsp %s at %s' % (directBsp,time.asctime()))
                            runtestsuite_build.vxworks(testable_packages[target.p['name']],
                                                       mopts.cflags,
                                                       target.log.info,
                                                       directBsp,
                                                       target.vx['path'],
                                                       target.vx['cvs'],
                                                       logpath,
                                                       target.vx['wrenv'],
                                                       target.p['smp'],
                                                       target.p['64bit'],
                                                       target.p['speed'],
                                                       target.vx['shell'],
                                                       target.vx['debug'],
                                                       target.p['ipv4-only'],
                                                       target.p['ipv6-only'],
                                                       target.vx['target'],
                                                       target.vx['tool'],
                                                       not target.vx['noedr'],
                                                       bridgeports
                                                       )
                            target.binary_name = "%s/default/vxWorks" % logpath
                            print '*** target.binary_name=', target.binary_name

                            if target.vx['directbsp'] in directTargets:
                                boardName = target.vx['directbsp']
                                tftp_path = directHosts[directHost]['tftp_path']
                                copyImageToFtpServer(p, logpath, tftp_path)

                    else:
                        # target.build(bopts)
                        target.p['use_umldev'] = True
                        print "Skipping unix build"
                
            except build_exception, e:
                raise BuildException(mailBody(None, e.message[1], e.message[0]))

            if p['buildonly']:
                if os.path.exists(target.binary_name):
                    print 'build only completed'
                    sys.exit(0) 
                else:
                    print 'cannot find vxWorks image at %s' % target.binary_name
                    sys.exit(1)

            p['tinderbox_vars']['errorparser'] = 'void'
            print '=== start linux host at %s' % time.asctime()
            lhost.start() #doesnt start anything

            # Do we need to force bridge usage for all subsequent ports?
            # If we're using the simdev, and anything else, we need to bridge
            force_bridge = p['codecoverage'] or p['use_extdev'] or (p['use_simdev'] and p['use_umldev'])
            num_binaries = p.get('targets', 6)
            try:
                for target in targets: #wtf?
                    num_binaries, force_bridge = target.start(num_binaries, force_bridge)
            except:
                traceback.print_exc()
                raise

            p['tinderbox_vars']['errorparser'] = 'testengine'

            if 'anvl' in p:
                test_suite_log = lhost.runAnvlTestSuite(targets)
            else:
                print '=== start runTestSuite at %s' % time.asctime()
                test_suite_log = lhost.runTestSuite(targets)

            if p['tag']:
                for vc_module in vc_modules:
                    lhost.tag(vc_module,
                              '%s-%s-%s-LAST_SUCCESSFUL_TESTRUN' % (mail['instance'], lhost.moduleRevision(vc_module), p['name']), True)

            p['tinderbox_vars']['status'] = 'success'
            mailNotify(p, lhost, True, False, test_suite_log)
        except CommandlineArgumentException, desc:
            log.error('%s exception raised: %s' % (desc.__class__.__name__, desc))
            usage(sys.argv)
        except BuildException, inst:
            log.error('%s exception raised: %s' % (inst.__class__.__name__, inst))
            p['tinderbox_vars']['status'] = 'build_failed'
            mailNotify(p, lhost, False, False, *inst.args)
        except SetupException, inst:
            traceback.print_exc()
            log.error('%s exception raised: %s' % (inst.__class__.__name__, inst))
            p['tinderbox_vars']['status'] = 'not_running'
            p['tinderbox_vars']['tests_failed']  = "1"
            p['tinderbox_vars']['tests_ok']      = "0"
            p['tinderbox_vars']['tests_skipped'] = "0"
            p['tinderbox_vars']['tests_total']   = "1"
            mailNotify(p, lhost, False, False, *inst.args)
        except TestSuiteException, inst:
            log.error('%s exception raised: %s' % (inst.__class__.__name__, inst))
            mailNotify(p, lhost, False, False, *inst.args)
        except VersionControlException, inst:
            log.error('%s exception raised: %s' % (inst.__class__.__name__, inst))
        except TestSilentlySkippedException, inst:
            log.info('package %s has been skipped; probably due to test script requirements.' % (p['name']))
            mailNotify(p, lhost, True, False, *inst.args)
    finally:
        print '=== end runtestsuite at %s' % time.asctime()
        log.info('cleaning up')
        os.chdir(cwd)
        for target in targets:
            try:
                target.cleanup()
            except:
                pass


if __name__ == '__main__':
    log = Log(Log.LEVEL_DEBUG)
    print '=== start runtestsuite at %s' % time.asctime()
    if sys.argv[-1] == 'ALL':
        allpkg = []
        for package in testable_packages:
            if 'exclude_from_all' not in testable_packages[package] or not testable_packages[package]['exclude_from_all']:
                allpkg.append(package)
        argv = sys.argv[1:-1] + allpkg
    else:
        argv = sys.argv[1:]

# cmdPrefix="$SCRIPTPATH/runtestsuite.py
# --uml="type=generic,kernel=/uml/linux,root=/uml/ubuntu_root_fs,user=test,password=test"
# --targets=$VLMTARGETNUM
# --vlmtargets="$VLMTARGETS"
# --speed $SMP
# --supports=mipl
# --target-speed=50
# --toolchain=$TOOL
# --vxworks="board=$BOARD,imagepath=$IMAGEPATH,tftpserver=$TFTPSERVER,tftppath=$TFTPPATH,$shell=ipcom,stdout,target=$TARGET,bootdev=fei_intel,interface=eth1,version=7,wrenv=$wrenv,path=$GITPATH,tty=/dev/ttyS0"
# "
    ntest = 0
    while True:
        try:
            testOneProduct(argv, log, ntest)
            ntest += 1
        except NoMoreTestsException, desc:
            log.info('A total of %d tests has been executed' % ntest)
            break


