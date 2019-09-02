<<<<<<< HEAD
#!/usr/bin/env python
import codecs


def getWebInfo(path):
    webinfo = {}
    config = open(path)
    for line in config:
        result = [ele.strip() for ele in line.split('=')]
        print(result)
        webinfo.update(dict([result]))
    return webinfo
	

def getUserInfo(path):
    user_info = []
    config = codecs.open(path,'r', 'utf-8')
    for line in config:
        user_dict = {}
        result = [ele.strip() for ele in line.split(' ')]
        for r in result:
            account = [ele.strip() for ele in r.split('=')]
            user_dict.update(dict([account]))
    user_info.append(user_dict)
    return user_info


if __name__ == '__main__':
    webinfo = getWebInfo(r'F:\Pycharm\Selenium_Xiaozhan\lxz_python\webinfo.txt')
    for key in webinfo:
        print(key,webinfo[key])
    user_info = getUserInfo(r'F:\Pycharm\Selenium_Xiaozhan\lxz_python\userinfo.txt')
    for l in user_info:
        print(l)
=======
#coding:utf-8
import codecs
import xlrd
def get_webinfo(path):
	web_info = {}
	#config = open(path)
	config = codecs.open(path, 'r', 'utf-8')
	
	for line in config:
		result = [ele.strip() for ele in line.split('=')]
		web_info.update(dict([result]))
	return web_info

def get_userinfo(path):
	user_info = []
	#config = open(path)
	config = codecs.open(path, 'r', 'utf-8')
	for line in config:
		user_dict = {}
		result = [ele.strip() for ele in line.split(';')]
		for r in result:
			account = [ele.strip() for ele in r.split('=')]
			print (account)
			user_dict.update(dict([account]))
		user_info.append(user_dict)
	return user_info

class XlUserinfo(object):
	def __init__(self, path = ''):
		self.xl = xlrd.open_workbook(path)

	def floattostr(self, val):
		if isinstance(val, float):
			val = str(int(val))
		return val

	def get_sheet_info(self):
		listkey = ['uname', 'pwd']
		infolist = []
		for row in range(1, self.sheet.nrows):
			info = [ self.floattostr(val) for val in self.sheet.row_values(row)]
			tmp = zip(listkey, info)
			infolist.append(dict(tmp))
		return infolist

	def get_sheetinfo_by_name(self,name):
		self.sheet = self.xl.sheet_by_name(name)
		return self.get_sheet_info()

	def get_sheetinfo_by_index(self, index):
		self.sheet = self.xl.sheet_by_index(index)
		return self.get_sheet_info()

if __name__ == '__main__':

	#webinfo = get_webinfo(r'C:\Users\hyg\Desktop\test\webinfo.txt')
	#for key in webinfo:
	#	print (key, webinfo[key])
	#userinfo = get_userinfo(r'C:\Users\hyg\Desktop\test\userinfo.txt')
	#print (userinfo)
	xinfo = XlUserinfo(r'C:\Users\hyg\Desktop\test\userinfo.xls')
	info = xinfo.get_sheetinfo_by_index(0)
	print (info)
	info = xinfo.get_sheetinfo_by_name('Sheet1')
	print (info)

	

	
>>>>>>> 4fc948b851e507ed66ee191ea35dba9b8cee742b
