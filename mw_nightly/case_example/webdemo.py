#! /usr/bin/python2.7

# -*- coding: utf-8 -*-
# python2.7 /buildarea2/mw/wassp-repos/testcases/vxworks7/mw/web/web_WEBDemoByHTTP/webdemo.py 128.224.166.109 http 128.224.167.129

from selenium import webdriver
import unittest
import os,sys
import time
import urllib2
import re

class WindMarkCase(unittest.TestCase):
    homepage = "Tutorial Index"
    homeConfirm = "Functionlity"
    targetIP = sys.argv[1]
    httpStr = sys.argv[2]
    hostIP = sys.argv[3]
    baseurl = httpStr + "://" + targetIP

    def setUp(self):
        self.verificationErrors = []

    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

    def testCgiEnv(self):
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/cgi.html"
        print test_url
        sel.get(test_url)
        time.sleep(10)

        self.assertTrue(sel.find_element_by_partial_link_text(self.homepage))

        sel.find_element_by_partial_link_text(self.homepage).click()
        time.sleep(10)

        sel.get(test_url)
        time.sleep(10)

        sel.find_element_by_partial_link_text("/cgi/printenv.cgi").click()
        time.sleep(10)

        self.assertTrue(sel.find_element_by_xpath("//LI[contains(text(),'SERVER_PROTOCOL')]"))
        self.assertTrue(sel.find_element_by_partial_link_text(self.homepage))

        sel.find_element_by_partial_link_text(self.homepage).click()
        time.sleep(10)

        sel.quit()

    def testV7man334(self):
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/index.html?^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^\
                                   @M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^@M^\
                                   @M^@M^@M^@M^@M^@M!@rt=ascending"
        print test_url
        sel.get(test_url)
        time.sleep(10)

        self.assertTrue(sel.find_element_by_xpath("//p[contains(text(),'Wind River Web Server Tutorial Index')]"))

        time.sleep(10)

        sel.quit()

    def testNewCgi(self):
        arg = "test=Cgi"
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/newcgi/cgitest.cgi?" + arg
        sel.get(test_url)
        time.sleep(10)
        self.assertTrue(find_element_by_link_text("The QUERY_STRING is " + arg))

        sel.open("/fs/newcgi.html")
        time.sleep("10")
        self.assertTrue(sel.find_element_by_partial_link_text(self.homepage))

        sel.type("xpath=//input[@name='sname']", "TestName")
        sel.type("xpath=//input[@name='age']", "28")

        sel.click("xpath=//input[@type='submit']")
        time.sleep(10)

        self.assertTrue(sel.find_element_by_link_text("The studentname is TestName, age is 28"))
        sel.quit()
        
    def testCgiWindMarkParameter(self):
        arg1 = "%24Attach%24=file.txt&%24To%24=swoopme@hotmail.com"
        arg2 = "test%20invalid"
        arg3 = "test%20Cgi"

        sel = webdriver.Firefox()

        test_url = self.baseurl + "/cgi/printenv.cgi?" + arg2
        sel.get(test_url)
        time.sleep(10)
        test_query="QUERY_STRING=" + arg2
        self.assertTrue(sel.find_element_by_xpath("//LI[contains(text(),test_query)]"))
        sel.quit()
        
        driver=webdriver.Firefox()
        sel = driver
        test_url = self.baseurl + "/cgi/printenv.cgi?" + arg3
        test_query = "QUERY_STRING=" + arg3
        sel.get(test_url)
        time.sleep(10)
        self.assertTrue(sel.find_element_by_xpath("//LI[contains(text(),test_query)]"))

        self.assertTrue(sel.find_element_by_partial_link_text(self.homepage))

        sel.find_element_by_partial_link_text(self.homepage).click()
        time.sleep(10)
        sel.quit()

    def testStructScalar(self):
        stringScalarField = "Wind River"
        integerScalarField = "1234"
        
        sel = webdriver.Firefox()
        sel.open("/fs/struct_scalar.html")
        sel.wait_for_page_to_load("30000")

        self.assertTrue(sel.is_text_present(self.homepage))

        sel.type("xpath=//input[@name='stringScalarField']", stringScalarField)
        sel.type("xpath=//input[@name='integerScalarField']", integerScalarField)

        sel.click("xpath=//input[@type='submit']")
        sel.wait_for_page_to_load("30000")

        val1 = sel.get_value("xpath=//input[@name='stringScalarField']")
        val2 = sel.get_value("xpath=//input[@name='integerScalarField']")
        
        ret1 = 0
        ret2 = 0
        
        if val1 == stringScalarField:
            ret1 = 1
        if val2 == integerScalarField:
            ret2 = 1
            
        self.assertTrue(ret1)
        self.assertTrue(ret2)

    def testlogfile(self):
        logfile = '/folk/target/htdocs/logfile.txt'
        self.assertTrue(os.path.isfile(logfile))
        f = open(logfile,'r')
        allLines = f.readlines()
        f.close()
        endLine = allLines[-1]
        self.assertTrue('GMT: from' in endLine)

    def testnetwork(self):
        sel = webdriver.Firefox()
        sel.open("/network/network.html")
        sel.wait_for_page_to_load("10000")
        
        sel.click("link=" + "Testing the function of logfile")
        sel.wait_for_page_to_load("10000")
        self.assertTrue(sel.is_text_present("GMT: from"))

    def testCustomRpm(self):
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/cust_rpm.html"
        sel.get(test_url)
        time.sleep(10)
        test_url = "/user_rpm/test.html"
        self.assertTrue(sel.find_element_by_partial_link_text(test_url))
       
        sel.find_element_by_partial_link_text(test_url).click()
        time.sleep(10)
        test_query = "This page has been accessed"
        self.assertTrue(sel.find_element_by_xpath("//p[contains(text(),test_query)]"))
        
        test_url = self.baseurl + "/fs/cust_rpm.html"
        sel.get(test_url)
        time.sleep(10)
        test_url = "/user_rpm/test.txt"
        self.assertTrue(sel.find_element_by_partial_link_text(test_url))
        sel.find_element_by_partial_link_text(test_url).click()
        time.sleep(10)
        test_url = self.baseurl + "/user_rpm/test.txt"
        content = urllib2.urlopen(test_url).read()
        
        self.assertTrue(re.compile("This page has been accessed").search(content))

        test_url = self.baseurl + "/fs/cust_rpm.html"
        sel.get(test_url)
        time.sleep(10)
        test_url = "/user_rpm/"
        self.assertTrue(sel.find_element_by_partial_link_text(test_url))
        sel.find_element_by_partial_link_text(test_url).click()
        time.sleep(10)
        test_query = "This page has been accessed"
        self.assertTrue(sel.find_element_by_xpath("//p[contains(text(),test_query)]"))
        sel.quit()


    def testSecurity(self):
        sel = webdriver.Firefox()
        url1 = "http://allowed:allowed@" + self.targetIP + "/secure/index.html"
        url2 = "http://allowed:allowed@" + self.targetIP + "/secure/debug_showauth/"
        url3 = "http://allowed:allowed@" + self.targetIP + "/secure/auth_test.html"
        url4 = "http://user:<<>>@" + self.targetIP + "/special/index.html"
        url5 = "http://host:host@" + self.targetIP + "/host/index.html"
        url6 = "http://allowed:allowed@" + self.targetIP + "/getAuthMIME/"

        sel.get(url1)
        time.sleep(5)
        self.assertTrue(sel.find_element_by_xpath("//p[contains(text(),'Wind River Web Server Tutorial Index')]"))

        sel.get(url2)
        time.sleep(5)
        self.assertTrue(sel.find_element_by_xpath("//I[contains(text(),'Basic YWxsb3dlZDphbGxvd2Vk')]"))

        sel.get(url3)
        time.sleep(5)
        self.assertTrue(sel.find_element_by_xpath("//p[contains(text(),'Authentication and Access Control Test')]"))
        sel.quit()

    def testSMTP(self):
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/smtp.html"
        sel.get(test_url)
        time.sleep(5)
        sel.find_element_by_xpath("//input[@name='smtp_mailServer']").clear()
        sel.find_element_by_xpath("//input[@name='smtp_mailServer']").send_keys("147.11.1.11")
        sel.find_element_by_xpath("//input[@name='smtp_domain']").clear()
        sel.find_element_by_xpath("//input[@name='smtp_domain']").send_keys("wrs.com")
        sel.find_element_by_xpath("//input[@name='smtp_mailFrom']").clear()
        sel.find_element_by_xpath("//input[@name='smtp_mailFrom']").send_keys("noreply@windriver.com")
        sel.find_element_by_xpath("//input[@name='smtp_mailTo']").clear()
        sel.find_element_by_xpath("//input[@name='smtp_mailTo']").send_keys("chunyan.ye@windriver.com")
        sel.find_element_by_xpath("//input[@name='smtp_subjectHeading']").clear()
        sel.find_element_by_xpath("//input[@name='smtp_subjectHeading']").send_keys("WebSMTPtest")
        sel.find_element_by_xpath("//input[@type='checkbox']").click()
        sel.find_element_by_xpath("//input[@type='submit']").click()
        time.sleep(5)
        self.assertTrue(sel.find_element_by_xpath("//p[contains(text(),'E-mail Alert Send Succeeded')]"))
        sel.quit()

    def testJavaAuthWithoutHash(self):
        sel = webdriver.Firefox()
        sel.open("/fs/jsAuth.html")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("Password Hash"))
        self.assertTrue(sel.is_text_present("Tutorial Index"))
        sel.select("xpath=//select[@name='xwithHash']","value=0")
        sel.click("xpath=//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("0 :NoHash"))
        self.testJavaAuthCase()
        
    def testJavaAuthWithHash(self):
        sel = webdriver.Firefox()
        sel.open("/fs/jsAuth.html")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("Password Hash"))
        self.assertTrue(sel.is_text_present("Tutorial Index"))
        sel.select("xpath=//select[@name='xwithHash']","value=1")
        sel.click("xpath=//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("1 :WithHash"))
        self.testJavaAuthCase()

    def testJavaAuthCase(self):
        sel = webdriver.Firefox()
        
        #L5 Test
        sel.open("/fs/jsAuthTestL5.html")
        sel.wait_for_page_to_load("30000")
        if sel.is_text_present("User Name:"):
            sel.type("xpath=//input[@name='username']", "test")
            sel.type("xpath=//input[@name='password']", "test")
            sel.click("xpath=//input[@type='submit']")
            sel.wait_for_page_to_load("30000")
            self.assertTrue(sel.is_text_present("User Name:"))

        sel.type("xpath=//input[@name='username']", "wrs")
        sel.type("xpath=//input[@name='password']", "wrs")
        sel.click("xpath=//input[@type='submit']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("JavaScript Authentication Test"))

        sel.open("/fs/jsAuthTestL5.html")
        sel.wait_for_page_to_load("30000")
        if sel.is_text_present("User Name:"):
            sel.type("xpath=//input[@name='username']", "admin")
            sel.type("xpath=//input[@name='password']", "admin")
            sel.click("xpath=//input[@type='submit']")
            sel.wait_for_page_to_load("30000")
            self.assertTrue(sel.is_text_present("JavaScript Authentication Test"))

        #L8 Test
        sel.open("/fs/jsAuthTest.html")
        sel.wait_for_page_to_load("30000")

        if sel.is_text_present("User Name:"):
        
            sel.type("xpath=//input[@name='username']", "test")
            sel.type("xpath=//input[@name='password']", "test")
            sel.click("xpath=//input[@type='submit']")
            sel.wait_for_page_to_load("30000")
            self.assertTrue(sel.is_text_present("User Name:"))

            sel.type("xpath=//input[@name='username']", "wrs")
            sel.type("xpath=//input[@name='password']", "wrs")
            sel.click("xpath=//input[@type='submit']")
            sel.wait_for_page_to_load("30000")
            self.assertTrue(sel.is_text_present("User Name:"))

            sel.type("xpath=//input[@name='username']", "admin")
            sel.type("xpath=//input[@name='password']", "admin")
            sel.click("xpath=//input[@type='submit']")
            sel.wait_for_page_to_load("30000")
            self.assertTrue(sel.is_text_present("JavaScript Authentication Test"))

    def testJavaAuthDemoCase(self):
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/jsAuthTest.html"
        sel.get(test_url)
        time.sleep(10)

        if sel.find_element_by_name("username"):
            
            sel.find_element_by_name("username").clear()
            sel.find_element_by_name("username").send_keys("admin")
            sel.find_element_by_name("password").clear()
            sel.find_element_by_name("password").send_keys("admin")
            sel.find_element_by_xpath("//input[@value='Log On']").click()
            time.sleep(5)

            self.assertTrue(sel.find_element_by_xpath("//p[contains(text(),'JavaScript Authentication Test')]"))
        sel.quit()

    def testDisplayErrors(self):

        sel = webdriver.Firefox()
        
        test_url = self.baseurl + "/fs/errors.html"
        sel.get(test_url)
        time.sleep(10)

        self.assertTrue(sel.find_element_by_partial_link_text(self.homepage))

        sel.find_element_by_xpath("//input[@name='err_noReadNoWrite']").clear()
        sel.find_element_by_xpath("//input[@name='err_noReadNoWrite']").send_keys("test")
        sel.find_element_by_xpath("//input[@type='submit']").click()
        
        time.sleep(5)
        sel.find_element_by_xpath("//FONT[contains(text(),'set attempt failed.')]")
        sel.quit()

    def testCreateAlias(self):
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/alias.html"
        sel.get(test_url)
        time.sleep(5)
        self.assertTrue(sel.find_element_by_partial_link_text(self.homepage))
        
        sel.find_element_by_partial_link_text("/xyz").click()
        time.sleep(5)
        self.assertTrue(sel.find_element_by_xpath("//p[contains(text(),'Wind River Web Server Tutorial Index')]"))
        sel.quit()

    def testCreateAlias_bak(self):
        sel = webdriver.Firefox()
        sel.open("/")
        sel.wait_for_page_to_load("10000")
        self.assertTrue(sel.is_text_present(self.homepage))

    def testDynamicPage(self):
        postDescr = "Embedded Target_1"
        postName = "Wind River Tutorial System_1"
        postContact = "Wind River Support_1"

        getDescr = "Embedded Target_2=%"
        getName = "=Wind River Tutorial_2=="
        getContact = "Wind River Support_2=="

        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/dyn_web_pages.html"
        sel.get(test_url)
        time.sleep(5)
        self.assertTrue(sel.find_element_by_partial_link_text(self.homepage))

        orgDescr = sel.find_element_by_xpath("//input[@name='xsysDescr']").get_attribute("value")
        orgName = sel.find_element_by_xpath("//input[@name='xsysName']").get_attribute("value")
        orgContact = sel.find_element_by_xpath("//input[@name='xsysContact']").get_attribute("value")

        sel.find_element_by_xpath("//input[@name='xsysDescr']").clear()
        sel.find_element_by_xpath("//input[@name='xsysDescr']").send_keys(postDescr)
        sel.find_element_by_xpath("//input[@name='xsysName']").clear()
        sel.find_element_by_xpath("//input[@name='xsysName']").send_keys(postName)
        sel.find_element_by_xpath("//input[@name='xsysContact']").clear()
        sel.find_element_by_xpath("//input[@name='xsysContact']").send_keys(postContact)

        sel.find_element_by_xpath("//input[@type='submit']").click()
        time.sleep(5)

        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%postDescr))
        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%postName))
        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%postContact))

        sel.find_element_by_xpath("//input[@name='xsysDescr']").clear()
        sel.find_element_by_xpath("//input[@name='xsysDescr']").send_keys(orgDescr)
        sel.find_element_by_xpath("//input[@name='xsysName']").clear()
        sel.find_element_by_xpath("//input[@name='xsysName']").send_keys(orgName)
        sel.find_element_by_xpath("//input[@name='xsysContact']").clear()
        sel.find_element_by_xpath("//input[@name='xsysContact']").send_keys(orgContact)
        
        sel.find_element_by_xpath("//input[@type='submit']").click()
        time.sleep(5)

        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%orgDescr))
        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%orgName))
        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%orgContact))

        self.assertTrue(sel.find_element_by_partial_link_text(self.homepage))
        sel.quit()

    def testSnmpObject(self):
        postLocation = "350 Terry Fox Rd. 200 Ottawa 1";
        postName = "vxTarget1";
        postContact = "Wind River System1";
        sel = webdriver.Firefox()

        test_url = self.baseurl + "/fs/snmp_objects.html"
        time.sleep(5)
        sel.get(test_url)
        self.assertTrue(sel.find_element_by_partial_link_text(self.homepage))

        orgLocation = sel.find_element_by_xpath("//input[@name='sysLocation']").get_attribute("value")
        orgName = sel.find_element_by_xpath("//input[@name='sysName']").get_attribute("value")
        orgContact = sel.find_element_by_xpath("//input[@name='sysContact']").get_attribute("value")
        
        sel.find_element_by_xpath("//input[@name='sysLocation']").clear()
        sel.find_element_by_xpath("//input[@name='sysLocation']").send_keys(postLocation)
        sel.find_element_by_xpath("//input[@name='sysName']").clear()
        sel.find_element_by_xpath("//input[@name='sysName']").send_keys(postName)
        sel.find_element_by_xpath("//input[@name='sysContact']").clear()
        sel.find_element_by_xpath("//input[@name='sysContact']").send_keys(postContact)

        sel.find_element_by_xpath("//input[@type='submit']").click()
        time.sleep(5)

        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%postLocation))
        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%postName))
        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%postContact))

        sel.find_element_by_xpath("//input[@name='sysLocation']").clear()
        sel.find_element_by_xpath("//input[@name='sysLocation']").send_keys(orgLocation)
        sel.find_element_by_xpath("//input[@name='sysName']").clear()
        sel.find_element_by_xpath("//input[@name='sysName']").send_keys(orgName)
        sel.find_element_by_xpath("//input[@name='sysContact']").clear()
        sel.find_element_by_xpath("//input[@name='sysContact']").send_keys(orgContact)

        sel.find_element_by_xpath("//input[@type='submit']").click()
        time.sleep(5)

        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%orgLocation))
        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%orgName))
        self.assertTrue(sel.find_element_by_xpath("//input[@value='%s']"%orgContact))

        sel.find_element_by_partial_link_text(self.homepage).click()
        self.assertTrue(sel.find_element_by_xpath("//p[contains(text(),'Wind River Web Server Tutorial Index')]"))
        sel.quit()

    def testMacroPage(self):
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/macros.html"
        sel.get(test_url)
        time.sleep(5)

        self.assertTrue(sel.find_element_by_xpath("//th[contains(text(),'ifIndex')]"))
        self.assertTrue(sel.find_element_by_xpath("//td[contains(text(),'lo0')]"))
        self.assertTrue(sel.find_element_by_xpath("//option[contains(text(),'1: Up')]"))
        
        sel.find_element_by_xpath("//select[@name='ifAdminStatus.1']").send_keys("2: Down")
        sel.find_element_by_xpath("//input[@type='submit']").click()
        time.sleep(5)

        self.assertTrue(sel.find_element_by_xpath("//th[contains(text(),'ifIndex')]"))
        self.assertTrue(sel.find_element_by_xpath("//td[contains(text(),'lo0')]"))
        self.assertTrue(sel.find_element_by_xpath("//option[contains(text(),'2: Down')]"))
        sel.quit()

    def testInvalidParameter(self):
        arg = "test invalid"
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/index.html?" + arg
        sel.get(test_url)
        time.sleep(5)
        self.assertTrue(sel.find_element_by_xpath("//a[contains(text(),self.homeConfirm)]"))
        sel.quit()

    def testUploadFile(self):
        sel = webdriver.Firefox()
        test_url = self.baseurl + "/fs/upload.html"
        sel.get(test_url)
        time.sleep(5)

        sel.find_element_by_xpath("//input[@type='file']").send_keys("/buildarea2/mw/webUploadFile.txt")
        sel.find_element_by_xpath("//input[@type='submit']").click()
        time.sleep(5)
        self.assertTrue(sel.find_element_by_xpath("//span[contains(text(),'File Uploaded!')]"))
        sel.quit()

    def testCheckbox(self):
        sel = webdriver.Firefox()
        flag = 0
        while(1):
            test_url = self.baseurl + "/fs/checkbox.html"
            sel.get(test_url)
            time.sleep(5)
            if (sel.find_element_by_xpath("//span[contains(text(),'CHECKED')]").text == "CHECKED"):
                sel.find_element_by_xpath("//input[@type='checkbox']").click()
                sel.find_element_by_xpath("//input[@type='submit']").click()
                time.sleep(5)
                self.assertTrue(sel.find_element_by_xpath("//span[contains(text(),'UNCHECKED')]"))
                flag = flag + 1
                if flag == 2:
                    break
                continue
            if (sel.find_element_by_xpath("//span[contains(text(),'CHECKED')]").text == "UNCHECKED"):
                sel.find_element_by_xpath("//input[@type='checkbox']").click()
                sel.find_element_by_xpath("//input[@type='submit']").click()
                time.sleep(5)
                self.assertTrue(sel.find_element_by_xpath("//input[@CHECKED]"))
                flag = flag + 1
                if flag == 2:
                    break
                continue

        sel.quit()

    def testDynamicTable(self):
        sel = webdriver.Firefox()
        sel.open("/fs/dynamicTable.html")
        sel.wait_for_page_to_load("30000")

        #Example 1
        sel.type("xpath=//input[@name='first_i']", "3")
        sel.click("xpath=//input[@value='Update1']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(not sel.is_text_present("offset_i(2)"))

        sel.type("xpath=//input[@name='first_i']", "0")
        sel.click("xpath=//input[@value='Update1']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("offset_i(0)"))

        #Example 2
        sel.type("xpath=//input[@name='first_p']", "0x0")
        sel.click("xpath=//input[@value='Update2']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(not sel.is_text_present("pointer_p(0x"))

        sel.type("xpath=//input[@name='first_p']", "")
        sel.click("xpath=//input[@value='Update2']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("pointer_p(0x"))

        #Example 3
        sel.type("xpath=//input[@name='first_pi']", "3")
        sel.click("xpath=//input[@value='Update3']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(not sel.is_text_present("pointer_pi(2)"))

        sel.type("xpath=//input[@name='first_pi']", "")
        sel.click("xpath=//input[@value='Update3']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("pointer_pi(0)"))

        #Example 4
        sel.type("xpath=//input[@name='first_s']", "fitzgerald")
        sel.click("xpath=//input[@value='Update4_1']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(not sel.is_text_present("charles"))

        sel.type("xpath=//input[@name='first_s']", "")
        sel.click("xpath=//input[@value='Update4_1']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("bennett"))

        #Example 4 add name & Example 5
        sel.type("xpath=//input[@name='nameToAdd']", "Weina Zhang")
        sel.type("xpath=//input[@name='nameToDelete']", "Nat King Cole")
        sel.click("xpath=//input[@value='Update4_2']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("zhang,weina"))
        self.assertTrue(sel.is_text_present("W,e,i,n, a, ,Z,h, a,n"))
        self.assertTrue(not sel.is_text_present("kingcole,nat"))

        #Example 4 change name & Example 5
        sel.type("xpath=//input[@name='nameToModify']", "Weina Zhang")
        sel.type("xpath=//input[@name='changeNameTo']", "Nat King Cole")
        sel.click("xpath=//input[@value='Update4_3']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(not sel.is_text_present("zhang,weina"))
        self.assertTrue(sel.is_text_present("kingcole,nat"))
        self.assertTrue(sel.is_text_present("NAT KING COLE"))
        
        #Example 6
        sel.type("xpath=//input[@name='myIpAddress(0)']", "128")
        sel.type("xpath=//input[@name='myIpAddress(1)']", "224")
        sel.type("xpath=//input[@name='myIpAddress(2)']", "153")
        sel.type("xpath=//input[@name='myIpAddress(3)']", "136")

        sel.click("xpath=//input[@value='Update6']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("128.224.153.136"))

        sel.type("xpath=//input[@name='myIpAddress(0)']", "a")
        sel.type("xpath=//input[@name='myIpAddress(1)']", "b")
        sel.type("xpath=//input[@name='myIpAddress(2)']", "c")
        sel.type("xpath=//input[@name='myIpAddress(3)']", "d")

        sel.type("xpath=//input[@name='a']", "1")
        sel.type("xpath=//input[@name='b']", "2")
        sel.type("xpath=//input[@name='c']", "3")
        sel.type("xpath=//input[@name='d']", "4")

        sel.click("xpath=//input[@value='Update6']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("1.2.3.4"))

        sel.type("xpath=//input[@name='myIpAddress(0)']", "e")
        sel.type("xpath=//input[@name='myIpAddress(1)']", "f")
        sel.type("xpath=//input[@name='myIpAddress(2)']", "g")
        sel.type("xpath=//input[@name='myIpAddress(3)']", "h")

        sel.click("xpath=//input[@value='Update6']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("The following WMB access errors were encountered"))

        sel.open("/fs/dynamicTable.html")
        sel.wait_for_page_to_load("30000")

        sel.type("xpath=//input[@name='myIpAddress(0)']", "a")
        sel.type("xpath=//input[@name='myIpAddress(1)']", "b")
        sel.type("xpath=//input[@name='myIpAddress(2)']", "c")
        sel.type("xpath=//input[@name='myIpAddress(3)']", "d")

        sel.click("xpath=//input[@value='Update6']")
        sel.wait_for_page_to_load("30000")
        self.assertTrue(sel.is_text_present("'1.2.3.4"))

    def testFileSequence(self):
        sel = webdriver.Firefox()
        regFs = "Testing the priority between file registry and ANSI_FS"
        ansiFs = "Testing the priority between ANSI_FS and MEM_FS"
        memFs = "Testing whether file could be accessed in MEM_FS only"
        compressFs = "Testing the file registry type of compressed ANSI"
        
        sel.open("/fs/fsSearchOrder.html")
        sel.wait_for_page_to_load("30000")
        sel.click("link=" + regFs)
        sel.wait_for_page_to_load("10000")
        self.assertTrue(sel.is_text_present("PASS"))

        sel.open("/fs/fsSearchOrder.html")
        sel.wait_for_page_to_load("30000")
        sel.click("link=" + ansiFs)
        sel.wait_for_page_to_load("10000")
        self.assertTrue(sel.is_text_present("PASS"))

        sel.open("/fs/fsSearchOrder.html")
        sel.wait_for_page_to_load("30000")
        sel.click("link=" + memFs)
        sel.wait_for_page_to_load("10000")
        self.assertTrue(sel.is_text_present("PASS"))

        sel.open("/fs/fsSearchOrder.html")
        sel.wait_for_page_to_load("30000")
        sel.click("link=" + compressFs)
        sel.wait_for_page_to_load("10000")
        self.assertTrue(sel.is_text_present("PASS"))
        
if __name__ == "__main__":
    suite = unittest.TestSuite() 

    suite.addTest(WindMarkCase("testCgiEnv"))
    suite.addTest(WindMarkCase("testCgiWindMarkParameter"))
    suite.addTest(WindMarkCase("testlogfile"))
    suite.addTest(WindMarkCase("testCustomRpm"))
    suite.addTest(WindMarkCase("testJavaAuthDemoCase"))
    suite.addTest(WindMarkCase("testDisplayErrors"))
    suite.addTest(WindMarkCase("testUploadFile"))
    suite.addTest(WindMarkCase("testCheckbox"))
    suite.addTest(WindMarkCase("testSMTP"))
    suite.addTest(WindMarkCase("testCreateAlias"))
    suite.addTest(WindMarkCase("testDynamicPage"))
    suite.addTest(WindMarkCase("testSnmpObject"))
    suite.addTest(WindMarkCase("testMacroPage"))
    suite.addTest(WindMarkCase("testInvalidParameter"))
    suite.addTest(WindMarkCase("testSecurity"))
    suite.addTest(WindMarkCase("testV7man334"))

    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    
    totalNum = (result.testsRun)
    failNum = len(result.errors) + len(result.failures)
    passNum = totalNum - failNum

    print(sys.argv[2] + "://" + sys.argv[1] + '\n')
    #print("MRES: TESTS=%d PASSES=%d FAILS=%d ABORTS=0 SKIPS=0" % (totalNum, passNum, failNum))
    print('TOTAL=%s PASS=%s FAIL=%s' % (totalNum, passNum, failNum))
    print('web test done\n')
    if totalNum == passNum and not failNum:
        sys.exit(0)
    else:
        sys.exit(1)
