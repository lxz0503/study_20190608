import sys

jiraLibPath = '/folk/lchen3/share/Jira'
if jiraLibPath not in sys.path:
    sys.path.insert(0, jiraLibPath) 

from JiraSelector import JiraSelector, Issue

class JiraDefect:
    def __init__(self):
        self.kongDefectJql = 'status in (Open, "In progress", Reopened, Accepted, Committed, "On Hold", \
                              Assigned, New_Incomplete, New) AND labels in (Kong) AND (project = V7BC OR \
                              project = V7LIBC OR project = V7CON OR project = V7COR OR project = V7DBG OR \
                              project = V7GFX OR project = V7MAN OR project = V7NET OR project = V7PRO OR \
                              project = V7SEC OR project = V7STO OR project = WB4 OR project = TCLLVM OR \
                              project = HELIX)'
        issues = [Issue(x) for x in JiraSelector().SearchDefects(self.kongDefectJql)]
        self.defects = [(x.key, x.internalDescription, x.status) for x in issues]
        
    def GetDefect(self, testCaseWithIPVersion, splitter='<br>'):            
        rets = []
        testCase = testCaseWithIPVersion.split('-')[0]
        for key, intDpt, status in self.defects:
            if intDpt.find(testCase) != -1:
                rets.append( (key, status) )
        if rets:
            return splitter.join([x[0] for x in rets]), splitter.join([x[1] for x in rets])
        else:
            return 'none', 'none'
    
def main():    
    jiraDefect = JiraDefect()
    print jiraDefect.GetDefect('ipipsec.ipipsec.esp_tfc_timeout-IPv4')
    print jiraDefect.GetDefect('notexistedtestcase-IPv6')

if __name__ == '__main__':
    main()
