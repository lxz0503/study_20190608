import sys
sys.path.insert(0, '/home/xli3/kong')
from vxBuild import buildVxworks, copyVxImage
from util import readYaml, printYamlFile

def buildVxImage(spin=False):   # xiaozhan, add spin=False to support build on branch
    if spin is True:
        installPath = '/home/xli3/SPIN/vx20240116114147_vx_2403'      # xiaozhan, this is only for SPIN
    else:
        installPath = '/home/xli3/vxworks'      # xiaozhan debug, this is for branch
    cfg = readYaml('vxBuildConfig.yaml')
    printYamlFile('vxBuildConfig.yaml')
    bsp = 'itl_generic'
    tool = 'llvm'
    smp = True
    m64bit = True
    debug = False
    cpu = 'SKYLAKE'
    ipv6 = True
    buildVxworks(cfg['IPNET-BASIC'], installPath, bsp, tool, smp, m64bit, cpu, ipv6, spin) # xiaozhan, debug
    copyVxImage('./%s_vip/default' % bsp, '/folk/xli3/tsn_trial/IA_Image/vxWorks-qemu')

def main():
    buildVxImage()
    
if __name__ == '__main__':
    main()