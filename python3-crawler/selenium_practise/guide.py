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