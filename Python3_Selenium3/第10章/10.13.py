import xlwt
wb = xlwt.Workbook()
sheet = wb.add_sheet(u'≤‚ ‘')
sheet.write(0,0,"automation")
sheet.write(0,1,"selenium course")
wb.save('automate1.xls')
