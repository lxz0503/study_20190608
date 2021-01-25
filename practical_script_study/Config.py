# config file

import os, sys, sets
from commands import getoutput
from logging import error

from Contact import *

class JenkinsJob:
    triggerJob = 'vx7-dev-branch-build'
    downstreamJob = 'vx7-dev-branch-truely-build'
    
masterGitPath = '/net/pek-cc-pb05l/buildarea1/target/vx7dev/vxworks'

FS_LAYERS =     [
                "FS",
                "FS_CDROMFS",
                "FS_CORE",
                "FS_COMMON",
                "FS_DEVFS",
                "FS_VFS",
                "FS_DOSFS",
                "FS_HRFS",
                "FS_NFS",
                "FS_ROMFS",
                "FS_VRFS",
                "FSAPI",
                "FSAPI_TCPLAY",
                "FSAPI_USR",
                "FSAPI_UTIL",
                "FSAPP",
                "BDM",
                "BDM_FLASH",
                "BDM_MTD",
                "BDM_NFTL",
                "BDM_SIM",
                "BDM_TFFS",
                "BDM_TFFS_DRIVER",
                "BDM_LOOPFS",
                "BDM_NVRAM",
                "BDM_SATA",
                "BDM_SDMMC",
                "BDM_XBD",
                "SDMMC",
                "SDMMC_CORE",
                "SDMMC_DEVICE",
                "SDMMC_STORAGE",
                "SDMMC_HOST",
                "SDMMC_SDHC",
                "SDMMC_TIMMCHS",
                ]

MIDDLEWARE_LAYERS =     [
                         'IPNET_SSL',
                         'IPNET_CRYPTO',
                         'IPNET_IPCRYPTO',
                         'IPNET_SSH',
                         'SNMP',
                         'WEBCLI',
                         'WEBCLI_CLI',
                         'WEBCLI_HTTP',
                         'WEBCLI_CLIDEMO',
                         'WEBCLI_WEBDEMO',
                         ]

VF610_TWR_LAYERS =     [
                         'SDMMC',
                         'SDMMC_CORE',
                         'SDMMC_DEVICE',
                         'SDMMC_STORAGE',
                         'SDMMC_HOST',
                         'SDMMC_SDHC',
                         'FSL_VYBRID',
                         'BDM_FLASH',
                         'USB_EHCI',
                         ]


IPNET_LAYERS = [
                "IPNET",
                "IPNET_AAA",
                "IPNET_DIAMETER",
                "IPNET_RADIUS",
                "IPNET_COREIP",
                "IPNET_CRYPTO",
                "IPNET_IPCRYPTO",
                #"IPNET_IPFREESCALE",
                #"IPNET_IPHWCRYPTO", 
                "IPNET_DHCPC6",
                "IPNET_DHCPC",
                "IPNET_DHCPR",
                "IPNET_DHCPS6",
                "IPNET_DHCPS",
                "IPNET_DNSC",
                "IPNET_EAP",
                "IPNET_FIREWALL",
                "IPNET_FTP",
                "IPNET_IPSECIKE",
                "IPNET_IKE",
                "IPNET_IPSEC",
                "IPNET_LINKPROTO",
                "IPNET_BRIDGE",
                "IPNET_L2TP",
                "IPNET_PPP",
                #"IPNET_ROHC",
                "IPNET_MOBILITY",
                "IPNET_8021X",
                "IPNET_DOT1X",
                "IPNET_WLAN",
                "IPNET_WLANDRV",
                "IPNET_WLANMLME",
                "IPNET_WPS",
                "IPNET_NTP",
                "IPNET_QOS",
                "IPNET_ROUTEPROTO",
                "IPNET_RIP",
                "IPNET_RIPNG",
                "IPNET_SNTP",
                "IPNET_SSH",
                "IPNET_SSL",
                "IPNET_TFTP",
                "IPNET_USRSPACE",
                "IPNET_VRRP",
                "NET_BASE",
                "NET_BENCHMARK",
               ]

JUNGANG_LAYERS = [
                  'IPNET',
                  'IPNET_DHCPC6',
                  'IPNET_DHCPC',
                  'IPNET_DNSC',
                  'IPNET_FTP',
                  'IPNET_TFTP',
                 ]

JUNGANG_TO_PREVENT = [
                      '/pkgs/net/ipnet',
                     ]

# directories to capture prevent output                 
COMPS_TO_PREVENT = [
                   '/pkgs/storage',
                   '/pkgs/connectivity/can',
                   '/pkgs/connectivity/usb',
                   '/pkgs/connectivity/ieee1394',
                   '/pkgs/connectivity/bluetooth',
                   '/pkgs/net/end',
                   '/pkgs/net/ipnet',
                   '/pkgs/net/mib2',
                   '/pkgs/net/net_base',
                   '/pkgs/os/drv/vxbus/drv',
                   '/pkgs/os/drv/vxbus/subsystem',
                   '/pkgs/os/platform/fsl_imx',
                   '/pkgs/os/arch/arm',
                   '/pkgs/ui/audio/drv/fslsgtl5000',
                   ]

NET_TO_PREVENT = ['/pkgs/net/ipnet',
                  '/pkgs/net/ipnet/app/ntp',
                  '/pkgs/net/mib2',
                  '/pkgs/net/net_base',
                  #'/pkgs/security/openssl', # owned by network
                  #'/pkgs/security/hash',    # owned by network
                 ]

jwang9_TO_PREVENT = ['/pkgs/net/ipnet',
                  '/pkgs/net/ipnet/coreip',
                  '/pkgs/net/ipnet/usrspace',
                  ]

NET_TO_PREVENT_NONTP = ['/pkgs/net/ipnet',
                  '/pkgs/net/mib2',
                  '/pkgs/net/net_base',
                 ]

USB_TO_PREVENT = [
                  '/pkgs/connectivity/usb',
                  '/pkgs/connectivity/sdmmc',
                 ]  

CAN_TO_PREVENT = [
                  '/pkgs/connectivity/can',
                 ]  

FIREWIRE_TO_PREVENT = [
                       '/pkgs/connectivity/ieee1394',
                      ]

BLUETOOTH_TO_PREVENT = [
                       '/pkgs/connectivity/bluetooth',
                       ]

MIDDLEWARE_TO_PREVENT = [
                       '/pkgs/app/samples',
                       '/pkgs/app/snmp',
                       '/pkgs/app/webcli',
                       '/pkgs/app/webcli/curl',
                       ]

vf610_twr_TO_PREVENT = [
                       '/pkgs/os/platform/fsl_vybrid',
                       '/pkgs/connectivity/sdmmc',
                       '/pkgs/storage/bdm/flash',
                       '/pkgs/connectivity/usb',
                       '/pkgs/os/drv/vxbus/drv',
                       '/pkgs/os/arch/arm/kernel',
                       '/pkgs/net/end/drv',
                       ]

TEST_TO_PREVENT = [
                       '/pkgs/storage/fs/vxTest',
                       '/pkgs/connectivity/usb/test',
                       '/pkgs/os/utils/ostools/vxTest',
                       '/pkgs/os/utils/boardlib/vxTest',
                       '/pkgs/os/utils/shell/vxTest',
                       '/pkgs/os/core/rtp/vxTest',
                       '/pkgs/os/core/io/vxTest',
                       '/pkgs/os/core/kernel/vxTest',
                       '/pkgs/os/drv/vxbus_legacy/vxTest',
                       '/pkgs/os/drv/vxbus/vxTest',
                       '/pkgs/os/drv/vxbus/subsystem/vxTest',
                   ]

PPC64_TO_PREVENT = [
                        '/pkgs/os'
                   ]
                   
branches = {
    'fr64-vx7-ppc64':[
        {'fsl_p3p4p5':{'cpu':'', 'tool':'diab', 'keywords':[], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':PPC64_TO_PREVENT } },
        #{'fsl_t1':{'cpu':'', 'tool':'diab', 'keywords':[], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':PPC64_TO_PREVENT } },
        #{'fsl_t2t4':{'cpu':'', 'tool':'diab', 'keywords':[], 'parallelBuild':True, 'preventBuild':True, 'smp':True, 'layers':[], 'components':PPC64_TO_PREVENT } },
        #{'qsp_ppc':{'cpu':'', 'tool':'diab', 'keywords':[], 'parallelBuild':True, 'preventBuild':True, 'smp':True, 'layers':[], 'components':PPC64_TO_PREVENT } },
    ],

    'fr115-openssl-101n':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['NET'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':NET_TO_PREVENT } },
    ], 

    #'vx7-release-Storage-bugfix':[
    #     {'fsl_t2t4':{'cpu':'', 'tool':'diab', 'keywords':[], 'parallelBuild':True,'preventBuild':False, 'smp':False} },
    #],
    #'vx7-imx6-sabreai':[
    #        { 'fsl_imx6':{'cpu':'ARMARCH7', 'tool':'diab', 'keywords':['USB|CAN'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':FS_LAYERS, 'components':COMPS_TO_PREVENT } },       
    #        { 'fsl_imx6':{'cpu':'ARMARCH7', 'tool':'gnu', 'keywords':['USB|CAN'], 'parallelBuild':True, 'preventBuild':True, 'smp':True, 'layers':FS_LAYERS, 'components':COMPS_TO_PREVENT } },  
    #],     
    #'vx7-release':[
    #        { 'fsl_imx6':{'cpu':'ARMARCH7', 'tool':'diab', 'keywords':['USB|CAN'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':FS_LAYERS, 'components':COMPS_TO_PREVENT } },       
    #        { 'fsl_imx6':{'cpu':'ARMARCH7', 'tool':'gnu', 'keywords':['USB|CAN'], 'parallelBuild':True, 'preventBuild':True, 'smp':True, 'layers':FS_LAYERS, 'components':COMPS_TO_PREVENT } },  
    #],           
    }    

"""
    'vx7-firewire':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['IEEE1394'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':FIREWIRE_TO_PREVENT } },
        {'fsl_p1p2':{'cpu':'', 'tool':'diab', 'keywords':['IEEE1394'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':FIREWIRE_TO_PREVENT } },
        {'itl_64':{'cpu':'', 'tool':'gnu', 'keywords':['IEEE1394'], 'parallelBuild':True, 'preventBuild':True, 'smp':True, 'layers':[], 'components':FIREWIRE_TO_PREVENT } },
    ],
            
    'vx7-usb':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['USB|SDMMC'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':USB_TO_PREVENT } },
        {'avnet_mini_itx_7z':{'cpu':'', 'tool':'diab', 'keywords':['SDMMC'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':USB_TO_PREVENT } },
        {'fsl_p1p2':{'cpu':'', 'tool':'diab', 'keywords':['USB|SDMMC'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':USB_TO_PREVENT } },
        #{'itl_64':{'cpu':'', 'tool':'gnu', 'keywords':['USB|SDMMC'], 'parallelBuild':True, 'preventBuild':True, 'smp':True, 'layers':[], 'components':USB_TO_PREVENT } },
    ],
                      
    'jliu1-vadk-f2848':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':[], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':JUNGANG_LAYERS, 'components':JUNGANG_TO_PREVENT } },
#        #{'bsp6x_itl_x86core2':{'cpu':'', 'tool':'gnu', 'keywords':['IEEE1394'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':USB_TO_PREVENT } },
#        #{'itl_64':{'cpu':'', 'tool':'gnu', 'keywords':['IEEE1394'], 'parallelBuild':True, 'preventBuild':True, 'smp':True, 'layers':[], 'components':USB_TO_PREVENT } },
    ],

    'fr55-vx7-quark-dev':[
        {'itl_quark':{'cpu':'', 'tool':'diab', 'keywords':['USB'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':['USB_PCHUDC'], 'components':USB_TO_PREVENT } },
        #{'bsp6x_itl_x86core2':{'cpu':'', 'tool':'gnu', 'keywords':['IEEE1394'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':USB_TO_PREVENT } },
        #{'itl_64':{'cpu':'', 'tool':'gnu', 'keywords':['IEEE1394'], 'parallelBuild':True, 'preventBuild':True, 'smp':True, 'layers':[], 'components':USB_TO_PREVENT } },
    ],
            
    'fr43-crypto-fips':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['NET'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':NET_TO_PREVENT } },
    ], 

    'jli7-V7NET-514':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['NET'], 'parallelBuild':False, 'preventBuild':True, 'smp':False, 'layers':[], 'components':NET_TO_PREVENT } },
    ],      

    'jli7-openssl-1_0_1k':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['NET'], 'parallelBuild':False, 'preventBuild':True, 'smp':False, 'layers':[], 'components':NET_TO_PREVENT } },
    ],      
                                      
    'vx7-openssl-rtp':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['NET'], 'parallelBuild':False, 'preventBuild':True, 'smp':False, 'layers':[], 'components':NET_TO_PREVENT } },
    ],      

    'vx7-netperf-exp':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':[], 'parallelBuild':False, 'preventBuild':True, 'smp':False, 'layers':IPNET_LAYERS, 'components':NET_TO_PREVENT_NONTP } },
    ],      

    'vx7-netperf-exp':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':[], 'parallelBuild':False, 'preventBuild':True, 'smp':False, 'layers':IPNET_LAYERS, 'components':NET_TO_PREVENT_NONTP } },
    ],      

    'jwang9-VXW7-V7NET533':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':[], 'parallelBuild':False, 'preventBuild':True, 'smp':False, 'layers':[], 'components':jwang9_TO_PREVENT } },
    ],      

    'vx7-bspvts-test':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['NET'], 'parallelBuild':False, 'preventBuild':True, 'smp':False, 'layers':[], 'components':['/pkgs/test'] } },
    ],      
                                 
    'vx7-bluetooth':[
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['BLUE'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':BLUETOOTH_TO_PREVENT } },
    ],
            
    'vx7-sja1000':[
        {'fsl_p1p2':{'cpu':'', 'tool':'diab', 'keywords':['CAN'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':CAN_TO_PREVENT } },
        {'fsl_imx6':{'cpu':'', 'tool':'gnu', 'keywords':['CAN'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':[], 'components':CAN_TO_PREVENT } },
    ],      
             
    'vx7-middleware':[
        {'bsp6x_itl_x86coreix':{'cpu':'', 'tool':'gnu', 'keywords':[], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':MIDDLEWARE_LAYERS, 'components':MIDDLEWARE_TO_PREVENT } },
    ],
            
    'vf610-twr':[ # ti_sitara_ctxa8 fsl_vf610twr_ca5
        {'ti_sitara_ctxa8':{'cpu':'', 'tool':'diab', 'keywords':['USB', 'FSLDR|FUNCTION'], 'parallelBuild':True, 'preventBuild':True, 'smp':False, 'layers':VF610_TWR_LAYERS, 'components':vf610_twr_TO_PREVENT } },
    ],  
"""
            
buildServers = (
                #'/net/pek-cc-pb08l/vxtest/vxtest6/vx7dev',
                '/net/pek-cc-pb01l/buildarea1/target/vx7dev',
                #'/net/pek-cc-pb02l/testcloud/vx7dev',
                '/net/pek-cc-pb05l/buildarea1/target/vx7dev',
                #'/net/pek-cc-pb06l/vxusb/usb4/vx7dev',
                #######################
                #'/net/ctu-cc-pb04l/ctu_nightly/vx7dev',
                #'/net/ala-d2121-lx1/home/vx7dev',
                #/net/yow-build36-lx/nightly,
                #######################
                #/net/128.224.157.68/vxtest/vxtest6/simics,
                #/net/128.224.160.44/testcloud/nightly,
                #/net/ctu-hig2/testcloud/nightly,
                #/net/ctu-cc-pb02l/testcloud/nightly,
                #/net/pek-mcbuild1/buildarea3/nightly,
               )

def GetServers():
    return map(lambda x : (x.split('/'))[2], buildServers)


class ConfigParser(object):
    def __init__(self, branch):
        self.branch = branch

    def GetBsps(self):
        """ return a list of bsps """
        bspSet = sets.Set()
        for e in branches[self.branch]:
            bsp = e.keys()[0]
            bspSet.add(bsp)
        return list(bspSet)        
        
                
    def GetBuildParameters(self, bsp):
        """ a list, each member is {key:value} """
        rets = []
        for e in branches[self.branch]:
            b = e.keys()[0]
            d = dict()
            if b == bsp:
                d['bsp'] = b
                d['cpu'] = e[b]['cpu']
                d['tool'] = e[b]['tool']
                d['keywords'] = e[b]['keywords']
                d['parallelBuild'] = e[b]['parallelBuild']
                d['preventBuild'] = e[b]['preventBuild']
                d['smp'] = e[b]['smp']
                d['layers'] = e[b]['layers']
                if e[b].has_key('components'):
                    d['components'] = e[b]['components']
                else:
                    d['components'] = []
                rets.append(d)
        return rets           
                    

class Vx7Config:
    def __init__(self, server):
        self.server = server
        self.serverPathes = self.GetServerPath()
        if server not in self.serverPathes.keys():
            print 'server %s not found at config' % server
            sys.exit(1)
        self.path = self.serverPathes[self.server]
        self.gitDir = ''
        self.buildDir = ''
        self.preventRunDir = ''
        self.preventTmpDir = ''
        self.InitDir()
        

    def GetServerPath(self):
        rets = dict()
        for line in buildServers:
            tokens = line.split('/')
            rets[ tokens[2] ] = '/' + '/'.join( tokens[3:] )
        return rets        


    """
    gitDir = '/buildarea2/lchen3/workspace/vx7-dev-nightly/vxworks'
    buildDirBase = '/buildarea2/lchen3/workspace/vx7-build'
    preventRunDir = '/buildarea1/lchen3/vx7dev'
    preventTmpDir = '/buildarea1/lchen3/tmp'
    """
    def GetDirs(self):
        return self.gitDir, self.buildDir, self.preventRunDir, self.preventTmpDir
        
    def GetGitDir(self):
        return self.gitDir

    def GetBuildDir(self):
        return self.buildDir

    def GetPreventRunDir(self):
        return self.preventRunDir

    def GetPreventTmpDir(self):
        return self.preventTmpDir

    def InitDir(self):
        self.gitDir = self.__CreateDir(self.path + '/vx-git')
        self.buildDir = self.__CreateDir(self.path + '/vx-build')
        self.preventRunDir = os.path.dirname(self.path) + '/nightly'
        self.preventTmpDir = self.__CreateDir(self.path + '/prevent-tmp')
                                        
    def __CreateDir(self, path):
        if not os.path.exists(path):
            ret = getoutput('mkdir %s' % path)
        return path
        
    def SetupEnv(self):
        # coverity record
        os.environ['PREVENT_RUN_DIR'] = self.preventRunDir
        # coverity tmp
        os.environ['TMPDIR'] = self.preventTmpDir
        # coverity env variable
        os.environ['CHECKER_OVERRIDE'] = "--checker-option CHECKED_RETURN:stat_threshold:0"        
        # coverity path
        preventPath = '/folk/beijing/tools/Coverity/Prevent'
        newPath = os.environ['PATH'] + ':' + preventPath
        os.environ['PATH'] = newPath  
        # buildwarn path
        buildwarnPath = '/folk/lchen3/tools'
        newPath = os.environ['PATH'] + ':' + buildwarnPath
        os.environ['PATH'] = newPath
    

def GetMgrEmail(author):
    contact = Contact('contact.txt')
    return contact.GetMgrEmail(author)

    
def GetCorpEmail(author):
    contact = Contact('contact.txt')
    return contact.GetEmail(author)
    #return author + '@windriver.com'
