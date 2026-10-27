#!/usr/bin/env python
# encoding=UTF-8

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from page.sina import *
from page.init import *


class SinaTest(Init, Sina):
    def test_sina_login_001(self, parent='divText', value='emailNull'):
        '''
        Logs in with empty account and password
        :param parent: tag name
        :param value: child tag name
        '''
        self.login('', '')
        self.assertEqual(self.getLoginError, self.getXmlUser(parent, value))

    def test_sina_login_002(self, parent='divText', value='emailFormat'):
        '''
        Logs in with invalid mailbox name
        :param parent: tag name
        :param value: child tag name
        '''
        self.login('wuya123', 'asd888')
        self.assertEqual(self.getLoginError, self.getXmlUser(parent, value))


if __name__ == '__main__':
    unittest.main(verbosity=2)



