#!/usr/bin/env python

import os, sys, re
from logging import *

from Action import Action

class VxAction(Action):
    def __init__(self, continueFailedCmd = False):
        debug('entering class VxAction::__init__')
        super(VxAction, self).__init__(continueFailedCmd)
        self.windBaseDir = ''


    def BeforeRun(self):
        debug('entering class VxAction::Before')

        self.windBaseDir = os.getenv("WIND_BASE")
        debug('WIND_BASE=%s' % self.windBaseDir)
        if self.windBaseDir is None:
            error('environment WIND_BASE not found')
            exit(1)
        else:
            if not re.search('vxworks-7', self.windBaseDir):
                error('environment WIND_BASE is not correct')
                exit(1)
        return self.windBaseDir
  