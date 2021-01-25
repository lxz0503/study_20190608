./runKong.sh buildTest -g /net/pek-vx-nwk1//buildarea1/svc-cmnet/SPIN/vx20190710183403_vx7-SR0620-native -m FIREWALL -c ipfirewall.ipfilter.return_icmp 2>&1 | tee FIREWALL.log
./runKong.sh buildTest -g /net/pek-vx-nwk1//buildarea1/svc-cmnet/SPIN/vx20190710183403_vx7-SR0620-native -m SSL -c ipssl.apps.ssl_srv_clt 2>&1 | tee SSL.log
