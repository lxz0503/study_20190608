#!/usr/bin/env python
# LTAF interface to read/write LTAF data

# configuration field
#    vx7-SR0620-features has not it
#    vx7-SR0621-STIG-EAR has it        (tr_kf11)
#    vx7-SR0640-features-native has it (tr_kf14)
#    vx7-integration-native has it     (tr_kf14)

import argparse
import os
import requests
import sys

from commands import getoutput
from lxml.html import fromstring

class InternalError(BaseException):
    pass

class HtmlFetcher:
    def __init__(self, url):
        self.url = url
        
    def GetHtml(self):
        r = requests.get(self.url, stream=True)
        return r.content
    
        
class NightlyTestReader(HtmlFetcher):
    def __init__(self, release, component, tags, reportDate, perPage=3000, tester=None):
        self.release = release
        self.component = component
        self.tags = tags
        self.reportDate = reportDate
        self.tester = tester        
        self.perPage = perPage
        if self.tester is not None:
            self.url = 'http://pek-lpgtest3.wrs.com/ltaf/nightly_results.php?releasename=%s&clearfilter=true&tf_test_component=%s&tf_tr_tester=%s&tf_tr_tags=%s&tf_tr_whentostart=%s&tf_per_page=%s' % (self.release, self.component, self.tester, self.tags, self.reportDate, self.perPage)
        else:
            self.url = 'http://pek-lpgtest3.wrs.com/ltaf/nightly_results.php?releasename=%s&clearfilter=true&tf_test_component=%s&tf_tr_tags=%s&tf_tr_whentostart=%s&tf_per_page=%s' % (self.release, self.component, self.tags, self.reportDate, self.perPage)
        print self.url
        
        
def PrintList(theList):
    for x in theList: 
        print '%s\n' % x
    print 'total=%s' % len(theList)
    print


class Record(object):
    def __init__(self, testName, testSuite, status, log, component, tester,  automation, requirement, trDomain, bsp, board, spin, tags, updateTime, funcPass, funcFail, defects, comment, tech, configLabel, configuration):
        self.testName = testName
        self.testSuite = testSuite
        self.status = status
        self.log = log
        self.component = component
        self.tester = tester
        self.automation = automation
        self.requirement = requirement
        self.trDomain = trDomain
        self.bsp = bsp
        self.board = board
        self.spin = spin
        self.tags = tags
        self.updateTime = updateTime
        self.funcPass = funcPass
        self.funcFail = funcFail
        self.defects = defects
        self.comment = comment
        self.tech = tech
        self.configLabel = configLabel
        self.configuration = configuration
    
    def __eq__(self, other):
        for attr in [ x for x in self.__dict__.keys() if x not in ('updateTime',) ]:
            selfAttr = eval('self.%s' % attr)
            otherAttr = eval('other.%s' % attr)
            if selfAttr != otherAttr:
                return False
        return True
        

class NightlyRecord(Record):
    def __init__(self, testName, testSuite, runDate, status, log, component, tester,  automation, requirement, trDomain, bsp, board, spin, tags, updateTime, funcPass, funcFail, defects, comment, tech, configLabel, configuration):
        super(NightlyRecord, self).__init__(testName, testSuite, status, log, component, tester,  automation, requirement, trDomain, bsp, board, spin, tags, updateTime, funcPass, funcFail, defects, comment, tech, configLabel, configuration)
        self.runDate = runDate

    def __str__(self):
        return 'testName = %s, ' % self.testName + \
               'testSuite = %s, ' % self.testSuite + \
               'runDate = %s, ' % self.runDate + \
               'status = %s, ' % self.status + \
               'log = %s, ' % self.log + \
               'component = %s, ' % self.component + \
               'tester = %s, ' % self.tester + \
               'automation = %s, ' % self.automation + \
               'requirement = %s, ' % self.requirement + \
               'trDomain = %s, ' % self.trDomain + \
               'bsp = %s, ' % self.bsp + \
               'configLabel = %s, ' % self.configLabel + \
               'tech = %s, ' % self.tech + \
               'board = %s, ' % self.board + \
               'configuration = %s, ' % self.configuration + \
               'spin = %s, ' % self.spin + \
               'tags = %s, ' % self.tags + \
               'updateTime = %s, ' % self.updateTime + \
               'funcPass = %s, ' % self.funcPass + \
               'funcFail = %s, ' % self.funcFail + \
               'defects = %s,' % self.defects + \
               'comments = %s' % self.comment


class LTAFTestResult:
    def __init__(self):
        self.tree = None
        self.testNameXpath = '//form[@name="testruns_form"]/div/table/tr[@name="trbeforeck"]'
        self.namespaces = {'re': "http://exslt.org/regular-expressions"}
        self.htmlTitleNameMap = {
                             'testName'         :             'Test Name',     
                             'testSuite'        :             'Test Suite',
                             'runDate'          :             'Run Date',  
                             'status'           :             'Status',
                             'log'              :             'Log',
                             'component'        :             'Component',
                             'tester'           :             'Tester',
                             'automation'       :             'Automation',
                             'requirement'      :             'Requirement',
                             'trDomain'         :             'TR Domain',
                             'funcPass'         :             'Func Pass',
                             'funcFail'         :             'Func Fail',
                             'bsp'              :             'BSP',
                             'board'            :             'Board', 
                             'spin'             :             'Spin', 
                             'tags'             :             'Tags',
                             'updateTime'       :             'Update Time',
                             'defects'          :             'Defects',
                             'comment'          :             'Comments',
                             'tech'             :             'Tech',
                             'configLabel'      :             'Config Label',
                             'configuration'    :             'Configuration',
                            }

    def GetRecords(self, html):
        self.tree = fromstring(html)
        return self.parse()
        
    def parse(self):
        records = []
        elems = self.tree.xpath(self.testNameXpath, namespaces=self.namespaces)
        table = elems[0].getparent()
        
        titles = table.find_class('tbl_header')
        htmlTitles = self.__parseTitle(titles)
        
        trs = table.find_class('tr_result')
        children = table.getchildren()
        for tr in trs:
            r = self.__parseOneTestRun(tr, htmlTitles)
            records.append(r)
        return records

    def __parseTitle(self, titles):
        htmlTitles = []
        for th in titles[0]:
            content = th.text_content().strip()
            if content:
                htmlTitles.append(content)
            else:
                inputTag = th.find('input')
                if inputTag is None:
                    htmlTitles.append('')
                else:
                    htmlTitles.append(inputTag.value)
        return htmlTitles            

    def __parseOneTestRun(self, tr, htmlTitles):
        record = {}

        tds = tr.getchildren()
        for nightlyRecordField in self.htmlTitleNameMap.keys():
            htmlTitle = self.htmlTitleNameMap[nightlyRecordField]
            if htmlTitle in htmlTitles:
                j = htmlTitles.index(htmlTitle)
                content = tds[j].text_content().strip()
                if not content:
                    if nightlyRecordField == 'status':
                        content = tds[j].find('div/img').get('title')
                    elif nightlyRecordField == 'log':
                        content = tds[j].find('div').get('value')        
                record[nightlyRecordField] = content
            else:
                # some LTAF releases do not have configuration field (see the comments
                # at the beginning, just assign it to null string
                record[nightlyRecordField] = ''
        return NightlyRecord(**record)            

        
"""                
class LTAFTestResult:
    def __init__(self):
        self.tree = None
        self.namespaces = {'re': "http://exslt.org/regular-expressions"}

        self.titles = ('testName', 'testSuite', 'runDate', 'status', 'log', 'component', 'tester',  'automation', 'requirement', 'trDomain', 'funcPass', 'funcFail', 
                       'bsp', 'board', 'spin', 'tags', 'updateTime', 'defects', 'comment', 'configLabel', 'configuration')
        self.xpaths = {
            'testName'    : '//form[@name="testruns_form"]/div/table/tr[@name="trbeforeck"]/td[3]',
            'testSuite'   : '//form[@name="testruns_form"]/div/table/tr[@name="trbeforeck"]/td[4]',
            
            # runDate uses /text() as xpath, it might return the list without empty string
            # however, runDate is always filled up
            'runDate'     : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_whentostart")]/text()',
            
            # @sth should be handled specifically as it returns string list
            'status'      : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_status")]/div/@value',
            'log'         : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_log")]/div/a/@href',
            
            'component'   : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_test_component")]/text()',
            'tester'      : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_tester")]/div',
            'automation'  : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_test_automation")]/text()',
            'requirement' : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_requirement")]/div/a',
            'trDomain'    : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_domain")]/div',
            'funcPass'    : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_function_pass")]/div',
            'funcFail'    : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_function_fail")]/div',
            'bsp'         : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_kf2")]/text()',
            'board'       : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_kf7")]/text()',
            'spin'        : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_ef5")]/div',
            'tags'        : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_tags")]/div',
            'updateTime'  : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_updatetime")]/text()',
            
            'defects'     : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_defects")]/div/@value',
            'comment'     : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_comments")]/div',
            
            'configLabel'   : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_kf3")]/text()',
            'configuration' : '//tr[@name="trbeforeck"]/td[re:test(@id, ".*?_tr_kf11")]/text()',
            }


    def GetTitles(self):
        return self.titles


    def GetRecords(self, html):
        rets = self.__ParseHtml(html)
        titles = self.GetTitles()
        
        return map(lambda x: NightlyRecord(x[titles.index('testName')], 
                                           x[titles.index("testSuite")],
                                           x[titles.index("runDate")],
                                           x[titles.index("status")],
                                           x[titles.index("log")],
                                           x[titles.index("component")],
                                           x[titles.index("tester")],
                                           x[titles.index("automation")],
                                           x[titles.index("requirement")],
                                           x[titles.index("trDomain")],
                                           x[titles.index("bsp")],
                                           x[titles.index("board")],
                                           x[titles.index("spin")],
                                           x[titles.index("tags")],
                                           x[titles.index("updateTime")],
                                           x[titles.index("funcPass")],
                                           x[titles.index("funcFail")],
                                           x[titles.index("defects")],
                                           x[titles.index("comment")],
                                           x[titles.index("configLabel")],
                                           x[titles.index("configuration")],
                                           ), rets)
    
                
    def __ParseHtml(self, html):
        self.tree = fromstring(html)
        
        testNames = self.__GetTestNames()
        num = len(self.titles)
        rets = []

        for title in self.titles[:num]:
            if title == 'testName':
                values = self.__GetTestNames()
            else:
                values = self.__GetElements(self.xpaths[title], namespaces=self.namespaces)
                if values == []:
                    values = [''] * len(rets[0])
            if True:
                print('=== %s :(%s):%s' % (title, len(values), values))
            if rets != [] and len(values) != len(rets[-1]): # defensive check
                theBefore = self.titles[self.titles.index(title) - 1]
                raise InternalError('the number of %s\'s column (%s) not match the number of %s\'s column (%s)' % (title, len(values), theBefore, len(rets[-1])))
            rets.append( values )
        return zip(*rets)
        

    def __GetTestNames(self):
        return self.__GetElements(self.xpaths['testName'])


    def __GetElements(self, xpath, namespaces=None):
        if namespaces is not None:
            elems = self.tree.xpath(xpath, namespaces=namespaces)
            if xpath.split('/')[-1].find('@') != -1 or xpath.split('/')[-1] == 'text()':
                return elems
            else:            
                return [x.text if x.text else '' for x in elems]
        else:
            elems = self.tree.xpath(xpath)
            if xpath.split('/')[-1].find('@') != -1 or xpath.split('/')[-1] == 'text()':
                return elems
            else:
                return [x.text if x.text else '' for x in elems]
"""            


class LTAFWriter(object):
    def __init__(self, release):
        self.records = []
        self.release = release


    # this function should not be used since it assumes that test case meta data
    # will be synced up to LTAF first 
    def CreateTestCaseFile(self, 
                             release, 
                             testsuite, 
                             component, 
                             testCaseType, 
                             feature, 
                             testName, 
                             testDate):
        contentTmpl = """[TEST_CONFIG]
TEST_SUITE_NAME = {R_TESTSUITE_R}
COMPONENT= {R_COMPONENT_R}
TEST_CASE_TYPE = {R_TESTCASETYPE_R}
FEATURE = {R_FEATURE_R}
AUTOMATION = yes
RCA = no

TEST_CASE_LIST = "
{R_ALLTESTCASE_R}
"

GIT_LINK = "none"

CREATED_DATE = {R_CREATEDATE_R}

RELEASE_NAME = {R_RELEASENAME_R}
"""
        content = contentTmpl.format(R_RELEASENAME_R = release,
                                    R_TESTSUITE_R = testsuite,
                                    R_COMPONENT_R = component,
                                    R_TESTCASETYPE_R = testCaseType,
                                    R_FEATURE_R = feature,
                                    R_ALLTESTCASE_R = testName,
                                    R_CREATEDATE_R = testDate,
                                    )
            
        tempFile = './ltaf_test_case.conf.temp'
        with open(tempFile, 'w') as fd:
            fd.write(content)
            
        return tempFile
    
    
    def CreateTestRunFile(self,
                          spinType,
                          release, 
                          testName, 
                          testsuite, 
                          component, 
                          domain,
                          sprint, 
                          week, 
                          bsp, 
                          spin, 
                          testResult, 
                          tag, 
                          tester, 
                          board, 
                          build, 
                          buildOption, 
                          log, 
                          funcPass,
                          funcFail,
                          defects,
                          requirement,
                          comment,
                          tech,
                          configLabel,
                          configuration,
                          ):
        contentTmpl = """[LTAF]
action = add_update

release_name = {R_RELEASENAME_R}

test_name = {R_TESTCASE_R}
test_suite = {R_TESTSUITE_R}
test_component = {R_COMPONENT_R}
domain = {R_DOMAIN_R}

sprint = {R_SPRINT_R}
week = {R_WEEK_R}

bsp = {R_BSP_R}
spin = {R_SPIN_R}

status = {R_TESTRESULT_R}
tags = {R_TAGS_R}
tester = {R_TESTER_R}
board = {R_BOARD_R}
log = {R_LOG_R}

# build for branch info
build = {R_BUILD_R}
# buildoptions for commit info
buildoptions = {R_BUILDOPTIONS_R}

defects = {R_DEFECTS_R}

requirements = {R_REQUIREMENT_R}

function_pass = {R_FUNCPASS_R}
function_fail = {R_FUNCFAIL_R}
SpinType = {R_SPINTYPE_R}
comments = '{R_COMMENT_R}'

tech = {R_TECH_R}
config label = {R_CONFIGLABEL_R}
configuration = {R_CONFIG_R}
"""
           
        content = contentTmpl.format(R_SPINTYPE_R = spinType,
                                     R_RELEASENAME_R = release,
                                     R_TESTCASE_R = testName,
                                     R_TESTSUITE_R = testsuite,
                                     R_COMPONENT_R = component,
                                     R_DOMAIN_R = domain,
                                     R_SPRINT_R = sprint,
                                     R_WEEK_R = week,
                                     R_BSP_R = bsp,
                                     R_SPIN_R = spin,
                                     R_TESTRESULT_R = testResult,
                                     R_TAGS_R = tag,
                                     R_TESTER_R = tester,
                                     R_BOARD_R = board,
                                     R_BUILD_R = build,
                                     R_BUILDOPTIONS_R = buildOption,
                                     R_LOG_R = log,
                                     R_FUNCPASS_R = funcPass,
                                     R_FUNCFAIL_R = funcFail,
                                     R_DEFECTS_R = defects,
                                     R_REQUIREMENT_R = requirement,
                                     R_COMMENT_R = comment,
                                     R_TECH_R = tech,
                                     R_CONFIGLABEL_R = configLabel,
                                     R_CONFIG_R = configuration,
                                    )

        tempFile = './ltaf_test_run.conf.temp'         
        with open(tempFile, 'w') as fd:
            fd.write(content)
            
        return tempFile

        
# The difference:
# release test record : Planned Sprint,  Planned Week; uses upload_results.php
# nightly test record : Run Date; uses upload_nightly_results.php

class ReleaseReportWriter(LTAFWriter):
    def __init__(self, spinType, release, plannedSprint, plannedWeek, requirement=None, log=None, trDomain=None, testCaseType='functional', feature='KONG', build='', buildOption=''):
        assert spinType in ('native', 'helix')
        self.interface = 'upload_results.php'
        super(ReleaseReportWriter, self).__init__(release)

        # use to create test case
        self.testCaseType = testCaseType
        self.feature = feature
        # use to create test run
        self.plannedSprint = plannedSprint
        self.plannedWeek = plannedWeek
        self.build = build
        self.buildOption = buildOption
        self.requirement = requirement
        self.log = log
        self.trDomain = trDomain
        self.spinType = spinType

        
    def AddTestResult(self, nightlyRecord):
        self.records.append(nightlyRecord)

    
    def Store(self):
        for r in self.records:
            if False:
                # add test case to LTAF
                tempTCFile = self.CreateTestCaseFile(self.release, r.testSuite, r.component,   
                                                     self.testCaseType, self.feature, r.testName, self.plannedWeek)
                cmd = 'curl -F testfile=@%s http://pek-lpgtest3.wrs.com/ltaf/%s' % (tempTCFile, self.testCaseInterface)
                print getoutput(cmd)
                print
            
            # add test run results to LTAF
            requirement = self.requirement if self.requirement is not None else r.requirement
            log = self.log if self.log is not None else r.log
            trDomain = self.trDomain if self.trDomain is not None else r.trDomain
            tempTRFile = self.CreateTestRunFile(self.spinType, self.release, r.testName, r.testSuite, r.component, trDomain,  
                                                self.plannedSprint, self.plannedWeek, r.bsp, r.spin, r.status, r.tags, r.tester, r.board, self.build, 
                                                self.buildOption, log, r.funcPass, r.funcFail, r.defects, requirement, r.comment, r.tech, r.configLabel, r.configuration)
            # release report uses upload_results.php while nightly report uses upload_nightly_results.php
            cmd = 'curl -F resultfile=@%s http://pek-lpgtest3.wrs.com/ltaf/%s' % (tempTRFile, self.interface)
            print '\nupload release=%s testname=%s component=%s domain=%s' % (self.release, r.testName, r.component, trDomain)
            print getoutput(cmd)
            print


class NightlyReportWriter(LTAFWriter):
    def __init__(self, spinType, release, runDate, domain=None, testCaseType='functional', feature='KONG', build='', buildOption=''):
        assert spinType in ('native', 'helix', 'git')
        self.testCaseInterface = 'upload_test.php'
        self.testRunInterface = 'upload_nightly_results.php'
        super(NightlyReportWriter, self).__init__(release)
        
        # use to create test case
        self.testCaseType = testCaseType
        self.feature = feature
        # use to create test run
        self.plannedSprint = 'Nightly'
        self.plannedWeek = runDate
        self.build = build
        self.buildOption = buildOption
        self.domain = domain
        self.spinType = spinType

        
    def AddTestResult(self, nightlyRecord):
        if isinstance(nightlyRecord, NightlyRecord):
            self.records.append(nightlyRecord)
        else:
            raise InternalError('nightlyRecord should be an instance of class NightlyRecord')

    
    def Store(self):
        for r in self.records:
            if False:
                # add test case to LTAF
                tempTCFile = self.CreateTestCaseFile(self.release, r.testSuite, r.component,   
                                                     self.testCaseType, self.feature, r.testName, self.plannedWeek)
                cmd = 'curl -F testfile=@%s http://pek-lpgtest3.wrs.com/ltaf/%s' % (tempTCFile, self.testCaseInterface)
                print getoutput(cmd)
                print
                        
            # add test run results to LTAF
            domain = self.domain if self.domain is not None else r.trDomain
            testName = ConvertTestNameToLTAF(r.testName)
            tempTRFile = self.CreateTestRunFile(self.spinType, self.release, testName, r.testSuite, r.component, domain,  
                                                self.plannedSprint, self.plannedWeek, r.bsp, r.spin, r.status, r.tags, r.tester, r.board, self.build, 
                                                self.buildOption, r.log, r.funcPass, r.funcFail, r.defects, r.requirement, r.comment, r.tech, r.configLabel, r.configuration)
            # release report uses upload_results.php while nightly report uses upload_nightly_results.php
            cmd = 'curl -F resultfile=@%s http://pek-lpgtest3.wrs.com/ltaf/%s' % (tempTRFile, self.testRunInterface)
            print '\nupload release=%s testname=%s component=%s domain=%s' % (self.release, r.testName, r.component, domain)
            print getoutput(cmd)
            print

    
def ConvertTestNameToLTAF(kongTestName):
    return kongTestName.replace(' ', '')


def ConvertTestResultToLTAF(kongTestResult):
    """ LTAF : Pass, Fail, Blocked, Notstarted """
    if kongTestResult.lower() == 'ok':
        return 'Pass'
    elif kongTestResult.lower() == 'failed':
        return 'Fail'
    elif kongTestResult.lower() == 'blocked':
        return 'Blocked'
    else:
        return None


def main_nightly_to_release_writer():
    print '=== nightly_to_release'
    # release report setup information
    release = 'vx7-SR0541-features'         # need to update
    component = 'networking'
    tags = 'KONG-nightly'
    tester = 'KONG'
    plannedSprint = 'Sprint 59 - Ending 2019-08-02'    # need to update
    plannedWeek = 'week 1'              # need to update
    requirement = 'VXWEXEC-6871'            # need to update
    log = 'http://pek-cc-pb08l/vxtest/vxtest1/LOG_VX7/Vx-7_Networking-Kong/vx7-SR0541-features' # need to update
    spinType = 'native'

    # nightly report setup information
    reportDate = '2019-07-24'   # need to update, coming from nightly report Run Date

    fetcher = NightlyTestReader(release, component, tags, reportDate, 3000, tester)
    html = fetcher.GetHtml()
    
    nightlyResult = LTAFTestResult()
    records = nightlyResult.GetRecords(html)
    PrintList(records)

    writer = ReleaseReportWriter(spinType, release, plannedSprint, plannedWeek, requirement, log, trDomain='networking')
    for x in records:
        writer.AddTestResult(x)

    print '\nWill upload to release "%s" from nightly test on date %s' % (release, reportDate)
    k = raw_input('upload? (y/n)')
    if k == 'y':
        writer.Store()
        print 'test cases uploaded'
    else:
        print 'not uploaded'


def main_nightly_to_nightly_writer():
    print '=== nightly_to_nightly'
    # release report setup information
    releaseFrom = 'vx7-integration-helix'
    #releaseFrom = 'vx7-integration'
    #releaseTo = 'vx7-integration'
    releaseTo = 'vx7-SR0630-features-helix'
    component = 'networking'
    tags = 'KONG-helix-nightly'
    fromDate = '2019-10-10'
    toDate = '2019-10-10'
    spinType = 'helix'
    
    # read nightly test results on one date
    fetcher = NightlyTestReader(releaseFrom, component, tags, fromDate)
    html = fetcher.GetHtml()
    
    nightlyResult = LTAFTestResult()
    records = nightlyResult.GetRecords(html)
    PrintList(records)

    # write nightly test results on the other date
    writer = NightlyReportWriter(spinType, releaseTo, toDate)

    for x in records:
        writer.AddTestResult(x)
    writer.Store()


def ReplaceRecord(x, bsp, testName, testSuite, status, comment):
    assert isinstance(x, Record)
    x.bsp = bsp
    x.testName = testName
    x.testSuite = testSuite
    x.comment = comment
    x.status = status
    if status == 'Pass':
        x.funcPass = 1
        x.funcFail = 0
    else:
        x.funcPass = 0
        x.funcFail = 1
    return x


def parseArgument(argv):
    parser = argparse.ArgumentParser(description='Update LTAF nightly test result')
    parser.add_argument('-f', action='store', dest='configFile', help='specify the config Python file (e.g. LTAFupdate.py) to update nightly tests (required)')
    args = parser.parse_args()

    if args.configFile is None:
        parser.print_help()
        exit(1)

    return args


def readUpdateConfigFile(pyConfigFile):
    if not os.path.exists(pyConfigFile):
        print('%s not found' % pyConfigFile)
        sys.exit(1)
    from importlib import import_module
    modName = pyConfigFile.replace('.py', '')
    m = import_module(modName)
    return m.releaseFrom, m.releaseTo, m.component, m.tags, m.fromDate, m.toDate, m.spinType, m.testsToUpdate 


def test_readRerunFile():
    tests = readUpdateConfigFile('LTAFupdate.py')
    print len(tests)
    print tests[0]
    

def test_read_nightly_records():
    print '=== read nightly and write nightly'
    # release report setup information
    release = 'vx7-integration-helix'         # need to update
    #component = 'networking'
    component = 'hypervisor'
    #tags = 'KONG-nightly'
    tags = ''
    #tester = 'KONG'
    tester = 'zluo1'
    reportDate = '2019-08-20'

    fetcher = NightlyTestReader(release, component, tags, reportDate, 200, tester)
    html = fetcher.GetHtml()
    
    nightlyResult = LTAFTestResult()
    records = nightlyResult.GetRecords(html)
    PrintList(records)

def test_write_nightly_records():
    nightlyRecord = {
                     'testName' : 'ipike.advanced.napt_liveness1-IPv4',
                     'testSuite' : 'IKE-ADVANCED',
                     'runDate' : '2019-08-22',     
                     'status' : 'Pass',      
                     'log' : 'https://jira.wrs.com/browse/V7NET-2530',   
                     'component' : 'networking',   
                     'tester' : 'kong-helix',
                     'automation' : 'Auto',  
                     'requirement' : '',
                     'trDomain' : 'networking',
                     'funcPass' : '1',   
                     'funcFail' : '0',    
                     'bsp' : 'itl_generic',      
                     'board' : '',       
                     'spin' : '123',      
                     'tags' : '456',
                     'updateTime' : '',  
                     'defects' : '',   
                     'comment' : 'no comment',    
                     'tech' : 'dynamic', 
                     'configLabel' : 'vx7smp64-vx7smp64',
                     'configuration' : 'hello', 
                    }
    
    x = NightlyRecord(**nightlyRecord)
    spinType = 'native'
    release = 'vx7-integration-helix'     
    toDate = '2019-08-30'
    
    # write nightly test results on the other date
    writer = NightlyReportWriter(spinType, release, toDate)
    writer.AddTestResult(x)

    print '\nWill upload to LTAF nightly release %s on %s' % (release, toDate)
    k = raw_input('upload? (y/n)')
    if k == 'y':
        writer.Store()
        print 'test cases uploaded'
    else:
        print 'not uploaded'


def main_update_Helix_LTAF_record():
    def readTestCase(testResultFileWithOk):
        testCases = []
        with open(testResultFileWithOk, 'r') as fd:
            lines = fd.readlines()
            for line in lines:
                testCases.append( line.split(' ETA:')[0].strip().replace(' ', '') )
        return testCases
    
    # data required to modify
    spinType = 'helix'
    release = 'vx7-SR0630-features-helix'     
    toDate = '2019-10-25'
    bsp = 'nxp_layerscape_a72'
    spin = 'vx20191023224252_vx7-SR0630-helix'
    configLabel = 'vx7smp32'
    configuration = 'Dynamic'
    testSuite = 'SYSVIEW'
    
    nightlyRecord = {
                     'testName' : 'to-be-replaced',
                     'testSuite' : testSuite,
                     'runDate' : toDate,     
                     'status' : 'Pass',      
                     'log' : '',   
                     'component' : 'networking',   
                     'tester' : 'KONG',
                     'automation' : 'Auto',  
                     'requirement' : '',
                     'trDomain' : 'networking',
                     'funcPass' : '1',   
                     'funcFail' : '0',    
                     'bsp' : bsp,
                     'board' : '',       
                     'spin' : spin,      
                     'tags' : 'KONG-helix-nightly',
                     'updateTime' : '',  
                     'defects' : '',   
                     'comment' : 'rerun passed',    
                     'tech' : 'guestOS', 
                     'configLabel' : configLabel,
                     'configuration' : configuration, 
                    }
    
    x = NightlyRecord(**nightlyRecord)
    
    testCases = readTestCase('LTAF_record_to_update')
    
    # write nightly test results on the other date
    writer = NightlyReportWriter(spinType, release, toDate)
    
    for testCase in testCases:
        x = NightlyRecord(**nightlyRecord)
        x.testName = testCase
        writer.AddTestResult(x)
        print('%s\n' % x)

    print '\nWill upload to LTAF nightly release %s on %s' % (release, toDate)
    k = raw_input('upload? (y/n)')
    if k == 'y':
        writer.Store()
        print 'test cases uploaded'
    else:
        print 'not uploaded'

    
def main_update_LTAF_record():
    print '=== update some records at nightly report'

    args = parseArgument(sys.argv)
    releaseFrom, releaseTo, component, tags, fromDate, toDate, spinType, testsToUpdate = readUpdateConfigFile(args.configFile)

    # read nightly test results on one date
    fetcher = NightlyTestReader(releaseFrom, component, tags, fromDate)
    html = fetcher.GetHtml()
    
    nightlyResult = LTAFTestResult()
    records = nightlyResult.GetRecords(html)
    print '%s records retrieved' % len(records)
    
    # write nightly test results on the other date
    writer = NightlyReportWriter(spinType, releaseTo, toDate)

    for i in xrange(len(testsToUpdate)):
        x = records[i]
        bsp, testName, testSuite, status, comment = testsToUpdate[i]
        newRecord = ReplaceRecord(x, bsp, testName, testSuite, status, comment)
        writer.AddTestResult(newRecord)

    print '\n== upload the test cases to %s on %s' % (releaseTo, toDate)    
    PrintList(writer.records)
    
    # confirm for last time
    print '\nWill upload to release "%s" on date %s by using %s' % (releaseTo, toDate, args.configFile)
    k = raw_input('upload? (y/n)')
    if k == 'y':
        writer.Store()
        print 'test cases uploaded'
    else:
        print 'not uploaded'
    
if __name__ == '__main__':
    #main_nightly_to_nightly_writer()
    main_update_Helix_LTAF_record()
    #main_update_LTAF_record()
    #test_read_nightly_records()
    #test_write_nightly_records()
