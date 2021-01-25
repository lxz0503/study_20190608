import re
import requests
import sys
import urlparse
import HTMLParser

from datetime import date, datetime, timedelta
from lxml import html
from KongRerunTest import ParseTestResult, CategorizeTestCaseResult

kongV6SummaryPage = 'http://128.224.154.135/tinderbox/release6_9.panel.html'

class BuildLogError(BaseException):
    pass

class ConfigError(BaseException):
    pass
    
class HtmlError(BaseException):
    pass
        
class HtmlFetcher:
    def __init__(self, url):
        self.url = url

        
    def GetHtml(self):
        r = requests.get(self.url, stream=True)
        return r.content


class TinderMainPage:
    def __init__(self, htmlPage):
        self.url = htmlPage
        self.moduleXPath = '/html/body/table/tr/td[1]/a'
        self.timestampXPath = '/html/body/table/tr/td[3]'
    
    
    def GetModules(self):
        rets = []
        r = requests.get(self.url, stream=True)
        repairedHtml = self.__RepairTd(r.content)
        repairedHtml = self.__RepairTr(repairedHtml)
        tree = html.document_fromstring(repairedHtml)
        
        modules = tree.xpath(self.moduleXPath)
        timestamps = tree.xpath(self.timestampXPath)
        if len(modules) == len(timestamps):
            for i in xrange(len(modules)):
                rets.append( (modules[i].text, modules[i].get('href'), timestamps[i].text) )
        else:
            raise HtmlError
        return rets
        
    
    def IsBuildPassed(self, timestamp):
        # the first build starts at 20:00 yesterday; timestamp likes Tue Mar 14 03:34:59 2017
        buildTime = datetime.strptime(timestamp, '%a %b %d %H:%M:%S %Y')
        yesterday = date.today() + timedelta(days=-1)
        startTime = datetime(yesterday.year, yesterday.month, yesterday.day, 20, 00, 00)
        return buildTime >= startTime
        
    
    def __RepairTd(self, inputHtml):
        i, tdTag, start, newHtml = 0, 0, 0, ''
        while i < (len(inputHtml) - 4):
            currentToken = inputHtml[i:i+5]
            if currentToken[:3] == '<TD':
                if tdTag == 0:
                    tdTag = 1
                elif tdTag == 1:
                    #print 'found:%s:%s' % (i, inputHtml[i-24:i+5])
                    newHtml += inputHtml[start:i] + '</TD>'
                    start = i
                else:
                    raise HtmlError('parse html TD tag error')
            elif currentToken == '</TD>':
                tdTag = 0
            i += 1
        newHtml += inputHtml[start:]
        return newHtml


    def __RepairTr(self, inputHtml):
        trs = inputHtml.split('</TR>')
        header, trs0 = trs[0].split('<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=1>')
        newHtml = header + '<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=1><TR>' + trs0 + '</TR>'
        for x in trs[1:-1]:
            newHtml += '<TR>' + x + '</TR>'
        newHtml += trs[-1]
        return newHtml


class ModuleParser:
    def __init__(self, htmlPage):
        self.url = htmlPage
        fetcher = HtmlFetcher(self.url)
        self.html = fetcher.GetHtml()
        self.config = None

    
    def GetConfig(self):
        url = self.GetRerunUrl()
        self.config = urlparse.parse_qs(urlparse.urlparse(url).query)
        return '-'.join( [self.config['platform'][0],
                          self.config['configuration'][0],
                          self.config['release'][0],
                          'speed' if self.config['speed'][0] == 'yes' else 'debug',
                          self.config['toolchain'][0],
                          self.config['tree'][0] ],                              
                       )


    def GetRerunUrl(self):
        ptn = '(?s)tinderbox: reschedule: (.*?)\n'
        found = re.search(ptn, self.html)
        if found is not None:
            url = HTMLParser.HTMLParser().unescape(found.groups()[0])
            return url
        else:
            raise ConfigError('incorrect config at %s' % self.url)

            
    def GetTestResult(self):
        content = self.__GetBuildLogText()
        content = self.__CleanupTestResult(content)
        try:
            return ParseTestResult('\n'.join([x.strip() for x in content.split('\n')]))
        except:
            return []

    
    def __CleanupTestResult(self, content):
        lines = []
        ptn = 'Couldn&acute;t login to linux at telnet:'
        for line in content.split('\n'):
            if line.find(ptn) == -1:
                lines.append(line) 
        return '\n'.join(lines)

    
    def __GetBuildLogText(self):
        ptn = '(?s)<H2>Build Log</H2>(.*?)No More Errors'
        ptnLine = '<.*>(.*?)\n'
        found = re.search(ptn, self.html)
        if found is not None:
            lines = found.groups()[0].split('\n')
            newLines = []
            for line in lines:
                index = line.rfind('>')
                newLines.append(line[index+1:])
            return '\n'.join(newLines)
        else:
            raise BuildLogError('incorrect build log at %s' % self.url)
        

def test_TinderMainPage():
    mainPage = TinderMainPage(kongV6SummaryPage)
    modUrlTimes = mainPage.GetModules()
    for module, url, timestamp in modUrlTimes:
        print module
        print url
        print timestamp
        print mainPage.IsBuildPassed(timestamp)
        break
            
    
def test_ModuleParser():
    modulePage = 'http://128.224.154.135/cgi-bin/tinderbox/gunzip.cgi?tree=IPMACSEC&full-log=1489347145.25240'
    modulePageMultiError = 'http://128.224.154.135/cgi-bin/tinderbox/gunzip.cgi?tree=IPIKE-IPEAP&full-log=1489516695.19986'
    modulePageWithCouldNot = 'http://128.224.154.135/cgi-bin/tinderbox/gunzip.cgi?tree=IPAPPL&full-log=1489427134.15305'
    modulePageWithoutTestResult = 'http://128.224.154.135/cgi-bin/tinderbox/gunzip.cgi?tree=IPDIAMETER-SecureKEYDB&full-log=1489512895.15711'
    
    modParser = ModuleParser(modulePageMultiError)
    print modParser.GetTestResult()
    print modParser.GetConfig()


def main():
    mainPage = TinderMainPage(kongV6SummaryPage)
    modUrlTimes = mainPage.GetModules()
    
    totalTestResults = []
    moduleBuildFailed = []
    for module, url, timestamp in modUrlTimes:
        modParser = ModuleParser(url)
        print '=== %s ===' % module
        testResults = modParser.GetTestResult()
        print 'ok:%s, failed:%s, skipped:%s' % CategorizeTestCaseResult(testResults)    
        totalTestResults += testResults    
        for x in testResults:
            print '\t', x
        print
        
        if not mainPage.IsBuildPassed(timestamp):
            moduleBuildFailed.append(module)
            
        del modParser
        
    print 'total: %s modules' % len(modUrlTimes)
    print 'total ok:%s, failed:%s, skipped:%s' % CategorizeTestCaseResult(totalTestResults)
    
    if len(moduleBuildFailed) > 0:
        print '\nBuild failed modules:'
        for x in moduleBuildFailed:
            print '\t%s' % x
        print 'total build failed modules:%s' % len(moduleBuildFailed)
        
if __name__ == '__main__':
    main()
    #test_ModuleParser()
    #test_TinderMainPage()
        
