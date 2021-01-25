#!/usr/bin/env python

import argparse
import os, sys, re


def HandleWalkError(osError):
    """Handle os.walk() error"""
    print(osError.errno, osError.filename)


def QueryBSP(boardDir, keywords):
    for parentDir, subDirs, files in os.walk(boardDir, topdown=True, onerror=HandleWalkError, followlinks=True):
        if 'target.ref' in files:
        #    if parentDir.endswith('ppc/fsl_p3p4p5'):
        #    if parentDir.endswith('arm/bsp6x_ti_am335x_evm'): 
            HandleBSP(parentDir, keywords)


def HandleBSP(parentDir, keywords):
    targetRef = parentDir + '/target.ref'
    if not os.path.exists(targetRef):
        print 'cannot find target.ref at %s' % parentDir
        return    

    arch = GetArchName(parentDir)
    bsp = GetBSPName(parentDir)
    dtsFiles = GetBSPDts(parentDir)
    #print '** %s' % parentDir
    bspComponents = GetBSPComponents(targetRef, keywords)
    
    Output(arch, bsp, bspComponents, dtsFiles)
    

def GetBSPDts(parentDir):
    dtsDir = parentDir + '/_dts'
    if not os.path.exists(dtsDir):
        #print 'cannot find _dts directory at %s' % parentDir
        return []
    return os.listdir(dtsDir)


def GetBSPComponents(targetRefFile, keywords):
    with open(targetRefFile, 'r') as fd:
        fc = fd.read()
    boards = re.findall("(?s)\\\\sh list of hardware features \((.*?)\)", fc, re.I) # \\\\sh means \sh; ignore case; 
    comps = re.findall("(?s)\\\\sh list of hardware features.*?\\\\ts(.*?)\\\\te", fc, re.I)
    #print boards
    #print comps
    if len(boards) != len(comps):
        print 'board number is not equal'
        return {}
    newComps = map(lambda x: FilterComp(x, keywords), comps)
    return dict(zip(boards, newComps))


def FilterComp(comp, keywords):
    lines = comp.split('\n')
    return '\n'.join([ line for line in lines if line.split(' ')[0] in keywords ])
    

def GetBSPName(parentDir):   
    return os.path.basename(parentDir)


def GetArchName(parentDir):
    return os.path.basename(os.path.dirname(parentDir))


def Output(arch, bsp, bspComponents, dtsFiles):
    print '== %s/%s: ==' % (arch, bsp)
    for board in sorted(bspComponents.keys()):
        print '\t%s' % board
        print '%s' % '\n'.join( '\t\t%s' % x for x in bspComponents[board].split('\n') )
    print '\tdts:%s' % dtsFiles
    print
     

def main():
    parser = argparse.ArgumentParser('Query BSP Parameters')
    parser.add_argument('--boarddir', action='store', dest='boardDir', help='specify board path in vx7')
    parser.add_argument('--keyword', action='store', dest='keywords', help='specify keywords to search, e.g. "SD USB"')
    r = parser.parse_args()
    
    if (r.boardDir is None) or (r.keywords is None):
        parser.print_help()
        sys.exit(1)

    if not r.boardDir.endswith('os/board'):
        print 'incorrect board path'
        sys.exit(2)
    
    keywords = r.keywords.split(' ')
    QueryBSP(r.boardDir, keywords)
    

def test():
    pDir = '/buildarea2/lchen3/workspace/vx7-dev-nightly/vxworks/vxworks-7/pkgs/os/board/ppc/fsl_p3p4p5'
    print GetBSPName(pDir)
    print GetArchName(pDir)
    print GetBSPDts(pDir)
    
    
if __name__ == '__main__' : 
    main()
    #test()
    
