# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:38
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : Analyzer.py
# @Project : demo
import os
from Common_Library.file import YamlFile
from Common_Library.file import XlsxFile
from Framework_Kernel.log import assemble_log



class Analyzer:
    def __init__(self, file_list):
        self.file_list = file_list

    def load(self):
        assemble_log.info('Load Data from file ')
        res_tem_list = []
        for i in self.file_list:
            if os.path.splitext(i)[1].lower() == '.xlsx':
                f = XlsxFile(os.path.dirname(i), os.path.basename(i))
                file_handle = f.open()
                sheet_handle = f.get_sheet_name(file_handle)[0]
                res = f.read(file_handle[sheet_handle])
            elif os.path.splitext(i)[1].lower() == '.yml' or os.path.splitext(i)[1].lower() == '.yaml':
                f = YamlFile(os.path.dirname(i), os.path.basename(i))
                file_handle = f.open()
                res = f.read(file_handle)
            else:
                return []
            res_tem_list.append({i: res})
            # print("load data {} finished".format(i))
            f.close(file_handle)
            # print("close file {} finished".format(i))
        # print("load all data finised")
        return res_tem_list

    def generate(self, res_list):
        assemble_log.info('generate Data')
        # print("generate data finished")
        return res_list
