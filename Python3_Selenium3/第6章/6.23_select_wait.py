# coding=utf-8
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

driver = webdriver.Chrome()
driver.maximize_window()
prj_path = os.path.split(os.path.realpath(__file__))[0].split('第6章')[0]
html_path = os.path.join(prj_path, "第6章", "single_selection_drop_list.html")
print(html_path)
driver.get(html_path)
# 找到下拉框,这是第一步
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@name='fruit']")))
se = driver.find_element_by_xpath("//[@name='fruit']")
# 返回下拉框所有的选项
ops = Select(se).options
for i in ops:
    print(i.text)
# 根据select_by_value获取下拉框选项
Select(se).select_by_value('xigua')
time.sleep(3)
# 根据select_by_index获取下拉框选项
Select(se).select_by_index(2)
time.sleep(3)
# 根据select_by_visible_text获取下拉框选项
Select(se).select_by_visible_text('猕猴桃')
time.sleep(3)
# all_selected_options   返回下拉框中已经选中的选项
already_selected = Select(se).all_selected_options
for i in already_selected:
    print(f'already selected {i.text}')
# 效果同上，也是返回已经选中的选项
first_selected = Select(se).first_selected_option
print(f'first selected {first_selected.text}')
driver.quit()
