import requests
import sys
import time
from commands import getoutput
from datetime import datetime

from jenkins import Jenkins, NotFoundException, LAUNCHER_SSH

kongDevJenkins  = 'http://pek-testharness-s1.wrs.com:8080'
kongDevUser     = 'svc-cmnet'
kongDevPassword = 'december2012!'

tasks = { 'itl_generic': { 'DNSC': [ ['build', 'helix-build-slave', 5744, u'SUCCESS'],
                             ['test', 'helix-test-itl_generic', 2541, u'SUCCESS'],
                             ['report', 'helix-report', 5216, u'SUCCESS'],
                             ['retest', 'na', 'na', 'SUCCESS'],
                             ['rereport', 'na', 'na', 'SUCCESS']],
                   'FTP': [ ['build', 'helix-build-slave', 5748, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 2542, u'SUCCESS'],
                            ['report', 'helix-report', 5217, u'SUCCESS'],
                            ['retest', 'na', 'na', 'SUCCESS'],
                            ['rereport', 'na', 'na', 'SUCCESS']],
                   'IKE-ADVANCED': [ ['build', 'helix-build-slave', 5752, u'SUCCESS'],
                                     ['test', 'helix-test-itl_generic', 2543, u'SUCCESS'],
                                     ['report', 'helix-report', 5222, u'SUCCESS'],
                                     ['retest', 'na', 'na', 'SUCCESS'],
                                     ['rereport', 'na', 'na', 'SUCCESS']],
                   'IPNET': [ ['build', 'helix-build-slave', 5756, u'SUCCESS'],
                              ['test', 'helix-test-itl_generic', 2544, u'SUCCESS'],
                              ['report', 'helix-report', 5231, u'SUCCESS'],
                              ['retest', 'na', 'na', 'SUCCESS'],
                              ['rereport', 'na', 'na', 'SUCCESS']],
                   'IPNET-IPSEC': [ ['build', 'helix-build-slave', 5760, u'SUCCESS'],
                                    ['test', 'helix-test-itl_generic', 2545, u'SUCCESS'],
                                    ['report', 'helix-report', 5233, u'SUCCESS'],
                                    ['retest', 'na', 'na', 'SUCCESS'],
                                    ['rereport', 'na', 'na', 'SUCCESS']],
                   'MCP': [ ['build', 'helix-build-slave', 5762, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 2546, u'SUCCESS'],
                            ['report', 'helix-report', 5234, u'SUCCESS'],
                            ['retest', 'na', 'na', 'SUCCESS'],
                            ['rereport', 'na', 'na', 'SUCCESS']],
                   'NET_VLAN': [ ['build', 'helix-build-slave', 5764, u'SUCCESS'],
                                 ['test', 'helix-test-itl_generic', 2547, u'SUCCESS'],
                                 ['report', 'helix-report', 5236, u'SUCCESS'],
                                 ['retest', 'na', 'na', 'SUCCESS'],
                                 ['rereport', 'na', 'na', 'SUCCESS']],
                   'NTP': [ ['build', 'helix-build-slave', 5766, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 2548, u'SUCCESS'],
                            ['report', 'helix-report', 5241, u'SUCCESS'],
                            ['retest', 'na', 'na', 'SUCCESS'],
                            ['rereport', 'na', 'na', 'SUCCESS']],
                   'QOS': [ ['build', 'helix-build-slave', 5768, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 2549, u'FAILURE'],
                            ['report', 'helix-report', 5245, u'SUCCESS'],
                            ['retest', 'helix-test-itl_generic', 2551, u'SUCCESS'],
                            ['rereport', 'helix-report', 5250, u'SUCCESS']],
                   'RADIUS': [ ['build', 'helix-build-slave', 5770, u'SUCCESS'],
                               ['test', 'helix-test-itl_generic', 2550, u'SUCCESS'],
                               ['report', 'helix-report', 5248, u'SUCCESS'],
                               ['retest', 'na', 'na', 'SUCCESS'],
                               ['rereport', 'na', 'na', 'SUCCESS']],
                   'ROHC_IP': [ ['build', 'helix-build-slave', 5772, u'SUCCESS'],
                                ['test', 'helix-test-itl_generic', 2552, u'SUCCESS'],
                                ['report', 'helix-report', 5251, u'SUCCESS'],
                                ['retest', 'na', 'na', 'SUCCESS'],
                                ['rereport', 'na', 'na', 'SUCCESS']],
                   'ROHC_UDP': [ ['build', 'helix-build-slave', 5774, u'SUCCESS'],
                                 ['test', 'helix-test-itl_generic', 2553, u'SUCCESS'],
                                 ['report', 'helix-report', 5252, u'SUCCESS'],
                                 ['retest', 'na', 'na', 'SUCCESS'],
                                 ['rereport', 'na', 'na', 'SUCCESS']],
                   'SECEVENT': [ ['build', 'helix-build-slave', 5776, u'SUCCESS'],
                                 ['test', 'helix-test-itl_generic', 2554, u'SUCCESS'],
                                 ['report', 'helix-report', 5253, u'SUCCESS'],
                                 ['retest', 'na', 'na', 'SUCCESS'],
                                 ['rereport', 'na', 'na', 'SUCCESS']],
                   'SSH': [ ['build', 'helix-build-slave', 5778, u'SUCCESS'],
                            ['test', 'helix-test-itl_generic', 2555, u'SUCCESS'],
                            ['report', 'helix-report', 5254, u'SUCCESS'],
                            ['retest', 'na', 'na', 'SUCCESS'],
                            ['rereport', 'na', 'na', 'SUCCESS']],
                   'SSHCLIENT': [ ['build', 'helix-build-slave', 5780, u'SUCCESS'],
                                  ['test', 'helix-test-itl_generic', 2556, u'FAILURE'],
                                  ['report', 'helix-report', 5255, u'SUCCESS'],
                                  ['retest', 'helix-test-itl_generic', 2558, u'SUCCESS'],
                                  ['rereport', 'helix-report', 5257, u'SUCCESS']],
                   'USERAUTH_LDAP': [ ['build', 'helix-build-slave', 5781, u'SUCCESS'],
                                      ['test', 'helix-test-itl_generic', 2557, u'SUCCESS'],
                                      ['report', 'helix-report', 5256, u'SUCCESS'],
                                      ['retest', 'na', 'na', 'SUCCESS'],
                                      ['rereport', 'na', 'na', 'SUCCESS']]},
  'nxp_layerscape_a72': { 'FIREWALL': [ ['build', 'helix-build-slave', 5743, u'SUCCESS'],
                                        ['test', 'helix-test-nxp_layerscape_a72', 1217, u'SUCCESS'],
                                        ['report', 'helix-report', 5218, u'SUCCESS'],
                                        ['retest', 'na', 'na', 'SUCCESS'],
                                        ['rereport', 'na', 'na', 'SUCCESS']],
                          'IKE-BASIC': [ ['build', 'helix-build-slave', 5745, u'SUCCESS'],
                                         ['test', 'helix-test-nxp_layerscape_a72', 1218, u'SUCCESS'],
                                         ['report', 'helix-report', 5221, u'SUCCESS'],
                                         ['retest', 'na', 'na', 'SUCCESS'],
                                         ['rereport', 'na', 'na', 'SUCCESS']],
                          'IKE-DAEMON': [ ['build', 'helix-build-slave', 5747, u'SUCCESS'],
                                          ['test', 'helix-test-nxp_layerscape_a72', 1219, u'SUCCESS'],
                                          ['report', 'helix-report', 5226, u'SUCCESS'],
                                          ['retest', 'na', 'na', 'SUCCESS'],
                                          ['rereport', 'na', 'na', 'SUCCESS']],
                          'IKE-ROHC-IPSEC': [ ['build', 'helix-build-slave', 5749, u'SUCCESS'],
                                              ['test', 'helix-test-nxp_layerscape_a72', 1220, u'SUCCESS'],
                                              ['report', 'helix-report', 5228, u'SUCCESS'],
                                              ['retest', 'na', 'na', 'SUCCESS'],
                                              ['rereport', 'na', 'na', 'SUCCESS']],
                          'IPSEC-IPCRYPTO': [ ['build', 'helix-build-slave', 5751, u'SUCCESS'],
                                              ['test', 'helix-test-nxp_layerscape_a72', 1221, u'SUCCESS'],
                                              ['report', 'helix-report', 5238, u'SUCCESS'],
                                              ['retest', 'na', 'na', 'SUCCESS'],
                                              ['rereport', 'na', 'na', 'SUCCESS']],
                          'RIP': [ ['build', 'helix-build-slave', 5753, u'SUCCESS'],
                                   ['test', 'helix-test-nxp_layerscape_a72', 1222, u'SUCCESS'],
                                   ['report', 'helix-report', 5239, u'SUCCESS'],
                                   ['retest', 'na', 'na', 'SUCCESS'],
                                   ['rereport', 'na', 'na', 'SUCCESS']],
                          'RIPNG': [ ['build', 'helix-build-slave', 5755, u'SUCCESS'],
                                     ['test', 'helix-test-nxp_layerscape_a72', 1223, u'SUCCESS'],
                                     ['report', 'helix-report', 5240, u'SUCCESS'],
                                     ['retest', 'na', 'na', 'SUCCESS'],
                                     ['rereport', 'na', 'na', 'SUCCESS']],
                          'SCTP': [ ['build', 'helix-build-slave', 5757, u'SUCCESS'],
                                    ['test', 'helix-test-nxp_layerscape_a72', 1224, u'SUCCESS'],
                                    ['report', 'helix-report', 5243, u'SUCCESS'],
                                    ['retest', 'na', 'na', 'SUCCESS'],
                                    ['rereport', 'na', 'na', 'SUCCESS']],
                          'SYSVIEW': [ ['build', 'helix-build-slave', 5759, u'SUCCESS'],
                                       ['test', 'helix-test-nxp_layerscape_a72', 1225, u'SUCCESS'],
                                       ['report', 'helix-report', 5246, u'SUCCESS'],
                                       ['retest', 'na', 'na', 'SUCCESS'],
                                       ['rereport', 'na', 'na', 'SUCCESS']]},
  'xlnx_zynqmp': { 'CRYPTO': [ ['build', 'helix-build-slave', 5742, u'SUCCESS'],
                               ['test', 'helix-test-xlnx_zynqmp', 1653, u'SUCCESS'],
                               ['report', 'helix-report', 5215, u'SUCCESS'],
                               ['retest', 'na', 'na', 'SUCCESS'],
                               ['rereport', 'na', 'na', 'SUCCESS']],
                   'DHCP': [ ['build', 'helix-build-slave', 5746, u'SUCCESS'],
                             ['test', 'helix-test-xlnx_zynqmp', 1654, u'SUCCESS'],
                             ['report', 'helix-report', 5219, u'SUCCESS'],
                             ['retest', 'na', 'na', 'SUCCESS'],
                             ['rereport', 'na', 'na', 'SUCCESS']],
                   'DHCP6': [ ['build', 'helix-build-slave', 5750, u'SUCCESS'],
                              ['test', 'helix-test-xlnx_zynqmp', 1655, u'FAILURE'],
                              ['report', 'helix-report', 5220, u'SUCCESS'],
                              ['retest', 'helix-test-xlnx_zynqmp', 1657, u'SUCCESS'],
                              ['rereport', 'helix-report', 5224, u'SUCCESS']],
                   'IKE-AUTHENTICATION': [ ['build', 'helix-build-slave', 5754, u'SUCCESS'],
                                           ['test', 'helix-test-xlnx_zynqmp', 1656, u'SUCCESS'],
                                           ['report', 'helix-report', 5223, u'SUCCESS'],
                                           ['retest', 'na', 'na', 'SUCCESS'],
                                           ['rereport', 'na', 'na', 'SUCCESS']],
                   'IKE-RACOON': [ ['build', 'helix-build-slave', 5758, u'SUCCESS'],
                                   ['test', 'helix-test-xlnx_zynqmp', 1658, u'SUCCESS'],
                                   ['report', 'helix-report', 5225, u'SUCCESS'],
                                   ['retest', 'na', 'na', 'SUCCESS'],
                                   ['rereport', 'na', 'na', 'SUCCESS']],
                   'IKE-SETTINGS': [ ['build', 'helix-build-slave', 5761, u'SUCCESS'],
                                     ['test', 'helix-test-xlnx_zynqmp', 1659, u'SUCCESS'],
                                     ['report', 'helix-report', 5227, u'SUCCESS'],
                                     ['retest', 'na', 'na', 'SUCCESS'],
                                     ['rereport', 'na', 'na', 'SUCCESS']],
                   'NAT': [ ['build', 'helix-build-slave', 5763, u'SUCCESS'],
                            ['test', 'helix-test-xlnx_zynqmp', 1660, u'SUCCESS'],
                            ['report', 'helix-report', 5229, u'SUCCESS'],
                            ['retest', 'na', 'na', 'SUCCESS'],
                            ['rereport', 'na', 'na', 'SUCCESS']],
                   'PPP': [ ['build', 'helix-build-slave', 5765, u'SUCCESS'],
                            ['test', 'helix-test-xlnx_zynqmp', 1661, u'SUCCESS'],
                            ['report', 'helix-report', 5230, u'SUCCESS'],
                            ['retest', 'na', 'na', 'SUCCESS'],
                            ['rereport', 'na', 'na', 'SUCCESS']],
                   'ROHC_ESP': [ ['build', 'helix-build-slave', 5767, u'SUCCESS'],
                                 ['test', 'helix-test-xlnx_zynqmp', 1662, u'SUCCESS'],
                                 ['report', 'helix-report', 5232, u'SUCCESS'],
                                 ['retest', 'na', 'na', 'SUCCESS'],
                                 ['rereport', 'na', 'na', 'SUCCESS']],
                   'ROHC_TCP': [ ['build', 'helix-build-slave', 5769, u'SUCCESS'],
                                 ['test', 'helix-test-xlnx_zynqmp', 1663, u'SUCCESS'],
                                 ['report', 'helix-report', 5235, u'SUCCESS'],
                                 ['retest', 'na', 'na', 'SUCCESS'],
                                 ['rereport', 'na', 'na', 'SUCCESS']],
                   'SNMP': [ ['build', 'helix-build-slave', 5771, u'SUCCESS'],
                             ['test', 'helix-test-xlnx_zynqmp', 1664, u'SUCCESS'],
                             ['report', 'helix-report', 5237, u'SUCCESS'],
                             ['retest', 'na', 'na', 'SUCCESS'],
                             ['rereport', 'na', 'na', 'SUCCESS']],
                   'SNTP_CLIENT': [ ['build', 'helix-build-slave', 5773, u'SUCCESS'],
                                    ['test', 'helix-test-xlnx_zynqmp', 1665, u'SUCCESS'],
                                    ['report', 'helix-report', 5242, u'SUCCESS'],
                                    ['retest', 'na', 'na', 'SUCCESS'],
                                    ['rereport', 'na', 'na', 'SUCCESS']],
                   'SSL': [ ['build', 'helix-build-slave', 5775, u'SUCCESS'],
                            ['test', 'helix-test-xlnx_zynqmp', 1666, u'SUCCESS'],
                            ['report', 'helix-report', 5244, u'SUCCESS'],
                            ['retest', 'na', 'na', 'SUCCESS'],
                            ['rereport', 'na', 'na', 'SUCCESS']],
                   'TFTP': [ ['build', 'helix-build-slave', 5777, u'SUCCESS'],
                             ['test', 'helix-test-xlnx_zynqmp', 1667, u'SUCCESS'],
                             ['report', 'helix-report', 5247, u'SUCCESS'],
                             ['retest', 'na', 'na', 'SUCCESS'],
                             ['rereport', 'na', 'na', 'SUCCESS']],
                   'USERDB': [ ['build', 'helix-build-slave', 5779, u'SUCCESS'],
                               ['test', 'helix-test-xlnx_zynqmp', 1668, u'SUCCESS'],
                               ['report', 'helix-report', 5249, u'SUCCESS'],
                               ['retest', 'na', 'na', 'SUCCESS'],
                               ['rereport', 'na', 'na', 'SUCCESS']]}}

class KongJenkins:
    def __init__(self):
        self.s = Jenkins(kongDevJenkins, kongDevUser, kongDevPassword)
    
    def getBuildConsoleOutput(self, job, buildId):
        return self.s.get_build_console_output(job, buildId).encode('utf-8')


def saveFile(fileName, content):
    with open(fileName, 'w') as fd:
        fd.write(content)    
    
def test_KongJenkins():
    j = KongJenkins()
    
    for bsp in sorted(tasks.keys()):
        for module in sorted(tasks[bsp].keys()):
            if module == 'FIREWALL':
                testName, testJob, testBuild, testStatus = tasks[bsp][module][1]
                if testName == 'test':
                    content = j.getBuildConsoleOutput(testJob, testBuild)
                    saveFile('%s.log' % module, content)
                    print(module, testJob, testBuild, testStatus)
                    if testStatus != 'SUCCESS':
                        retestName, retestJob, retestBuild, retestStatus = tasks[bsp][module][3]
                        content = j.getBuildConsoleOutput(testJob, testBuild)
                        saveFile('%s-retest.log' % module, content)
                        print(module, retestJob, retestBuild, retestStatus)                    
                print('\n')
    

def main():
    j = KongJenkins()
    
    for bsp in sorted(tasks.keys()):
        for module in sorted(tasks[bsp].keys()):
            testName, testJob, testBuild, testStatus = tasks[bsp][module][1]
            if testName == 'test':
                content = j.getBuildConsoleOutput(testJob, testBuild)
                print(module, testJob, testBuild, testStatus)
                saveFile('%s.log' % module, content)
                if testStatus != 'SUCCESS':
                    retestName, retestJob, retestBuild, retestStatus = tasks[bsp][module][3]
                    content = j.getBuildConsoleOutput(testJob, testBuild)
                    print(module, retestJob, retestBuild, retestStatus)                    
                    saveFile('%s-retest.log' % module, content)
            print('\n')

   
if __name__ == '__main__':
    main()
    #test_KongJenkins()
    