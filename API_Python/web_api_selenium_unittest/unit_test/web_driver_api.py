from selenium import webdriver
import unittest
import time
import HTMLTestRunner


class WebTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.quit()

    def test_visitURL(self):
        url = "http://www.sogou.com"
        self.driver.get(url)
        title = self.driver.title
        print(title)
        assert self.driver.title.find(u"搜狗搜索") >= 0, "assert error"

    def test_visitRecentURL(self):
        first_url = "http://www.sogou.com"
        second_url = "https://www.baidu.com"   # this url should be https:// at office while http://at home
        self.driver.get(first_url)
        self.driver.get(second_url)
        self.driver.back()
        time.sleep(5)
        self.driver.forward()

    def test_refreshCurrentUrl(self):
        url = "http://www.sogou.com"
        self.driver.get(url)
        time.sleep(5)
        self.driver.refresh()

    def test_maximizeWindow(self):
        url = "http://www.sogou.com"
        self.driver.get(url)
        self.driver.maximize_window()
        time.sleep(5)
        self.driver.minimize_window()

    def test_operateWindowHandle(self):
        url = "https://www.baidu.com"
        self.driver.get(url)
        now_handle = self.driver.current_window_handle
        print(now_handle)
        self.driver.find_element_by_id("kw").send_keys("w3cschool")
        self.driver.find_element_by_id("su").click()
        time.sleep(3)
        self.driver.find_element_by_xpath('//h3[@class="t"]/a[@class="favurl"]').click()
        time.sleep(5)

    def test_getBasicInfo(self):
        url = "https://www.baidu.com"
        self.driver.get(url)
        ele = self.driver.find_element_by_xpath('//a[text()="新闻"]')
        print("the tag name is %s" % ele.tag_name)
        print("the size is %s" % ele.size)

    def test_getWebElementText(self):
        url = "https://www.baidu.com"
        self.driver.get(url)
        time.sleep(3)
        ele = self.driver.find_element_by_xpath('//*[@class="mnav"][2]')
        text = ele.text
        print(text)

    def test_getWebElementAttribute(self):
        url = "http://www.sogou.com"
        self.driver.get(url)
        search_box = self.driver.find_element_by_xpath('//input[@id="query"]')
        print("the name is %s" % search_box.get_attribute("name"))
        search_box.send_keys("python")
        time.sleep(5)
        search_box.clear()
        search_box.send_keys("python")
        print("the content to search is %s" % search_box.get_attribute("value"))
        search_button = self.driver.find_element_by_xpath('//input[@id="stb"]')
        search_button.click()
        time.sleep(5)
        self.driver.back()

    def test_clickButton(self):
        url = "file:///D:/xiaozhan_git/study_20190608/API_Python/web_api_selenium_unittest/unit_test/click.html"
        self.driver.get(url)
        button = self.driver.find_element_by_id('button')
        time.sleep(5)
        button.click()
        time.sleep(5)

    def test_doubleClick(self):
        url = "file:///D:/xiaozhan_git/study_20190608/API_Python/web_api_selenium_unittest/unit_test/double_click.html"
        self.driver.get(url)
        input_box = self.driver.find_element_by_id('inputBox')
        from selenium.webdriver import ActionChains
        action_chains = ActionChains(self.driver)
        time.sleep(5)
        action_chains.double_click(input_box).perform()
        time.sleep(5)

    def test_printSelectText(self):
        url = "file:///D:/xiaozhan_git/study_20190608/API_Python/web_api_selenium_unittest/unit_test/single_selection_drop_list.html"
        self.driver.get(url)
        select = self.driver.find_element_by_name('fruit')
        all_options = select.find_elements_by_tag_name('option')
        for option in all_options:
            print("the text is %s" % option.text)
            print("the selected value is %s" % option.get_attribute('value'))
            option.click()
            time.sleep(5)

    def test_operateDropList(self):
        url = "file:///D:/xiaozhan_git/study_20190608/API_Python/web_api_selenium_unittest/unit_test/single_selection_drop_list.html"
        self.driver.get(url)
        from selenium.webdriver.support.ui import Select
        select_element = Select(self.driver.find_element_by_xpath('//select'))
        print("the default selection is %s" % select_element.first_selected_option.text)
        time.sleep(5)
        all_options = select_element.options
        print("the length of options is %s" % len(all_options))
        select_element.select_by_value("shanzha")
        print("the selected element is %s" % select_element.all_selected_options[0].text)
        self.assertEqual(select_element.all_selected_options[0].text,u"山楂")
        time.sleep(5)

    def test_operateMultipleOptionDropList(self):
        url = "file:///D:/xiaozhan_git/study_20190608/API_Python/web_api_selenium_unittest/unit_test/multiple_drop_list.html"
        self.driver.get(url)
        from selenium.webdriver.support.ui import Select
        select_element = Select(self.driver.find_element_by_xpath('//select'))
        select_element.select_by_index(0)
        select_element.select_by_visible_text('山楂')
        select_element.select_by_value('mihoutao')
        for option in select_element.all_selected_options:
            print("the selected option is %s" % option.text)
        select_element.deselect_all()
        time.sleep(5)
        print("------再次选中3个-------")
        select_element.select_by_index(3)
        select_element.select_by_visible_text('西瓜')
        select_element.select_by_value('juzi')
        for option in select_element.all_selected_options:
            print("the selected option is %s" % option.text)
        time.sleep(5)
        select_element.deselect_by_visible_text('西瓜')
        select_element.deselect_by_index(3)
        select_element.deselect_by_value('juzi')

    def test_operateMultipleOptionDropList(self):
        url = "file:///D:/xiaozhan_git/study_20190608/API_Python/web_api_selenium_unittest/unit_test/data.html"
        self.driver.get(url)
        from selenium.webdriver.common.keys import Keys
        self.driver.find_element_by_id('select').clear()
        time.sleep(5)
        self.driver.find_element_by_id('select').send_keys('c', Keys.ARROW_DOWN)
        self.driver.find_element_by_id('select').send_keys(Keys.ARROW_DOWN)
        self.driver.find_element_by_id('select').send_keys(Keys.ENTER)
        time.sleep(5)

    def test_operateRadio(self):
        url = "file:///D:/xiaozhan_git/study_20190608/API_Python/web_api_selenium_unittest/unit_test/radio.html"
        self.driver.get(url)
        berryRadio = self.driver.find_element_by_xpath('//input[@value="berry"]')
        berryRadio.click()
        time.sleep(5)
        self.assertTrue(berryRadio.is_selected(), u"草莓单选框未被选中")
        if berryRadio.is_selected():
            watermelonRadio = self.driver.find_element_by_xpath('//input[@value="watermelon"]')
            watermelonRadio.click()
            time.sleep(5)
            self.assertFalse(berryRadio.is_selected())
        radioList = self.driver.find_elements_by_xpath('//input[@name="fruit"]')
        for radio in radioList:
            if radio.get_attribute('value') == 'orange':
                if not radio.is_selected():
                    radio.click()
                    time.sleep(5)
                    self.assertEqual(radio.get_attribute('value'),'orange')

    def test_operateCheckBox(self):
        url = "file:///D:/xiaozhan_git/study_20190608/API_Python/web_api_selenium_unittest/unit_test/check_box.html"
        self.driver.get(url)
        berry_check_box = self.driver.find_element_by_xpath('//input[@value="berry"]')
        berry_check_box.click()
        time.sleep(5)
        self.assertTrue(berry_check_box.is_selected(), u"草莓复选框未被选中")
        if berry_check_box.is_selected():
            berry_check_box.click()
            time.sleep(5)
            self.assertFalse(berry_check_box.is_selected())
        check_box_list = self.driver.find_elements_by_xpath('//input[@name="fruit"]')
        for box in check_box_list:
            if not box.is_selected():
                box.click()
                time.sleep(5)


if __name__ == '__main__':
    # unittest.main()                  # 必须注释掉这句话才能生成html报告,否则始终以unittest方式运行
    suite = unittest.TestSuite()
    # suite.addTest(WebTest('test_visitURL'))    # 运行单个case
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(WebTest))   # 运行整个测试套
    # file_name = "F:\\Pycharm\\Selenium_Xiaozhan\\report.html"
    file_name = "D:\\xiaozhan_git\\study_20190608\\API_Python\\web_api_selenium_unittest\\unit_test\\report.html"
    with open(file_name, 'wb+') as fp:
        runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='report', description='web api test')
        runner.run(suite)