#import pdb

from pytestAuto.utils.iprohc_common import *

def check_config(list, val):
    indx = list.index(val)    
    return indx 

############################################################
class static_config_test:
    'Static configuration test'
    def config(self):
        self.hosts = 3
        self.eta = 30
        self.v6 = False
        #Disable test cases
        self.works_on_vxworks  = False
        self.works_on_unix = False
        self.works_on_iplite = False
        self.works_on_lkm = False

    def test(self, log, hosts, v6, _):
        log('Test rohc static configuraiton', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()

        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

#Get default rohc sysvars 
        f_max_period = dut1.get_sysvar('iprohc.f_max_period')
        f_max_time = dut1.get_sysvar('iprohc.f_max_time') 
        feedback_for =dut1.get_sysvar('iprohc.feedback_for')
        feedback_for_defined = dut1.get_sysvar('iprohc.feedback_for_defined')
        interface_list = dut1.get_sysvar('iprohc.interface_list')
        interface_profile_list = dut1.get_sysvar('iprohc.interface_profile_list')
        large_cid = dut1.get_sysvar('iprohc.large_cid')
        max_cid = dut1.get_sysvar('iprohc.max_cid')

#Verify rohc configuration 
        peer1.rohc_shell_start()
        peer1.rohc_open()
        l = peer1.rohc_show()
        check_config(l, 'Monitoring interfaces: None')
        check_config(l, 'Maximum CID:           ' + max_cid)
        check_config(l, 'CID representation:    Small CID')
        check_config(l, 'Feedback_for:          Not defined')
        check_config(l, 'F_MAX_PERIOD:          ' + f_max_period)
        check_config(l, 'F_MAX_TIME:            ' + f_max_time)
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()

#Invalid f_max_period   
        dut1.set_sysvar('iprohc.f_max_period', '0')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        peer1.rohc_shell_exit()
        check_config(l, 'Failed to open ROHC, ret -1')
        dut1.set_sysvar('iprohc.f_max_period', f_max_period)  
     
#Invalid f_max_time 
        dut1.set_sysvar('iprohc.f_max_time', '0')
        peer1.rohc_shell_start() 
        l = peer1.rohc_open()
        peer1.rohc_shell_exit()
        check_config(l, 'Failed to open ROHC, ret -1')
        dut1.set_sysvar('iprohc.f_max_time',f_max_time)

#Test CID configuration 
        dut1.set_sysvar('iprohc.large_cid', '0')
        dut1.set_sysvar('iprohc.max_cid', '16')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        peer1.rohc_shell_exit()
        check_config(l, 'Failed to open ROHC, ret -1') 
        dut1.set_sysvar('iprohc.max_cid', max_cid)
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'ROHC is opened')
        peer1.rohc_close()
        peer1.rohc_shell_exit()

        dut1.set_sysvar('iprohc.large_cid', '1')
        dut1.set_sysvar('iprohc.max_cid', '16384')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        peer1.rohc_shell_exit()
        check_config(l, 'Failed to open ROHC, ret -1')
        dut1.set_sysvar('iprohc.max_cid', '16383')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'ROHC is opened')
        peer1.rohc_close()
        peer1.rohc_shell_exit()

        dut1.set_sysvar('iprohc.large_cid', '2')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        peer1.rohc_shell_exit()
        check_config(l, 'Failed to open ROHC, ret -1')
        dut1.set_sysvar('iprohc.large_cid', '1')
 
#Test feedback configuration
        dut1.set_sysvar('iprohc.feedback_for_defined', '0')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'ROHC is opened')
        peer1.rohc_close()
        peer1.rohc_shell_exit()

        dut1.set_sysvar('iprohc.feedback_for_defined', '1')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'ROHC is opened')
        peer1.rohc_close()
        peer1.rohc_shell_exit()

        dut1.set_sysvar('iprohc.feedback_for_defined', '2')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'Failed to open ROHC, ret -1')
        dut1.set_sysvar('iprohc.feedback_for_defined', '0')
 
#Test interface configuration 
        dut1.set_sysvar('iprohc.interface_list', 'eth,1, eth,2')
        l = peer1.rohc_open()
        check_config(l, 'ROHC is opened')
        peer1.rohc_close()
        peer1.rohc_shell_exit()

        dut1.set_sysvar('iprohc.interface_list', 'eth,1, eth,')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'Failed to open ROHC, ret -1')

        dut1.set_sysvar('iprohc.interface_list', '1, eth')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'ROHC is opened')
        peer1.rohc_close()
        peer1.rohc_shell_exit()

        dut1.set_sysvar('iprohc.interface_list', '')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'Failed to open ROHC, ret -1')
        peer1.rohc_close()
        peer1.rohc_shell_exit()

#Test profile configuration 
        dut1.set_sysvar('iprohc.interface_list', 'eth,1')
        dut1.set_sysvar('iprohc.interface_profile_list', 'eth1,0,2,3,4')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'ROHC is opened')
        l = peer1.rohc_show()

        check_config(l, 'uncompressed profile')
        check_config(l, 'UDP/IP profile')
        check_config(l, 'ESP/IP profile')
        check_config(l, 'IP profile')
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()

        dut1.set_sysvar('iprohc.interface_list', 'eth,1')
        dut1.set_sysvar('iprohc.interface_profile_list', 'eth1,1')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'Failed to open ROHC, ret -1')
        peer1.rohc_shell_exit()

        dut1.set_sysvar('iprohc.interface_list', 'eth,1')
        dut1.set_sysvar('iprohc.interface_profile_list', 'eth1,7')
        peer1.rohc_shell_start()
        l = peer1.rohc_open()
        check_config(l, 'Failed to open ROHC, ret -1')
        peer1.rohc_close()
        peer1.rohc_shell_exit()

#Test a valid rohc configuration 
        dut1.set_sysvar('iprohc.f_max_period', '64000')
        dut1.set_sysvar('iprohc.f_max_time', '200')
        dut1.set_sysvar('iprohc.feedback_for', '10')
        dut1.set_sysvar('iprohc.feedback_for_defined', '1')
        dut1.set_sysvar('iprohc.interface_list', 'eth,2')
        dut1.set_sysvar('iprohc.interface_profile_list', 'eth2,4')
        dut1.set_sysvar('iprohc.large_cid', 1)
        dut1.set_sysvar('iprohc.max_cid', '200')
        peer1.rohc_shell_start()
        peer1.rohc_open()
        l = peer1.rohc_show() 
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit() 
        check_config(l, 'F_MAX_PERIOD:          64000')
        check_config(l, 'F_MAX_TIME:            200')
        check_config(l, 'Feedback_for:          10')
        check_config(l, 'eth,2   Supported profiles:')
        check_config(l, 'IP profile')
        check_config(l, 'Maximum CID:           200')
        check_config(l, 'CID representation:    large CID')
        
############################################################
class dynamic_config_test:
    'Test dynamic configuraiton'
    def config(self):
        self.hosts = 3
        self.eta = 30
        self.v6 = False
#Run only for unix port
        self.works_on_unix = True
        self.works_on_vxworks  = False
        self.works_on_iplite = False
        self.works_on_lkm = False
    def test(self, log, hosts, v6, _):
        log('Test rohc dynamic configuraiton', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()

        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

#Test IF configuraiton 
        peer1.rohc_shell_start()
        peer1.rohc_open()

        l = peer1.rohc_add_if('eth','0')  
        check_config(l, 'Added a ROHC monitoring interface') 

#Add an interface with invalid ifnum. ROHC does not check kernel IFs 
        l = peer1.rohc_add_if('eth','20')
        check_config(l, 'Added a ROHC monitoring interface')

#Add an interface with invalid ifname. ROHC does check kernel IFs 
        l = peer1.rohc_add_if('fakeif','0')
        check_config(l, 'Added a ROHC monitoring interface')

#Make sure IFs are added to ROHC
        l = peer1.rohc_show()
        check_config(l, 'eth,0   Supported profile: None')
        check_config(l, 'eth,20   Supported profile: None')
        check_config(l, 'fakeif,0   Supported profile: None')

#Delete interfaces  
        l = peer1.rohc_del_if('fakeif','0')
        check_config(l, 'Removed a ROHC monitoring interface')

        l = peer1.rohc_del_if('eth','20')
        check_config(l, 'Removed a ROHC monitoring interface')

#Make sure IFs are deleted from ROHC 
        l = peer1.rohc_show()
        l.index('eth,0   Supported profile: None')

        if 'eth,20   Supported profile: None' in l:
           raise Exception("Incorrect interface configuration") 

        if 'fakeif,0   Supported profile: None' in l: 
           raise Exception("Incorrect interface configuration")

        check_config(l, 'eth,0   Supported profile: None')

        l = peer1.rohc_del_if('eth','0')
        l = peer1.rohc_show()
        if 'eth,0   Supported profile: None' in l:
           raise Exception("Incorrect interface configuration")

#Add the same interface twice 
#        l = peer1.rohc_add_if('eth','0')
#        check_config(l, 'Added a ROHC monitoring interface')

#        l = peer1.rohc_add_if('eth','0')
#        check_config(l, 'Added a ROHC monitoring interface')

#        l = peer1.rohc_del_if('eth','0')
#        check_config(l, 'Removed a ROHC monitoring interface')

#Delete non existing interface 
#        l = peer1.rohc_del_if('eth','0')
#        check_config(l, 'Removed a ROHC monitoring interface')

# Test profiles 
        l = peer1.rohc_add_if('eth','0')
        check_config(l, 'Added a ROHC monitoring interface')

        l = peer1.rohc_add_if('eth','1')
        check_config(l, 'Added a ROHC monitoring interface')

        l = peer1.rohc_add_if('eth','2')
        check_config(l, 'Added a ROHC monitoring interface')

#       /* ESP */
        peer1.rohc_add_profile('eth', '1', 'eth1', 3, 0)
        l =  peer1.rohc_show()
        indx = l.index('eth,1   Supported profiles:')
        res =  l[indx] + l[indx + 1]        
        check_config(res, 'eth,1   Supported profiles:ESP/IP profile')       

#       /* Udp */
        peer1.rohc_add_profile('eth', '1', 'eth1', 2, 0)
        l =  peer1.rohc_show()
        indx = l.index('eth,1   Supported profiles:')
        res =  l[indx] + l[indx + 1] + ', ' + l[indx + 2]
        check_config(res, 'eth,1   Supported profiles:UDP/IP profile, ESP/IP profile')
        check_config(l, 'eth,2   Supported profile: None')
 
        peer1.rohc_del_profile('eth', '1', 'eth1', 2, 0)       
        peer1.rohc_add_profile('eth','2', 'eth2', 2, 0)

        l =  peer1.rohc_show()
        indx = l.index('eth,1   Supported profiles:')
        res =  l[indx] + l[indx + 1]
        check_config(res, 'eth,1   Supported profiles:ESP/IP profile')
                
        indx = l.index('eth,2   Supported profiles:')
        res =  l[indx] + l[indx + 1]
        check_config(res, 'eth,2   Supported profiles:UDP/IP profile')       

        peer1.rohc_del_profile('eth', '1', 'eth1', 3, 0)
        peer1.rohc_del_profile('eth','2', 'eth2', 2, 0)
        l =  peer1.rohc_show()               
        check_config(l, 'eth,1   Supported profile: None')
        check_config(l, 'eth,2   Supported profile: None')        

#Add/delete the same profile twice 
#        l = peer1.rohc_add_profile('eth','1', 'eth1', 2, 0)
#        l = peer1.rohc_add_profile('eth','1', 'eth1', 2, 0)
#        l = peer1.rohc_del_profile('eth','1', 'eth1', 2, 0)
#        l = peer1.rohc_del_profile('eth','1', 'eth1', 2, 0) 

#Clean up
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_open()
          
#Configure all profiles
        l = peer1.rohc_add_if('eth','1')
        check_config(l, 'Added a ROHC monitoring interface')
        l = peer1.rohc_add_profile('eth', '1', 'eth1', 0, 0)
        check_config(l, 'Added a ROHC profile to the interface') 
        line = peer1.rohc_add_profile('eth', '1', 'eth1', 2, 0)
        check_config(l, 'Added a ROHC profile to the interface')
        line = peer1.rohc_add_profile('eth', '1', 'eth1', 3, 0)
        check_config(l, 'Added a ROHC profile to the interface')
        line = peer1.rohc_add_profile('eth', '1', 'eth1', 4, 0)
        check_config(l, 'Added a ROHC profile to the interface')
         
#Invalid and not supported profiles 
        l = peer1.rohc_add_profile('eth', '1', 'eth1', 8, 0) 
        check_config(l, 'profile id must be a valid ID (0-6).') 
        l = peer1.rohc_add_profile('eth', '1', 'eth1', 1, 0)
        check_config(l, 'Failed to add a ROHC profile 1 to the interface eth1')
        l = peer1.rohc_add_profile('eth', '1', 'eth1', 5, 0)
        check_config(l, 'Failed to add a ROHC profile 5 to the interface eth1')

        l =  peer1.rohc_show()
        indx = l.index('eth,1   Supported profiles:')
        if_prof = [l[indx], l[indx + 1], l[indx + 2], l[indx + 3], l[indx + 4]]  
        check_config(if_prof, 'uncompressed profile')
        check_config(if_prof, 'UDP/IP profile')
        check_config(if_prof, 'ESP/IP profile')
        check_config(if_prof, 'IP profile')

# Clean up the ROHC  
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()

############################################################
class cid_allocation:
    'Test CID allocation'
    def config(self):
        self.hosts = 3
        self.eta = 30

    def test(self, log, hosts, v6, _):
        log('Rohc allocation test', echo=True)
        host1 = hosts[0]
        host2 = hosts[1]
        dut1  = hosts[0].ipcom_shell()
        dut2  = hosts[1].ipcom_shell()

        peer1 = rohc_base(host1)
        peer2 = rohc_base(host2)

# Small CID 
        dut1.set_sysvar('iprohc.large_cid', '0')
        dut2.set_sysvar('iprohc.large_cid', '0')

        dut1.set_sysvar('iprohc.max_cid', '6')
        dut2.set_sysvar('iprohc.max_cid', '6')

# Configure PPPoE
        addr1, addr2, if_name1, if_name2 = config_pppoe(hosts, peer1, peer2, v6 = v6)

# Prepare PPPoE addresses for use 
        addr1_s, addr1_c, addr2_s, addr2_c = pppoe_addr(addr1, addr2, if_name1, if_name2, v6)

# Configure ROHC 
        peer1.rohc_configure(if_name1[:5], if_name1[5:], if_name1, '2', '3')
        peer1.rohc_shell_exit()
        peer2.rohc_configure(if_name2[:5], if_name2[5:], if_name2, '2', '3')
        peer2.rohc_shell_exit()

        dut2.echoserver(addr2_s, proto='udp')

# Begin testing  
# Take cids from 3 to 6

        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7301, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100, chunk_size = 100, local_port = 7302, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100,  chunk_size = 100, local_port = 7303, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100,  chunk_size = 100, local_port = 7304, verify_data=True)

        ls = peer1.rohc_show()

        lookup_in_lines(ls, "cid:   3", 0, True)
        lookup_in_lines(ls, "cid:   4", 0, True)
        lookup_in_lines(ls, "cid:   5", 0, True)
        lookup_in_lines(ls, "cid:   6", 0, True)
        lookup_in_lines(ls, "cid:   1", 0, False)
        lookup_in_lines(ls, "cid:   2", 0, False)

# Take 1, 2 cids 
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100,  chunk_size = 100, local_port = 7306, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 100,  chunk_size = 100, local_port = 7307, verify_data=True)

        ls = peer1.rohc_show()

        lookup_in_lines(ls, "cid:   1", 0, True)
        lookup_in_lines(ls, "cid:   2", 0, True)

# All slots are full. This should fail and context should not be created.  
        dut1.echoclient(addr2_c, proto='udp', nbuf = 1,  chunk_size = 100, local_port = 7308, verify_data=True)
        dut1.echoclient(addr2_c, proto='udp', nbuf = 1,  chunk_size = 100, local_port = 7309, verify_data=True)

        ls = peer1.rohc_show()

        lookup_in_lines(ls, "cid:   7", 0, False)
        lookup_in_lines(ls, "cid:   8", 0, False)

# Search for failed decompression 
        peer1.lookup_for_failed_decompression()
        peer2.lookup_for_failed_decompression()

        dut2.stop_echoserver()

# Clean up the ROHC  
        peer1.rohc_shell_start()
        peer1.rohc_close()
        peer1.rohc_shell_exit()
        peer2.rohc_shell_start()
        peer2.rohc_close()
        peer2.rohc_shell_exit()

