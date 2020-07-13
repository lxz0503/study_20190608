import os
import config


class default_test(object):
    def __init__(self):
        self.v4 = True
        self.v6 = True
        self.v4andv6 = False
        self.hosts = 1
        self.doc = ''
        self.eta = 1
        self.eta6 = -1
        self.flags = ()
        self.net_layout = 'default'
        self.will_fail = False
        self.might_fail = False
        self.retries    = 0
        #stacks / shell commands
        self.works_on_ipnet = True
        self.works_on_lkm = True
        self.works_on_fos = True
        self.works_on_iplite = False
        #OS ports
        self.works_on_unix = True
        self.works_on_ose5 = True
        self.works_on_vxworks = True
        self.works_on_gpp = True
        self.required_product_versions = { }
        self.require_types = ()


    def config(self):
        pass


    def required_product_version(self, product, version):
        self.required_product_versions[product] = version


    def pause(self):
        'press enter to continue. good for telnetting to target and check things out then continue. do NOT commit to cvs. use it in your test app during development.'
        import time
        print ('paused, press enter to continue')
        input()


    def breakpoint(self):
        'you will be dropped into the python debugger, press "n" to go to the code line after the "breakpoint()" statement'
        import pdb
        pdb.set_trace()

def gather_tests(what_to_test, listing = False):
    #check for bad names
    # adds e.g. '../../ipnet-2.6.7/test' to the pythonpath
    product = what_to_test.split('.')[0]
    if product not in config.productpath:
        print('No product named "%s" (from %s), skipping...' % (product, what_to_test))
        return []
    productpath = os.path.join(config.productroot, config.productpath[ product ], 'test')
    if not os.access(productpath, os.F_OK):
        #print 'No dir named "%s" (from %s), skipping...' % (productpath, what_to_test)
        return []
    if productpath not in sys.path:
        sys.path.append(productpath)
    if '.' in what_to_test:
        modules_to_import = [what_to_test.split('.')[1]]
    else:
        modules_to_import = [x[:-3] for x in os.listdir(productpath) if x.endswith('.py') and not x.startswith('.')]
    modules = []
    for m in modules_to_import[:]:
        # inject things from here in each test so they need not import iptestengine
        #'all' must be something not ''
        try:
            moo = __import__(m, globals(), locals(), ['all'])
        except Exception as e:      # xiaozhan
            print(e)
        # except ImportError, msg:
        #     modules_to_import.remove(m)
        #     print (msg)
        #     print ('importing', m, 'sys.path is ', sys.path)
        #     continue
        # except SyntaxError, msg:
        #     modules_to_import.remove(m)
        #     print (msg)
        #     continue

        # moo.test_fail = test_fail
        # moo.engine_error = engine_error
        # moo.pause = pause
        # moo.breakpoint = breakpoint
        # moo.ip = ip
        # moo.custom_cmd = custom_command
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
            print ('No testclass named "%s"' % what_to_test.split('.')[2])
            return []
    else:
        #specified product (and possibly file). get all testclasses in file.
        for x in range(len(modules)):
            modname = modules_to_import[x]
            for t in all_tests_in(modules[x]):
                testclasses.append((modname, t))
    tests = []
    for t in testclasses:
        class mixin(t[1], default_test):
            pass
        inst = mixin()
        inst.doc = t[1].__doc__
        inst.config()
        inst.prodname = product
        inst.modname  = t[0]
        inst.testname = t[1].__name__
        tests.append(inst)
    return tests

if __name__ == '__main__':

    import optparse,sys
    p = optparse.OptionParser()
    p.add_option('-b', '--break-on-error', dest = 'break_on_fail', action="store_true", default = False, help = '''Exit the test script as soon as there is an error. Otherwise, remaining tests will be run anyways but a report in the end will show the number of failures''')
    p.add_option('-v', '--verbose', action="store_true", default = False, help = 'Everything that would have been written to the log is printed to screen')
    #p.add_option('-q', '--quiet',  help = 'Be more quiet')
    quiet = True
    p.add_option('-l', '--list', dest = 'list_prods', action="store_true", default = False, help = 'List available tests. Combine with -v to see descriptions. Add -t prodname[.modulename[.testname]] to list specific products and their tests.')
    p.add_option('-L', '--loop', dest = 'loop_forever', action="store_true", default = False, help = 'Loop all selected tests forever until you press ctrl-c or until one fails if you specified -b/--break-on-error.')
    p.add_option('-4', '--only-ipv4', dest = 'test_v6', action="store_false", default = True, help = 'Only run IPv4 versions of tests.')
    p.add_option('-6', '--only-ipv6', dest = 'test_v4', action="store_false", default = True, help = 'Only run IPv6 versions of tests.')
    p.add_option('-f', '--fast', action="store_true", default = False, help = 'Tests with support for this flag will not be run as thoroughly. This also skips process accounting.')
    p.add_option('-d', '--dry-run', action="store_true", default = False, help = "Don't actually do anything, just log what would've been done to screen. This is only useful sometimes when debugging the test engine. The output looks similar to the old tcl expect engine.")
    p.add_option('-t', '--test', dest = 'what_to_test', default = None, help = 'Run the tests found in product TEST. TEST is chosen as either by its fully qualified name or a set of tests. E.g: ipnet or ipnet.tcp or ipnet.tcp.accept. TEST can also be a comma-separated list without whitespace, e.g.: ipnet.icmp.echo,ipnet.arp (mixing single and sets of tests is ok).')

    args = sys.argv[1:]
    print(args)
    # ['-t', 'ipipsec.ipipsec.esp_transport_aesctr_none']
    # No such test: ipipsec.ipipsec.esp_transport_aesctr_none     esp_transport_aesctr_none is the case name
    # tests are []
    (o, _) = p.parse_args(args)

    tests = []                                  # xiaozhan    this is the origin of tests

    # fail on badly specified tests
    for what in o.what_to_test.split(','):      # xiaozhan   '-t', '--test', dest = 'what_to_test'
        print(what)    # ipipsec.ipipsec.esp_transport_aesctr_none
        tests_ = gather_tests(what)             # xiaozhan,
        if not tests_:
            print("No such test: " + what)
        tests += tests_

    print('tests are', tests)