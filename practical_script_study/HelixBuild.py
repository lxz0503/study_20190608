#!/usr/bin/env python
import sys
import shutil
import time

from KongUtil import runShCmd
from HelixCommon import *

def test():
    print('\n' + '='*20)
    print(getImagePath())
    print(getImageServer())
    print(getImageModulePath('FTP', 'itl_generic'))
    
    print('\n' + '='*20)
    gitPath = getGitPath('SPIN:/buildarea1/svc-cmnet/HELIXSPIN/vx20190815060702_vx7-helix')
    print(gitPath)
    scriptPath = getScriptPath('/buildarea1/svc-cmnet/HELIXSPIN/vx20190815060702_vx7-helix')
    print(scriptPath)
    
    print('\n' + '='*20)
    tarFile = 'FTP.tar'
    modulePath = '/buildarea1/lchen3/vxworks/helix/guests/vxworks-7/pkgs_v2/net/ipnet/coreip/src/ipcom/KongUtil/scripts/FTP'
    tar = createHelixTarFile(tarFile, modulePath)
    print(tar)


def main():
    # HelixBuild.py $BRANCH $NEWCOMMIT $MODULE $BSP
    # check arguments
    if len(sys.argv) != 5:
        print('\nusage:%s $BRANCH $NEWCOMMIT $MODULE $BSP')
        sys.exit(1)
    
    branch, newCommit, module, bsp = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    # set up env
    gitPath = getGitPath(branch)
    scriptPath = getScriptPath(gitPath)
    # build - runKong.sh -g gitPath -m module -b bsp --helix
    buildCmd = '%s/runKong.sh -g %s -m %s -b %s --helix buildOnly' % (scriptPath, gitPath, module, bsp)
    print('=== build cmd:%s' % buildCmd)
    retCode, ret = runShCmd(buildCmd)
    print(ret)
    print(retCode)
    if retCode != 0:
        sys.exit(1)
    # move
    srcPath = '%s/%s' % (os.getcwd(), module)
    dstPath = getImageModulePath(module, bsp)
    #shKongUtil.rmtree(dstPath)
    shutil.copytree(srcPath, dstPath, ignore=shutil.ignore_patterns('*.o', '*.d'))
    # tar
    tarFile = '%s.tar' % module
    modulePath = dstPath
    tar = createHelixTarFile(tarFile, modulePath)
    # move to Helix image path
    #os.remove(os.path.join(os.path.dirname(dstPath), tarFile))
    shutil.move(tar, os.path.dirname(dstPath))
    
if __name__ == '__main__':
    main()
