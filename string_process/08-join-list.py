components = ' -add '.join(['_WRS_CONFIG_COMPONENT_IPDHCPS=y',
                            '_WRS_CONFIG_COMPONENT_IPIKE=y',
                            '_WRS_CONFIG_COMPONENT_IPIPSEC=y',
                            '_WRS_CONFIG_COMPONENT_IPMCP=y',
                            '_WRS_CONFIG_COMPONENT_IPRIP=y',
                            '_WRS_CONFIG_COMPONENT_IPFIREWALL=y',
                            '_WRS_CONFIG_COMPONENT_FEATURE_IPNET_INET6=y'])
components = 'vxprj vsb -add ' + components
print(components)
if 'IPIKE' in components:
    print('we have IPIKE')

components_list = ['-add _WRS_CONFIG_COMPONENT_IPDHCPS=y',
                   '-add _WRS_CONFIG_COMPONENT_IPIKE=y',
                   '-add _WRS_CONFIG_COMPONENT_IPIPSEC=y',
                   '-add _WRS_CONFIG_COMPONENT_IPMCP=y',
                   '-add _WRS_CONFIG_COMPONENT_IPRIP=y',
                   '-add _WRS_CONFIG_COMPONENT_IPFIREWALL=y',
                   '-remove _WRS_CONFIG_COMPONENT_NTP=y',
                   '-add _WRS_CONFIG_COMPONENT_FEATURE_IPNET_INET6=y',
                   ]
components_str = 'vxprj vsb ' + ' '.join(components_list)
print(components_str)
if 'IPIKE' in components_str:
    print('we have IPIKE')

# test configuration file should be separated from test script
components_list = []
with open('test_config', 'r') as f:
    for line in f:
        components_list.append(line.strip('\n'))
print(components_list)
components_str = 'vxprj vsb ' + ' '.join(components_list)
print(components_str)
if 'IPIKE' in components_str:
    print('we have IPIKE')

