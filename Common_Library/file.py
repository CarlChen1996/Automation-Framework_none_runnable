# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
import sys
import os
import yaml


class File:
    def __init__(self, folder_path, name, size=0):
        self.folder_path = folder_path
        self.name = name
        self.size = size

    def open(self):
        file_name = os.path.join(self.folder_path, self.name)
        f = open(file_name)
        print("open {} pass".format(file_name))
        return f

    def read(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def write(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def close(self):

        print(sys._getframe().f_code.co_name + " " + self.name + "  finished")

    def copy(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def move(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def delete(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def rename(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def exist(self):
        print(sys._getframe().f_code.co_name + "  finished")


class XlsxFile(File):
    def __init__(self, folder_path, name, size, sheet_name, rows, cols):
        File.__init__(self, folder_path, name, size)
        self.sheet_name = sheet_name
        self.rows = rows
        self.cols = cols

    def get_sheet_name(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def get_rows(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def get_cols(self):
        print(sys._getframe().f_code.co_name + "  finished")


class MsgFile(File):
    def __init__(self, folder_path, name, size, subject, receiver, sender,
                 send_date, content, attachment):
        File.__init__(self, folder_path, name, size)
        self.subject = subject
        self.receiver = receiver
        self.sender = sender
        self.send_date = send_date
        self.content = content
        self.attachment = attachment

    def get_attanchment(self):
        print(sys._getframe().f_code.co_name + "  finished")


class YamlFile(File):
    def read(self, file_handle):
        res = yaml.load(file_handle)
        return res

    def close(self, file_handle):
        file_handle.close()


class HtmlFile(File):
    pass


class TxtFile(File):
    pass


if __name__ == "__main__":

    folder_path = "c:\\test"
    name = "123.txt"
    size = 0

    # f=File(folder_path,name,size)
    # f.open()
    # f.read()
    # f.close()

    # sheetname="a"
    # colum=1
    # row=2
    # xx=XLSX(folder_path,name,size,sheetname,row,colum)
    # xx.open()
    # xx._()
    # xx.getRows()
    # xx.close()

    # subject="bamboo's mail"
    # receiver="bamboo.pan@hp.com"
    # sender="bamboo1@hp.com"
    # senddate="20190501"
    # content="test mail"
    # attachment="123.txt"
    #
    # msg=MSG(folder_path,name,size,subject,receiver,sender,senddate,content,attachment)
    # msg.open()
    # msg.getAttanchment()
    # msg.close()

    txt = TxtFile(folder_path, name, size)
    txt.open()
    txt.read()
    txt.close()
