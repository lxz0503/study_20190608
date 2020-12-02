#!/usr/bin/env python3
# coding: utf-8
import os
import xlrd
import xlwt
import xlutils
from itertools import compress

def get_backlist():
	list_case = []
	list_flag = []
	list_test_suite = []
	list_case_result = []
	list_case_combine = []

	backlist = '/folk/hyan1/Nightly/common/blacklist.xls'
	rb = xlrd.open_workbook(backlist,
			                formatting_info=True,
			                on_demand=True)
	ws = rb.sheet_by_index(0)
	cells_case_name = ws.col_slice(colx=0,
			          		 	start_rowx=0,
			          		 	end_rowx=500)
	cells_tset_suite = ws.col_slice(colx=1,
								start_rowx=0,
								end_rowx=500)

	cell_case_flag = ws.col_slice(colx=2,
								start_rowx=0,
								end_rowx=500)
	for cell in cells_case_name:
		list_case.append(cell.value)
	for cell in cells_tset_suite:
		list_test_suite.append(cell.value)
	for flag in cell_case_flag:
		list_flag.append(flag.value)
	list_flag_result = [ n == 1 for n in list_flag]
	list_case_combine = [(x, y) for x, y in zip(list_case, list_test_suite)]
	list_case_result = list(compress(list_case_combine, list_flag_result))
	#print(list_case_result)
	return list_case_result

if __name__ == '__main__':
	get_backlist()
	