#!/usr/bin/python
""" Script for retrieving information from testcases. It supports
defect and requirement numbers. By default it gets a list containing
all defect end requirement numbers from all testcases.

In the tests the defects and requirements are given by adding two
class varables to the test. Example:

---------
class example_test:
    '''A test'''

    defects = ['WIND00277121']
    requirements = ['WIND00243789']
    
    def config:
        '''Do some configuration'''

    def test:
        '''Start test'''
---------

The script must be run from .../iptestengine/src."""

import sys
import os
import inspect

sys.path.insert(0, '../config')
import config

ROOTPATH = "../../"
TESTFOLDER = "/test"

def get_tests():
    '''Get all tests available'''
    test_list = []

    for product in config.productpath.values():
        # Set up path to tests 
        test_path = ROOTPATH + product + TESTFOLDER 

        # Check if component exists
        if os.path.exists(test_path):
            # Set working directory to test path
            sys.path.append(test_path)

            # Filter out python files
            test_files = filter(lambda x: x[-3:] == ".py", 
                                os.listdir(test_path))

            for module in test_files:
                # Import all python files as modules (remove ".py")
                mod = __import__(module[0:-3])
                # Get all members from module
                for name, obj in inspect.getmembers(mod):
                    # Check if member is a class and has a 'test' method
                    if inspect.isclass(obj) and hasattr(obj, "test"): 
                        test_list.append(obj)
    return test_list


def get_defects(test):
    '''Get a list of all defects related to a test'''
    try:
        return test.defects
    except AttributeError:
        pass


def get_requirements(test):
    '''Get a list of all requirements related to a test'''
    try:
        return test.requirements
    except AttributeError:
        pass


def parse_arguments():
    '''Parse arguments'''
    import optparse

    parser = optparse.OptionParser()

    # Add general options
    parser.add_option('-r', '--requirements-only', action = "store_true", 
                      dest = 'requirements', default = False, 
                      help = '''Get only a list of requirements''')
    parser.add_option('-d', '--defects-only', action = "store_true", 
                      dest = 'defects', default = False, 
                      help = '''Get only a list of defects''')
    parser.add_option('-t', '--tests', action = "store_true", 
                      dest = 'tests', default = False, 
                      help = '''Get only a list of tests available''')

    (options_instance, args) = parser.parse_args()
    return vars(options_instance)



def main():
    '''Main function'''
    program_options = parse_arguments()

    # Get list of tests
    test_list = get_tests()

    if program_options['tests']:
        for test in test_list:
            print test
        return 

    defect_list = []
    requirement_list = []

    for test in test_list:
        defects = get_defects(test)
        if defects != None:
            for defect in defects:
                defect_list.append(defect)

        requirements = get_requirements(test)
        if requirements != None:
            for requirement in requirements:
                requirement_list.append(requirement)

    if program_options['requirements']:
        print requirement_list
    elif program_options['defects']:
        print defect_list
    else:
        print defect_list + requirement_list


if __name__ == '__main__':
    main()

