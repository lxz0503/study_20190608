import os
import time
import requests

from KongV6TestSummary import WebFetcher, TinderMainPage, ModuleParser, kongV6SummaryPage
from KongRerunTest import CategorizeTestCaseResult

def LaunchRerun(rerunUrl):
    return WebFetcher(rerunUrl).GetHtml()
    
class NodeNotFound(BaseException):
    pass

class Rerunner:
    def __init__(self, timeout=140, interval=1):
        self.timeout = timeout      
        self.interval = interval    
        self.nodes = {
                        'UNIX-INTEL32' : 'BJ-LTH-S1',
                        'UNIX-INTEL64' : 'BJ-LTH-S3',
                     }
        self.reschedulePath = '/usr/local/TestHarness/reschedule'
        self.waitQueue = []


    def AddModule(self, module, url):
        self.waitQueue.append( (module, url) )

        
    def GetModule(self):
        if self.waitQueue == []:
            return None
        else:
            return self.waitQueue[0]


    def RemoveModule(self, moduleUrl):
        self.waitQueue.remove(moduleUrl)            

        
    def Run(self):
        """
        1) decide which node to check
        2) if no task at this node, then continue; or wait for rerunning to complete; or timeout to exit with error
        """
        start_time = time.time()
        
        while True:
            moduleUrl = self.GetModule()
            if moduleUrl is None:
                break   # exit since all queued job get done
            else:
                if self.IsNodeBusy(moduleUrl[0]):
                    print '%s busy and waiting ...' % self.nodes[moduleUrl[0][0:12]]
                    time.sleep(self.interval * 60)
                else:
                    self.RemoveModule(moduleUrl)
                    print 'waitQueue len=', len(self.waitQueue)
                    print 'launching ', moduleUrl[0]
                    LaunchRerun(moduleUrl[1])
                    time.sleep(6)   # wait for a while since the rerun can be launched
                    start_time = time.time()

            if (time.time() - start_time) >= (self.timeout * 60):
                print 'Rerunner timeout'
                break


    def IsNodeBusy(self, module):
        if module[0:12] in self.nodes:
            checkPath = self.reschedulePath + '/' + self.nodes[module[0:12]]
            if os.listdir(checkPath) == []:
                return False
            else:
                return True
        else:
            raise NodeNotFound('node not found for module %s' % module)


def main():
    mainPage = TinderMainPage(kongV6SummaryPage)
    modUrlTimes = mainPage.GetModules()
    
    totalTestResults = []
    moduleBuildFailed = []
    rerunner = Rerunner()
    for module, url, timestamp in modUrlTimes:
        modParser = ModuleParser(url)
        testResults = modParser.GetTestResult()
        numOk, numFail, numSkip = CategorizeTestCaseResult(testResults)   
        print module, numOk, numFail, numSkip
        if numFail != 0 or numOk == 0:
            #print '\trerun %s : %s' % (module, LaunchRerun(modParser.GetRerunUrl()))
            rerunUrl = modParser.GetRerunUrl()
            rerunner.AddModule(module, rerunUrl)
            
        #if not mainPage.IsBuildPassed(timestamp):
        #    print '\trerun build failed module %s : %s' % (module, LaunchRerun(modParser.GetRerunUrl()))
            
        del modParser

    rerunner.Run()

if __name__ == '__main__':
    main()
                
