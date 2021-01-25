#!/usr/bin/env python

# gather_tests() comes from pkgs/net/ipnet/NOT_IMPORTED/iptestengine/src/iptestengine.py

import sys
import os

import config

def GetProductTestname(productroot, product):
    if not product in config.productpath.keys():
        raise 'cannot find the path for product:', product
    tests = gather_tests(productroot, product, listing=True)
    return create_testname(tests)


def create_testname(tests):
    return ['.'.join([x[2],x[1],x[0]]) for x in tests]


def gather_tests(productroot, what_to_test, listing = False):
    # productroot is the full path to pkgs/net/ipnet
    product = what_to_test.split('.')[0]
    if product not in config.productpath:
        print 'No product named "%s" (from %s), skipping...' % (product, what_to_test)
        return []
    productpath = os.path.join(productroot, config.productpath[ product ], 'test')
    if not os.access(productpath, os.F_OK):
        print 'No dir named "%s" (from %s), skipping...' % (productpath, what_to_test)
        return []

    AddSysPath(productpath)
    AddSysPath(productroot)

    # use local config.py instead of pkgs/net/ipnet/NOT_IMPORTED/iptestengine/config/config.py
    # or ipike will get the error like:
    #  File "/buildarea2/lchen3/workspace/vx7-dev-nightly/vxworks/vxworks-7/pkgs/net/ipnet/ipsecike/ike/test/racoon.py", line 5, in <module>
    #  exec open(os.path.join(config.productroot, config.productpath['ipike'], 'test', 'racoon1.py'))
    #  IOError: [Errno 2] No such file or directory: '../../ike/test/racoon1.py'
    AddSysPath(os.path.realpath(__file__)) 
    
    AddSysPath(productroot + '/NOT_IMPORTED/iptestengine/config')
    AddSysPath(productroot + '/NOT_IMPORTED/iptestengine/src')
    
    AddSysPath(productroot + '/linkproto/ppp/test')
    AddSysPath(productroot + '/linkproto/rohc/test/ip/test')
    
    if '.' in what_to_test:
        modules_to_import = [what_to_test.split('.')[1]]
    else:
        modules_to_import = [x[:-3] for x in os.listdir(productpath) if x.endswith('.py') and not x.startswith('.')]
    modules = []
    for m in modules_to_import[:]:
        # inject things from here in each test so they neednt import iptestengine
        #'all' must be something not ''
        try:
            moo = __import__(m, globals(), locals(), ['all'])
        except ImportError, msg:
            modules_to_import.remove(m)
            print '***', msg
            continue
        except SyntaxError, msg:
            modules_to_import.remove(m)
            print '###', msg
            continue

        moo.test_fail = 'failed'
        moo.engine_error = 'engine_error'
        moo.pause = 'pause'
        moo.breakpoint = 'breakpoint'
        moo.ip = 'ip'
        moo.custom_cmd = 'custom_command'
        modules.append(moo)

    def all_tests_in(mod):
        class someclass:
            pass
        return [mod.__dict__[x] for x in dir(mod) if type(someclass) == type(mod.__dict__[x]) and hasattr(mod.__dict__[x], 'test') and callable(mod.__dict__[x].test)]

    testclasses = []
    if what_to_test.count('.') == 2:
        # specified product, file and testclass. get it.
        for t in all_tests_in(modules[0]):
            if t.__name__ == what_to_test.split('.')[2]:
                testclasses = [(modules_to_import[0], t)]
                break
        if not testclasses:
            print 'No testclass named "%s"' % what_to_test.split('.')[2]
            return []
    else:
        #specified product (and possibly file). get all testclasses in file.
        for x in range(len(modules)):
            modname = modules_to_import[x]
            for t in all_tests_in(modules[x]):
                testclasses.append((modname, t))
    tests = []
    for t in testclasses:
        prod_name = product
        mod_name  = t[0]
        test_name = t[1].__name__
        tests.append((test_name, mod_name, prod_name))

    return tests


def AddSysPath(path):
    if not path in sys.path:
        sys.path.append(path)    
