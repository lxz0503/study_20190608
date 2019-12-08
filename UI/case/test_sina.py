#!/usr/bin/env python
# encoding=UTF-8

import unittest
from page.sina import *
from page.init import *
import time

class SinaTest(Init, Sina):
    def test_sina_login_001(self, parent='divText', value='emailNull'):
        '''
        log in with empty account and password
        :param parent: tag name
        :param value: child tag name
        '''
        self.login('', '')
        self.assertEqual(self.getLoginError, self.getXmlUser(parent, value))

    def test_sina_login_002(self, parent='divText', value='emailFormat'):
        '''
        log in with invalid mailbox name
        :param parent: tag name
        :param value: child tag name
        '''
        self.login('wuya123', 'asd888')
        self.assertEqual(self.getLoginError, self.getXmlUser(parent, value))


if __name__ == '__main__':
    unittest.main(verbosity=2)



