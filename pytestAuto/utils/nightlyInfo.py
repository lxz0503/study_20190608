#!/usr/bin/env python
import sys, os

sys.path.insert(0, '/home/xli3/pytestAuto/utils')
from InstallSpin import GetSpinInfo
from spin import get_spin_type


def nightlyInfo():
    branch = get_spin_type()
    nightly_date = GetSpinInfo(branch, 'date')
    release_name = GetSpinInfo(branch, 'release')
    spin = GetSpinInfo(branch, 'name')
    return nightly_date, release_name, spin, branch


def main():
    nightlyInfo()


if __name__ == '__main__':
    main()
