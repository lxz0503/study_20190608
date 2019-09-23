# coding=utf-8

# 如何定位元素。参考截图locate_css.png
# 先点击截图里面的箭头，然后再把鼠标移动到想要定位的元素，例如输入框，按钮等，
# 此时上面会自动显示元素的css位置
# 左键点击一下，就会定位到相应的元素上
# 此时再把鼠标放到下面的元素上，右键选择Copy selector

# #q   这是淘宝页面的搜索框
#   这是那个搜索按钮css_selector   #J_TSearchForm > div.search-button > button
# 每个页面元素的ID是唯一的，所以，第一步通常是根据ID来定位，然后再空格，右尖括号，再去下面的子元素div里面的class（class名字是search-button）查找
# 然后locate下面的子元素button


# Expected Conditions
#
# There are some common conditions that are frequently of use when automating web browsers. Listed below are the names of each. Selenium Python binding provides some convenience methods so you don’t have to code an expected_condition class yourself or create your own utility package for them.
#
# title_is
# title_contains
# presence_of_element_located
# visibility_of_element_located
# visibility_of
# presence_of_all_elements_located
# text_to_be_present_in_element
# text_to_be_present_in_element_value
# frame_to_be_available_and_switch_to_it
# invisibility_of_element_located
# element_to_be_clickable
# staleness_of
# element_to_be_selected
# element_located_to_be_selected
# element_selection_state_to_be
# element_located_selection_state_to_be
# alert_is_present