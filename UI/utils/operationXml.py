#!/usr/bin/env python
# encoding=UTF-8

import os
import xml.dom.minidom

class OperationXml(object):

    def dir_base(self, fileName, filePath='data'):
        '''get file at data repository
           :param fileName is the name of the file
           :param filePath is the name of the file directory
        '''
        # os.path.dirname(os.path.dirname(__file__))      # D:/xiaozhan_git/study_20190608/UI
        # FileNotFoundError: [Errno 2] No such file or directory: 'D:/xiaozhan_git/study_20190608/UI\\data\\ui.xml'
        # for linux you can use
        # os.path.join(os.path.dirname(os.path.dirname(__file__)), filePath, fileName)
        # for windows you should use,this is also ok for linux
        # return os.path.dirname(os.path.dirname(__file__)) + "/" + filePath + "/" + fileName
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), filePath, fileName).replace("\\", "/")

    def getXmlData(self, value):
        '''
        get the individual data for specified tag
        :param value: tag name
        :return: tag value
        '''
        dom = xml.dom.minidom.parse(self.dir_base('test.xml'))
        db = dom.documentElement
        name = db.getElementsByTagName(value)
        nameValue = name[0]
        return nameValue.firstChild.data

    def getXmlUser(self, parent, child):
        '''
        get the value of child tag attribute value
        :param parent: parent tag name
        :param child: child tag name
        :return: child tag value
        '''
        dom = xml.dom.minidom.parse(self.dir_base('test.xml'))
        db = dom.documentElement
        itemList = db.getElementsByTagName(parent)
        item = itemList[0]
        return item.getAttribute(child)

if __name__ == '__main__':
    data = OperationXml()
    r = data.dir_base('test.xml')
    print(r)
    r = data.getXmlData('url')
    print(r)