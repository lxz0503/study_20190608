# Kong config

# for centralized img building at several servers
kongBuildServers = {
                    #'pek-cc-pb02l.wrs.com' : { 'gitDir' : '/testcloud/svc-cmnet/vxworks' },
                    #'pek-cc-pb01l.wrs.com' : { 'gitDir' : '/buildarea1/svc-cmnet/vxworks' },
                    'pek-vx-nightly3' : { 'gitDir' : '/buildarea1/svc-cmnet/vxworks' },
                    'pek-sec-kong-02' : { 'gitDir' : '/workspace/svc-cmnet/vxworks' },
                   }

kongImageDir = 'pek-sec-kong-02:/workspace/svc-cmnet/IMAGES' # host name should be without .wrs.com

# the following parameter: if False, force to skip the centralized image building
# and should keep the parameter name unique in this file
# spin build & test can only be supported at centralized img building mode
# for git branch test, please set to False
kongBuildFirstFlag = True

# the flag ON will enter debugging mode
kongDebugOn = True

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
        'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks-7-r2',
        'spinToDir' : '/home/windriver/CISPIN',
        'profile' : 'VxWorks_7_Plus_Platform__Time_Based_BASE',
        'gitPathRef' : '/home/windriver/vxworks-latest',
        'spinBranch' : 'vx7-integration',   # the branch to get Kong test framawork and test cases
     },
     
    'SPIN' : {
        'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks-7-r2',
        'spinToDir' : '/home/windriver/SPIN',
        'profile' : 'VxWorks_7_Plus_Platform__Time_Based_BASE',
        'gitPathRef' : '/home/windriver/vxworks-latest',
        'spinBranch' : 'vx7-integration',   # the branch to get Kong test framawork and test cases
     },

    '653SPIN' : {
        'fromBaseDir' : '/net/pek-cdftp/pek-cdftp1/ftp/r1/vxworks/vxworks653-4',
        'spinToDir' : '/workspace/svc-cmnet/653SPIN',
        'profile' : 'VxWorks_7_Plus_Platform__Time_Based_BASE',
        'gitPathRef' : '/workspace/svc-cmnet/vxworks-latest',
        'spinBranch' : 'vx7-SR0540-features', # the branch to get Kong test framawork and test cases
     },
}
     
# Jenkins for Kong
kongJenkins = 'http://pek-testharness-s1.wrs.com:8080'
kongUser = 'svc-cmnet'
kongPassword = 'december2012!'

kongBuildJob = 'ci-build-slave' # the same as try-ci-build
kongBuildFailureRatio = 0.9
kongTestJobPrefix = 'ut-vxsim-'

kongAdminEmail = 'peng.bi@windriver.com; libo.chen@windriver.com; haixiao.yan@windriver.com; li.wan@windriver.com; xiaozhan.li@windriver.com; roger.boden@windriver.com; kenneth.jonsson@windriver.com; markus.carlstedt@windriver.com; dan.krejsa@windriver.com;'

kongReportEmail = 'dong.liu@windriver.com; peng.bi@windriver.com; ENG-VxNET-China@windriver.com; libo.chen@windriver.com; haixiao.yan@windriver.com; li.wan@windriver.com; xiaozhan.li@windriver.com; yanyan.liu@windriver.com;'
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
            "CRYPTO-FIPS-140-2",
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
            "OPENSSL_FIPS",
            "CORE_SAFETY",
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
            #"OPENSSL_FIPS",
            #'RTNET',
           ]
"""
kongTestServers = {
              #"ROHC_ESP" : 'ci-rerun-test-rm',
              #"ROHC_IP" : 'ci-rerun-test-rm',
              #"ROHC_TCP" : 'ci-rerun-test-rm',
              #"ROHC_UDP" : 'ci-rerun-test-rm',
              #"ROHC_UNCMP" : 'ci-rerun-test-rm',
              #"NAT" : 'ci-rerun-test-rm',
              #"DHCP6" : 'ci-rerun-test-rm',
              #"QOS" : 'ci-rerun-test-rm',
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
                      #'vx7-SR0500-features',
                      'SPIN',       # release spin
                      'CISPIN',     # vx7-integration spin
                      '653SPIN',    # 653 spin
                      'LLVMSPIN',   # LLVM spin, i.e. 1032
                     )
                     
# the branch needs LTAF-based nightly report
kongReportBranches = (
    'vx7-integration',
    #'vx7-SR0500-features',
    )

# spin's Rally requirement, which stores at LTAF
kongLTAFRequirements = {
        'vx7-CR0501-features' : 'US95057',
    }

# the Jenkins jobs need LTAF-based nightly report    
kongReportJenkinsJobs = (
    'ut-vxsim-CRYPTO',
    'ut-vxsim-CRYPTO-FIPS-140-2',
    'ut-vxsim-DHCP',
    'ut-vxsim-DHCP6',
    'ut-vxsim-DNSC',
    'ut-vxsim-FIREWALL',
    'ut-vxsim-FTP',
    'ut-vxsim-IKE-1',
    'ut-vxsim-IKE-2',
    'ut-vxsim-IKE-ADVANCED-1',
    'ut-vxsim-IKE-ADVANCED-2',
    'ut-vxsim-IKE-ADVANCED-3',
    'ut-vxsim-IKE-ADVANCED-4',
    'ut-vxsim-IKE-ADVANCED-5',
    'ut-vxsim-IKE-ALGORITHMS-1',
    'ut-vxsim-IKE-ALGORITHMS-2',
    'ut-vxsim-IKE-ALGORITHMS-3',
    'ut-vxsim-IKE-AUTHENTICATION',
    'ut-vxsim-IKE-BASIC-1',
    'ut-vxsim-IKE-BASIC-2',
    'ut-vxsim-IKE-DAEMON-1',
    'ut-vxsim-IKE-DAEMON-2',
    'ut-vxsim-IKE-RACOON',
    'ut-vxsim-IKE-ROHC-IPSEC',
    'ut-vxsim-IKE-IPEAP',
    'ut-vxsim-IKE-SETTINGS',
    'ut-vxsim-IPNET-1',
    'ut-vxsim-IPNET-2',
    'ut-vxsim-IPNET-IPSEC',
    'ut-vxsim-IPSEC-IPCRYPTO-1',
    'ut-vxsim-IPSEC-IPCRYPTO-2',
    'ut-vxsim-IPSEC-IPCRYPTO-3',
    'ut-vxsim-IPSEC-IPCRYPTO-4',    
    'ut-vxsim-L2TP',
    'ut-vxsim-MCP',
    'ut-vxsim-NAT',
    'ut-vxsim-NET_VLAN',
    'ut-vxsim-NTP',
    'ut-vxsim-PPP',
    'ut-vxsim-QOS-1',
    'ut-vxsim-QOS-2',
    'ut-vxsim-RADIUS',
    'ut-vxsim-RIP',
    'ut-vxsim-RIPNG',
    'ut-vxsim-ROHC_ESP',
    'ut-vxsim-ROHC_IP',
    'ut-vxsim-ROHC_TCP',
    'ut-vxsim-ROHC_UDP',
    'ut-vxsim-ROHC_UNCMP',
    'ut-vxsim-RTNET',
    'ut-vxsim-SECEVENT',
    'ut-vxsim-SCTP-1',
    'ut-vxsim-SCTP-2',
    'ut-vxsim-SNMP',
    'ut-vxsim-SNTP_CLIENT',
    'ut-vxsim-SNTP_SERVER',
    'ut-vxsim-SSH',
    'ut-vxsim-SSHCLIENT',
    'ut-vxsim-SSL',
    'ut-vxsim-SYSVIEW',
    'ut-vxsim-TFTP',
    'ut-vxsim-USERAUTH_LDAP',
    'ut-vxsim-USERDB',
    'ut-vxsim-VRRP',
    'ut-vxsim-OPENSSL_FIPS',
    'ut-vxsim-CORE_SAFETY',
    )

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
    
