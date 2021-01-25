from crontab import CronTab

from InstallSpin import GetSpinInfo

"""
1 21 * * * /folk/lchen3/try/workspace/PdvTool/vx7tool/new/KongNightly.sh --nightly 653SPIN
1 2 * * * /folk/lchen3/try/workspace/PdvTool/vx7tool/new/KongNightly.sh --nightly SPIN
"""

class SpinList:
    def __init__(self):
        #self.prioritizedSpins = ('SPIN', 'HELIXSPIN', 'CISPIN', '653SPIN')
        #self.prioritizedSpins = ('CISPIN', '653SPIN')
        self.prioritizedSpins = ('SPIN', 'CISPIN', '653SPIN')
        
    def GetSpins(self):
        spinNames = [x for x in self.prioritizedSpins if GetSpinInfo(x, 'name')]
        return spinNames        


class CronJob(object):
    def __init__(self, userName, jobName):
        self.cron = CronTab(user=userName)
        self.jobName = jobName
        self.slots = {0 : {'hour' : 21, 'minute' : 1},
                      1 : {'hour' : 2,  'minute' : 1},
                     }
        
    def RemoveJobs(self):
        jobs = self.cron.find_command(self.jobName)
        for job in jobs:
            self.cron.remove(job)
            self.cron.write()
        
    def AddJobs(self, jobs):
        numSlot = self.slots.keys()
        numJob = len(jobs)
        print(numSlot, numJob)
        if numJob <= numSlot:
            self.__AddToCronTab(jobs)
        else:
            self.__AddToCronTab(jobs[:numSlot])
    
    def __AddToCronTab(self, jobs):
        for i in xrange(len(jobs)):
            jobFullName = self.jobName + ' --nightly ' + jobs[i]
            print 'job=%s, at=%s %s' % (jobFullName, self.slots[i]['hour'], self.slots[i]['minute'])
            j = self.cron.new(command=jobFullName)
            j.hour.on(self.slots[i]['hour'])
            j.minute.on(self.slots[i]['minute'])
        """
        # use fixed time for SPIN / HELIXSPIN 
        if 'SPIN' in jobs or 'CISPIN' in jobs:
            jobFullName = self.jobName + ' --nightly SPIN'
            print 'job=%s, at=%s %s' % (jobFullName, self.slots[0]['hour'], self.slots[0]['minute'])
            j = self.cron.new(command=jobFullName)
            j.hour.on(self.slots[0]['hour'])
            j.minute.on(self.slots[0]['minute'])
        
        if 'HELIXSPIN' in jobs:
            jobFullName = self.jobName + ' --nightly HELIXSPIN'
            print 'job=%s, at=%s %s' % (jobFullName, self.slots[1]['hour'], self.slots[1]['minute'])
            j = self.cron.new(command=jobFullName)
            j.hour.on(self.slots[1]['hour'])
            j.minute.on(self.slots[1]['minute'])
        """
        self.cron.write()            
        

def main():
    spinList = SpinList()
    
    jobName = 'export DISPLAY=pek-vx-nwk1.wrs.com:4.0 && export USERNAME=svc-cmnet && /folk/lchen3/try/workspace/PdvTool/vx7tool/new/KongNightly.sh'
    cronJob = CronJob('svc-cmnet', jobName)
    
    cronJob.RemoveJobs()
    print '\n=== clear and add new jobs start'
    cronJob.AddJobs(spinList.GetSpins())
    print '=== clear and add new jobs done\n'
    
    
if __name__ == '__main__':
    main()
    
