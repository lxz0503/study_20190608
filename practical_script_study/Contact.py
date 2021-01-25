#!/usr/bin/env python

import os, sys
from commands import getoutput
from Action import ExecCmd

class Contact(object):
    def __init__(self, fileName):
        self.contacts = {}
        fname = os.path.dirname(os.path.realpath(__file__)) + '/' + fileName
        if not os.path.exists(fname):
            print 'cannot find the data file:%s' % fname
            sys.exit(1)
        with open(fname, 'r') as fd:
            fc = fd.read()
        for line in [ x for x in fc.split('\n') if x != '' ]:
            #Arch Hughes|Senior Project Manager - Services|Services COS|Professional Services Cost|Employee|+1-858-535-5122|+1-858-344-2051|ahughes|arch.hughes@windriver.com|San Diego|3634|http://internal.wrs.com:8080/employeedirectory/main.jsp?manager_id=3634|Carl H Forsman
            name, title, dept, _, employType, _, _, loginName, email, city, employId, _, manager = line.split('|')
            i = manager.find('(')
            if i != -1:
                manager = manager[i+1:].replace(')', '')
            if employId in self.contacts:
                print '?? dup employId %s and name %s' % (employId, name)
            self.fields = ['name', 'title', 'loginName', 'email', 'city', 'manager', 'employId']
            self.contacts[employId] = (name, title, loginName, email, city, manager, employId)


    def GetFullName(self, loginName): 
        # first, search in this contact.txt file     
        ret = self.__Query('loginName', loginName, 'name')
        if ret !=  '':
            return ret
        else:
            # if not found, then use yellow page
            cmd = 'ypcat passwd | grep \"^%s\"' % loginName
            retCode, output = ExecCmd(cmd)
            if retCode != 0:
                return ''
            else:
                fullName = output.split(':')[4]
                if fullName.find('.') != -1:
                    fullName = fullName.replace('.', ' ')
                return fullName

                    
    def GetEmail(self, loginName):
        ret = self.GetFullName(loginName)
        if ret ==  '':
            return ret
        else:
            # match by name first
            email = self.__Query('name', ret, 'email')
            if email == '':
                # match by email secondly
                retEmail = ret.replace(' ', '.') + '@windriver.com'
                ret = self.__Query('email', retEmail, 'email')
                return ret
            return email

           
    def GetMgrName(self, loginName):
        fullName = self.GetFullName(loginName)
        if fullName == '':
            return ''
        else:
            # match by name first
            mgr = self.__Query('name', fullName, 'manager')
            if mgr == '':
                # match by email secondly
                retEmail = fullName.replace(' ', '.') + '@windriver.com'
                ret = self.__Query('email', retEmail, 'manager')
                return ret
            else:
                i = mgr.find('(')
                if i != -1:
                    mgr = mgr[i+1:].replace(')', '')
                return mgr


    def GetMgrEmail(self, loginName):
        manager = self.GetMgrName(loginName)
        if manager == '':
            return ''
        else:
			email = self.__Query('name', manager, 'email')
			return email


    def GetFields(self):
        return self.fields
        
        
    def __Query(self, fieldToCompare, fieldValue, newFieldToReturn):
        assert fieldToCompare in self.GetFields()
        assert newFieldToReturn in self.GetFields()
        
        i = self.GetFields().index(fieldToCompare)
        j = self.GetFields().index(newFieldToReturn)
        for v in self.contacts.values():
            if v[i].lower() == fieldValue.lower():
                return v[j]
        return ''
			
