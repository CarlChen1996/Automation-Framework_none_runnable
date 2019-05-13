# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
import sys

class File:
    def __init__(self,FolderPath,Name,Size):
        self.FolderPath=FolderPath
        self.Name=Name
        self.Size=Size
    def open(self):
        print(sys._getframe().f_code.co_name +" "+ self.Name+"  finished")
    def read(self):
        print(sys._getframe().f_code.co_name +"  finished")
    def write(self):
        print(sys._getframe().f_code.co_name +"  finished")
    def close(self):
        print(sys._getframe().f_code.co_name+" "+ self.Name +"  finished")
    def copy(self):
        print(sys._getframe().f_code.co_name +"  finished")
    def move(self):
        print(sys._getframe().f_code.co_name +"  finished")
    def delete(self):
        print(sys._getframe().f_code.co_name +"  finished")
    def rename(self):
        print(sys._getframe().f_code.co_name +"  finished")
    def exist(self):
        print(sys._getframe().f_code.co_name +"  finished")

class XLSX(File):
    def __init__(self,FolderPath,Name,Size,SheetNames,rows,cols):
        File.__init__(self,FolderPath,Name,Size)
        self.SheetNames=SheetNames
        self.rows=rows
        self.cols=cols
    def getSheetNames(self):
        print(sys._getframe().f_code.co_name + "  finished")
    def getRows(self):
        print(sys._getframe().f_code.co_name + "  finished")
    def getCols(self):
        print(sys._getframe().f_code.co_name + "  finished")

class MSG(File):
    def __init__(self, FolderPath, Name, Size,subject,receiver,sender,sendDate,content,attachment):
        File.__init__(self, FolderPath, Name, Size)
        self.subject=subject
        self.receiver=receiver
        self.sender=sender
        self.sendDate=sendDate
        self.content=content
        self.attachment=attachment
    def getAttanchment(self):
        print(sys._getframe().f_code.co_name + "  finished")

class YAML(File):
    pass
class HTML(File):
    pass

class TXT(File):
    pass

if __name__=="__main__":

    folderpath="c:\\test"
    name="123.txt"
    size=0

    # f=File(folderpath,name,size)
    # f.open()
    # f.read()
    # f.close()

    # sheetname="a"
    # colum=1
    # row=2
    # xx=XLSX(folderpath,name,size,sheetname,row,colum)
    # xx.open()
    # xx.getSheetNames()
    # xx.getRows()
    # xx.close()

    # subject="bamboo's mail"
    # receiver="bamboo.pan@hp.com"
    # sender="bamboo1@hp.com"
    # senddate="20190501"
    # content="test mail"
    # attachment="123.txt"
    #
    # msg=MSG(folderpath,name,size,subject,receiver,sender,senddate,content,attachment)
    # msg.open()
    # msg.getAttanchment()
    # msg.close()

    txt=TXT(folderpath,name,size)
    txt.open()
    txt.read()
    txt.close()