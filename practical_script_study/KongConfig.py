# Kong config

# for centralized img building at several servers
# pek-vx-nightly slave configuration:
#   Name: pek-vx-nightly
#   Remote root directory: pek-vx-nightly
#   Labels: kong-build
#   Credentials: svc-cmnet/******

kongBuildServers = {
                    #'pek-cc-pb02l.wrs.com' : { 'gitDir' : '/testcloud/svc-cmnet/vxworks' },
                    #'pek-cc-pb01l.wrs.com' : { 'gitDir' : '/buildarea1/svc-cmnet/vxworks' },
                    #'pek-vx-nightly3' : { 'gitDir' : '/buildarea1/svc-cmnet/vxworks' }, 
                    #'pek-sec-kong-02' : { 'gitDir' : '/workspace/svc-cmnet/vxworks' },
                    'pek-vx-nwk1' : { 'gitDir' : '/buildarea1/svc-cmnet/vxworks' },   # NEED TO CHANGE
                   }

# NEED TO CHANGE
#kongImageDir = 'pek-sec-kong-02:/workspace/svc-cmnet/IMAGES' # host name should be without .wrs.com
kongImageDir = 'pek-vx-nwk1:/buildarea1/svc-cmnet/IMAGES' # host name should be without .wrs.com

# the following parameter: if False, force to skip the centralized image building
# and should keep the parameter name unique in this file
# spin build & test can only be supported at centralized img building mode
# for git branch test, please set to False
kongBuildFirstFlag = True

# the flag ON will enter debugging mode
kongDebugOn = False

def IsBuildFirst():
    if kongBuildFirstFlag:
        return True
    else:
        return False
        
def GetGitDir(host):
    return kongBuildServers[host]['gitDir']

def GetAllGitDirs():
    rets = []
    for host in kongBuildServers:
        rets.append('/net/' + host + GetGitDir(host))
    return ' '.join(rets)

def GetServerName(nfsGitPath):
    # assume that git path is like /net/server_name/git_path
    return nfsGitPath.split('/')[2]

def GetGitPath(nfsGitPath):
    # assume that git path is like /net/server_name/git_path
    serverName = GetServerName(nfsGitPath)
    return nfsGitPath.replace('/net/%s' % serverName, '')
     
def GetImageServer():
    return kongImageDir.split(':')[0]

def GetImageDir():
    return kongImageDir.split(':')[1]

# install spin & kong patch for ci-branch spin or release spin
# spinToDir must have the same server as kongImageDir
spinConfig = {
    'CISPIN' : {
        # 'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks-7-r2',
        'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/helix/vxworks-std',
        'spinToDir' : '/buildarea1/svc-cmnet/CISPIN',          # NEED TO CHANGE
        'profile' : 'VxWorks_7_Plus_Platform__Time_Based_BASE',
        'gitPathRef' : '/buildarea1/svc-cmnet/vxworks-latest', # NEED TO CHANGE
        'spinBranch' : 'vx7-integration',   # the branch to get Kong test framawork and test cases
     },
     
    'SPIN' : {
        'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/helix/vxworks-std',
        # 'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks-7-r2',
        'spinToDir' : '/buildarea1/svc-cmnet/SPIN',             # NEED TO CHANGE
        'profile' : 'VxWorks_7_Plus_Platform__Time_Based_BASE',
        'gitPathRef' : '/buildarea1/svc-cmnet/vxworks-latest',  # NEED TO CHANGE
        'spinBranch' : 'vx7-integration',   # the branch to get Kong test framawork and test cases
     },

    'HELIXSPIN' : {
        'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks-platform', # NEED TO CHANGE
        'spinToDir' : '/buildarea1/svc-cmnet/HELIXSPIN',             # NEED TO CHANGE
        'profile' : 'VxWorks_7_Plus_Platform__Time_Based_BASE',
        'gitPathRef' : '/buildarea1/svc-cmnet/vxworks-latest',  # NEED TO CHANGE
        'spinBranch' : 'vx7-integration',   # the branch to get Kong test framawork and test cases
     },

    'HELIXCISPIN' : {
        'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks-platform', # NEED TO CHANGE
        'spinToDir' : '/buildarea1/svc-cmnet/HELIXCISPIN',             # NEED TO CHANGE
        'profile' : 'VxWorks_7_Plus_Platform__Time_Based_BASE',
        'gitPathRef' : '/buildarea1/svc-cmnet/vxworks-latest',  # NEED TO CHANGE
        'spinBranch' : 'vx7-integration',   # the branch to get Kong test framawork and test cases
     },
              
    '653SPIN' : {
        'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks653-4',
        'spinToDir' : '/buildarea1/svc-cmnet/653SPIN',          # NEED TO CHANGE
        'profile' : 'VxWorks_7_Plus_Platform__Time_Based_BASE',
        'gitPathRef' : '/buildarea1/svc-cmnet/vxworks-latest',  # NEED TO CHANGE
        'spinBranch' : 'vx7-SR0540-features', # the branch to get Kong test framawork and test cases
     },
}
     
# Jenkins for Kong
kongJenkins = 'http://pek-testharness-s1.wrs.com:8080'
kongUser = 'svc-cmnet'
kongPassword = 'december2012!'

kongBuildJob = 'ci-build-slave' # the same as try-ci-build
kongBuildFailureRatio = 0.9
kongBuildFailureNum = 8
kongTestJobPrefix = 'ut-vxsim-'

kongAdminEmail = 'peng.bi@windriver.com; libo.chen@windriver.com; dapeng.zhang@windriver.com;xiaozhan.li@windriver.com; roger.boden@windriver.com; kenneth.jonsson@windriver.com; markus.carlstedt@windriver.com; dan.krejsa@windriver.com;'

kongReportEmail = 'dong.liu@windriver.com; peng.bi@windriver.com; ENG-VxNET-China@windriver.com; libo.chen@windriver.com; dapeng.zhang@windriver.com; xiaozhan.li@windriver.com; yanyan.liu@windriver.com;'
# vx7-nightly-test@list-int.wrs.com; 

# 3 level rerunning controls: 
#   kongRerunFlag - rerun or not
#    one is at job level (rerun will take place if no passed test cases for this job
#    the other is at test cases level. If kongRerunFailedJob == True, then failed test cases will be rerun
kongRerunFlag = True
kongRerunFailedJob = True   
kongRerunTestNum = 2

kongModules = [
            "CRYPTO",
            "DHCP",
            "DHCP6",
            "DNSC",
            "FIREWALL",
            "FTP",
            "IKE",
            "IKE-ADVANCED",
            "IKE-ALGORITHMS",
            "IKE-AUTHENTICATION",
            "IKE-BASIC",
            "IKE-DAEMON",
            "IKE-IPEAP",
            "IKE-RACOON",
            "IKE-ROHC-IPSEC",
            "IKE-SETTINGS",
            "IPNET",
            "IPNET-IPSEC",
            "IPSEC-IPCRYPTO",
            "L2TP",
            "MCP",
            "NAT",
            "NET_VLAN",
            "NTP",
            "PPP",
            "QOS",
            "RADIUS",
            "RIP",
            "RIPNG",
            "ROHC_ESP",
            "ROHC_IP",
            "ROHC_TCP",
            "ROHC_UDP",
            "ROHC_UNCMP",
            'RTNET',
            'SECEVENT',
            "SCTP",
            "SNMP",
            "SNTP_CLIENT",
            "SNTP_SERVER",
            "SSH",
            "SSHCLIENT",
            "SSL",
            "SYSVIEW",
            "TFTP",
            "USERAUTH_LDAP",
            "USERDB",
            "VRRP",
            "CORE_SAFETY",
            "EDOOM",
            "8021X",
            "SOCKTEST",
            "BOND",
           ]
"""
# typical modules for debugging build & test 
kongModules = [
            # at pek-sec-kong-02
            #"DHCP6",
            "DNSC",
            #"IKE-ADVANCED",
            #"IPNET-IPSEC",
            #"ROHC_ESP",
            #"VRRP",
            #"SNTP_SERVER",
            #"SSH",
            #"SSHCLIENT",
            #"SSL",
            #"USERAUTH_LDAP",
            # at pek-vx-nightly3
            #'RTNET',
           ]
"""

# this KongBuildModules is used for building modules 
# and it should have the same modules for vxsim_linux bsp
# it is introduced to avoid modifying too many codes
"""
kongBuildModules = {
    'vxsim_linux': 
            [ 
            "DNSC",
            'RTNET',
           ],

    'fsl_imx6' : 
           [ 'RTNET', 
             #'RTNET_RTP',
           ],

    'itl_generic' :
           [ #'RTNET', 
             'RTNET_RTP',
           ],
}
"""

kongBuildModules = {
    'vxsim_linux': 
            [ 
            "CRYPTO",
            "DHCP",
            "DHCP6",
            "DNSC",
            "FIREWALL",
            "FTP",
            "IKE",
            "IKE-ADVANCED",
            "IKE-ALGORITHMS",
            "IKE-AUTHENTICATION",
            "IKE-BASIC",
            "IKE-DAEMON",
            "IKE-IPEAP",
            "IKE-RACOON",
            "IKE-ROHC-IPSEC",
            "IKE-SETTINGS",
            "IPNET",
            "IPNET-IPSEC",
            "IPSEC-IPCRYPTO",
            "L2TP",
            "MCP",
            "NAT",
            "NET_VLAN",
            "NTP",
            "PPP",
            "QOS",
            "RADIUS",
            "RIP",
            "RIPNG",
            "ROHC_ESP",
            "ROHC_IP",
            "ROHC_TCP",
            "ROHC_UDP",
            "ROHC_UNCMP",
            'RTNET',
            'SECEVENT',
            "SCTP",
            "SNMP",
            "SNTP_CLIENT",
            "SNTP_SERVER",
            "SSH",
            "SSHCLIENT",
            "SSL",
            "SYSVIEW",
            "TFTP",
            "USERAUTH_LDAP",
            "USERDB",
            "VRRP",
            "CORE_SAFETY",
            "EDOOM",
            "8021X",
            "SOCKTEST",
            "BOND",
           ],

    'fsl_imx6' : 
           [ 'RTNET', 
             'RTNET_RTP',
           ],

    'itl_generic' :
           [ 'RTNET', 
             'RTNET_RTP',
           ],
}

def GetSupportedBsps():
    return kongBuildModules.keys()

kongTestServers = {
              #"ROHC_ESP" : 'ci-rerun-test-rm',
              #"ROHC_IP" : 'ci-rerun-test-rm',
              #"ROHC_TCP" : 'ci-rerun-test-rm',
              #"ROHC_UDP" : 'ci-rerun-test-rm',
              #"ROHC_UNCMP" : 'ci-rerun-test-rm',
              #"NAT" : 'ci-rerun-test-rm',
              #"DHCP6" : 'ci-rerun-test-rm',
              #"QOS" : 'ci-rerun-test-rm',
              'SCTP' : 'ci-rerun-test-rm',
              }

# disable per checkin test for vxworks network
# since we will use nightly test for it
branchesToMonitor = [
                     #'vx7-cert',
                     #'vx7-net',
                     #'vx7-release',
                    ]

# the branch that allow to run Kong
branchesForNightly = (
                      'vx7-integration',
                      'vx7-SR0660-features',
                      'rboden-f10798-3',
                      'SPIN',       # release spin
                      'CISPIN',     # vx7-integration spin
                      'HELIXSPIN',  # helix spin
                      'HELIXCISPIN',  # helix branch spin
                      '653SPIN',    # 653 spin
                      'LLVMSPIN',   # LLVM spin, i.e. 1032
                     )
                     
# the branch needs LTAF-based nightly report
kongReportBranches = (
    'vx7-integration',
    'vx7-SR0660-features',
    )

# spin's Rally requirement, which stores at LTAF
kongLTAFRequirements = {
        'vx7-CR0501-features' : 'US95057',
    }

kongReportFilteredOutTestCases = (
    #'ipnet.route.fragmenting_fragment',     # unstable, not a defect like V7NET-909
    #'ipnet.ip4.mroute',                     # V7NET-1079
    #'ipnet.ip6.privacy_extension',          # unstable
    #'ipdhcp6.assign.info_only_client_refresh', # unstable
    #'ipppp.pppmp.local_mpthree',            # unstable
    #'iprohc_ip.iprohc_ip.mine_enc_pppoe',   # V7NET-1081 (for -k only)
    #'ipsctp.sctp.c0190api_opt_seqpacket',   # V7NET-1082
    #'ipsntp.server.multicast',              # V7NET-1084
    #'ipsntp.api.multicast',                 # V7NET-1084
    #'ipfirewall.ipfilter.ipsecstate',       # v6 failed
    #'ipfirewall.ipfilter.return_icmp',      # failed
    #'ipike.basic.lost_delete_notification2', # V7SEC-316
    )
    
