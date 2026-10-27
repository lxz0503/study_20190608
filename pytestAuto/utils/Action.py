#!/usr/bin/env python

import os, subprocess
from sys import exit
from abc import ABCMeta, abstractmethod
from logging import *


def ExecCmd(cmd, shell=False, outputHandler=None):
    """ Run a command and invoke call-back function outputHandler if existed
            outputHandler should have the following format:
                HandleOutput(cmd, retCode, output)
        input: a shell comand or a list of shell commands separated by ';' 
        output: (return_code, output)
    """
    cmdList = cmd
    shellValue = True
    try:
        output = subprocess.check_output(cmdList, shell=shellValue, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        if outputHandler is not None:
            outputHandler(cmdList, err.returncode, err.output)
        return (err.returncode, err.output)
    else:
        if outputHandler is not None:
            outputHandler(cmdList, 0, output)
        return (0, output)


def ExecCmdList(cmdList, shell=False, stepByStep=False, outputEachStep=False, 
                outputHandler=None, continueFailedCmd=False):
    """ run a list of commands in one shell
          if steByStep is False, run the commands in one shell
          if steByStep is True, run the command one by one and exit when any one gets failure
          outputHandler is the call-back function for each command
    """
    if not stepByStep:
        cmdStr = ''
        for eachCmd in cmdList:
            cmdStr += eachCmd + ';'
        debug('executing command:%s' % cmdStr) 
        retCode, retContent = ExecCmd(cmdStr, shell)
        return (retCode, retContent, cmdStr[:-1])
    else:
        for eachCmd in cmdList:
            debug('executing command:%s' % eachCmd)
            retCode, retContent = ExecCmd(eachCmd, shell)
            if outputEachStep:
                print(retContent)
            if outputHandler is not None:
                outputHandler(eachCmd, retCode, retContent)
            if retCode != 0:
                if continueFailedCmd:
                    continue
                else:
                    return (retCode, retContent, eachCmd)
        cmdStr = ''
        for cmd in cmdList: cmdStr += cmd + ';'
        return (0, retContent, cmdStr[:-1])
        
    
class Action(object):
    """virtual class Action"""
    __metaclass__ = ABCMeta
    
    # private method
    def __init__(self, continueFailedCmd=False):
        debug('entering class Action::__init__')
        super(Action,self).__init__()
        self.__cmds = []
        self.continueFailedCmd = continueFailedCmd
        self.retCode = 0
        
    def Run(self):
        """ return 0 (succeed) or else (failed) """
        self.BeforeRun()
        debug('entering class Action::Run')
        if self.GetCmd() != []:
            debug('doing class Action::Run commands=%s' % self.GetCmd())
            # execute the commands one by one
            # if you need to run N commands together, use 'cmd1; cmd2' instead
            self.retCode, retContent, cmd = ExecCmdList(self.GetCmd(), stepByStep=True, 
                                                   outputHandler=self.HandleOutput, continueFailedCmd=self.continueFailedCmd)
            # only analyze the last command execution result
            self.AfterRun()
        return self.retCode

    @abstractmethod        
    def BeforeRun(self):
        debug('entering class Action::BeforeRun')
        pass

    def AfterRun(self):
        debug('entering class Action::AfterRun')
        return None

    def AddCmd(self, cmdStr):
        debug('entering class Action::AddCmd')
        self.__cmds.append(cmdStr)

    def GetCmd(self):
        return self.__cmds
            
    def HandleOutput(self, cmd, retCode, retContent):
        debug('entering class Action::HandleOutput')        
        print('COMMAND=%s' % cmd)
        print('\treturn_code=%s' % retCode)
        print('\toutput=\n%s' % retContent)
    
# end of class Action

def main():
    basicConfig(level=DEBUG)
    act = Action()
    act.AddCmd('cd ~/try; ls -l | wc -l')
    act.AddCmd('echo hello')
    print('GetCmd():%s' % act.GetCmd())
    act.Run()

if __name__ == '__main__':
    main()
