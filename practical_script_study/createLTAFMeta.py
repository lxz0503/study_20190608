from KongTestPlanToReport import kongTestPlanToReport
import os
import KongUtil

class ComponentMeta(object):
    def __init__(self, component, testCaseList):
        self.component = component
        self.testCases = self.__RemoveSpace(testCaseList)
        
        
    def __RemoveSpace(self, testCaseList):
        return map(lambda x: x.strip().replace(' ', ''), testCaseList)
        
        
    def CreateMetaFile(self, 
                        testSuite,
                        testType,
                        feature,
                        autoFlag,
                        description,
                        testCases,
                        gitLink,
                        createdDate,
                        ):
        contentTmpl = """[TEST_CONFIG]
TEST_SUITE_NAME = {testSuite}
COMPONENT = {component}
TEST_CASE_TYPE = {testType}
FEATURE = {feature}
AUTOMATION = {autoFlag}
RCA = no
DESCRIPTION = {description}
TRACEABILITY = 

TEST_CASE_LIST = "
{testCases}
"

GIT_LINK = "{gitLink}"
           
CREATED_DATE = {createdDate}

RELEASE_NAME = 
"""
        content = contentTmpl.format(testSuite = testSuite,
                                     component = self.component,
                                     testType = testType,
                                     feature = feature,
                                     autoFlag = autoFlag,
                                     description = description,
                                     testCases = '\n'.join([' '*4 + x for x in testCases]),
                                     gitLink = gitLink,
                                     createdDate = createdDate,
                                    )
            
        tempFile = './test_case.conf'
        with open(tempFile, 'w') as fd:
            fd.write(content)
            
        return tempFile


def main():
    for component in kongTestPlanToReport:
        testResults = kongTestPlanToReport[component]
        tests = sorted(testResults.keys())

        cwd = os.getcwd()
        os.mkdir(os.path.join(cwd, component))
        os.chdir(os.path.join(cwd, component))
        
        meta = ComponentMeta('networking-kong', tests)
        meta.CreateMetaFile(testSuite = component,
                            testType = 'Functional',
                            feature = component,
                            autoFlag = 'yes',
                            description = 'networking kong test cases for ' + component,
                            testCases = meta.testCases,
                            gitLink = 'http://git.wrs.com/cgit/projects/wassp-repos/testcases/vxworks7/tree/networking-kong/' + component,
                            createdDate = KongUtil.TodayStr(),
                            )
        os.chdir(cwd)
        
        
if __name__ == '__main__':
    main()
            
