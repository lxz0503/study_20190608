#coding:utf-8
import time
import xlsxwriter

class Loginfo(object):
	def __init__(self, path = '', mode = 'w'):
		fname = path + time.strftime('%Y-%m-%d', time.gmtime())
		self.log = open(path + fname + '.txt', mode)

	def log_init(self, sheetname, *title):
		pass

	def log_write(self, msg):
		self.log.write(msg)

	def log_close(self):
		self.log.close()

class Xlloginfo(object):
	def __init__(self, path=''):
		fname = path + time.strftime('%Y-%m-%d', time.gmtime())
		self.row = 0
		self.xl = xlsxwriter.Workbook(path+fname+'.xls')
		self.style = self.xl.add_format({'bg_color': 'red'})

	def xl_write(self, *args):
		col = 0
		style = ''
		if 'Error' in args:
			style = self.style
		for val in args:
			self.sheet.write_string(self.row, col, val, style)
			col += 1
		self.row += 1

	def log_init(self, sheet_name, *title):
		self.sheet = self.xl.add_worksheet(sheet_name)
		self.sheet.set_column('A:E', 30)
		self.xl_write(*title)

	def log_write(self, *args):
		self.xl_write(*args)

	def log_close(self):
		self.xl.close()


if __name__ == '__main__':
	'''
	log = Loginfo()
	log.log_write('test Loginfo 测试')
	log.log_close()
	'''
	xinfo = Xlloginfo()
	xinfo.log_init('test', 'name', 'pwd', 'result', 'info')
	xinfo.log_write('123', '123', 'Error', 'error')
	xinfo.log_close()
