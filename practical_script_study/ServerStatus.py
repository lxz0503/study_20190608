#!/usr/bin/env python

from Config import *

class ServerStatus(object):
    def __init__(self):
        self.status = dict()
        self.__InitServerStatus()
        
        
    def __InitServerStatus(self):
        servers = GetServers()
        for server in servers:
            self.status[server] = 0
       
    def GetServers(self):
        return self.status.keys()
        
    def GetIdleServer(self):
        for k in self.status:
            if self.status[k] is 0:
                return k
        return None
            

    def SetBusyServer(self, server, buildId):
        self.status[server] = buildId

    def GetServerStatus(self, server):
        return self.status[server]
        
    def SetIdleServer(self, server):
        self.status[server] = 0 
        
# end of ServerStatus    
    
