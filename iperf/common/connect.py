#!/usr/bin/env python3
# coding: utf-8

from pymongo import MongoClient

class Connect(object):
	@staticmethod
	def get_connection():
		#return MongoClient('mongodb://localhost:27017/')
		return MongoClient('mongodb://128.224.153.34:27017,128.224.166.223:27107,128.224.166.211:27107/')