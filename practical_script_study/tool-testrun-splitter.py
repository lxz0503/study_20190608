import math
from operator import itemgetter

from testDuration import testCaseDurations

def dict2list(theDict):
    theList = []
    for k in theDict:
        theList.append((k, theDict[k]))
    return theList


class TestTask(object):
    def __init__(self, module, duration, tests):
        self.module = module
        self.duration = duration
        self.tests = tests
    
    def __str__(self):
        return 'module=%s, ' % self.module + \
               'duration=%s, \n' % self.duration + \
               'tests=%s' % '\n'.join(['    %s' % x for x in self.tests])
    
class Splitter(object):
    def __init__(self, testCaseDurations):
        self.budgetTime = 60 * 30
        self.buildTime = 300
        self.testEnvReadyTime = 120
        
        self.taskBudget = self.budgetTime - self.buildTime - self.testEnvReadyTime
        
        self.durations = testCaseDurations
        self.bsp = 'vxsim_linux'
        self.modules = testCaseDurations[self.bsp].keys()
        
    
    def splitModule(self, module):
        modDuration = self.getModuleTime(module)
        tests = self.durations[self.bsp][module]
        if modDuration < self.taskBudget:
            testDurations = ['%s : %s' % (x, self.durations[self.bsp][module][x]) for x in tests]
            return [TestTask(module, modDuration, testDurations)]
        else:
            n = int(modDuration / self.taskBudget) + 1
            testTasks = self.arrangeTestCases(tests, n, self.taskBudget)
            if testTasks:
                return testTasks
            else:
                raise Exception('cannot split module %s' % module)
                
    
    def arrangeTestCases(self, testCaseWithDurations, numOfTasks, perTaskDuration):
        print('task budget=%s' % perTaskDuration)
        testDurations = dict2list(testCaseWithDurations)
        distributePairs(testDurations, numOfTasks)
            
    
    def distributePairs(thePairs, numOfList):
        thePairs = sorted(thePairs, key=itemgetter(1), reverse=True)
        
    def sortModule(self):
        modTimes = []
        for mod in self.modules:
            duration = self.getModuleTime(mod)
            modTimes.append((mod, duration))
        return sorted(modTimes, key=itemgetter(1), reverse=True)
    
        
    def getModuleTime(self, module):
        testTimes = self.durations[self.bsp][module]
        total = 0
        for tn in testTimes:
            total += testTimes[tn]
        return total
        
    
def main():
    s = Splitter(testCaseDurations)
    tasks = s.splitModule('NTP')
    for x in tasks: print(x)


def distributePairs(valueWeights, numOfSubList):
    def sumWeight(valueWeightPairs):
        if not valueWeightPairs:
            return 0
        else:
            return sum([x[1] for x in valueWeightPairs])
        
    valueWeights = sorted(valueWeights, key=itemgetter(1), reverse=False)
    totalWeight = sum([x[1] for x in valueWeights])
    averageWeight = int(math.ceil(totalWeight / numOfSubList))
    subLists = [[]] *  numOfSubList
    #weights = [0] * numOfSubList
    while valueWeights:
        v, w = valueWeights.pop()
        for x in xrange(numOfSubList):
            subTotalWeight = sumWeight(subList[x])
            if subTotalWeight < averageWeight:
                subList[x].append( (v, w) )
        if 

def test_distributePairs():
    vws = [('a', 10),
           ('b', 50),
           ('c', 20),
           ('d', 40),
           ('e', 30),
          ]
    subLists = distributePairs(vws, 3)
    print(subLists)

if __name__ == '__main__':
    #main()    
    test_distributePairs()
    