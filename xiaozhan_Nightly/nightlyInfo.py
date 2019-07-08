#!/usr/bin/env python
from InstallSpin import InstallSpin, InstallLicense, GetSpinInfo
import KongConfig


def nightlyInfo():
    branch = "SPIN"
    nightly_date = GetSpinInfo(branch, 'date')
    #print '=== nightly test date is:%s' % nightly_date
    release_name = GetSpinInfo(branch, 'release')
    #print '=== nightly release name is:%s' % release_name
    spin = GetSpinInfo(branch, 'name')
    print '====nightly spin is %s ' % spin
    return nightly_date,release_name,spin
	
	
def main():
    nightlyInfo()
	

if __name__ == '__main__':
    main()
