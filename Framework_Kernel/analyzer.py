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

    def load(self, file):
        assemble_log.info('Load Data from file {}'.format(file))
        if os.path.splitext(file)[1].lower() == '.xlsx':
            f = XlsxFile(os.path.dirname(file), os.path.basename(file))
            file_handle = f.open()
            res = f.read(file_handle)
        elif os.path.splitext(file)[1].lower() == '.yml' or os.path.splitext(file)[1].lower() == '.yaml':
            f = YamlFile(os.path.dirname(file), os.path.basename(file))
            file_handle = f.open()
            res = f.read(file_handle)
        else:
            assemble_log.info('Unknown file format {}'.format(file))
            res = False
        f.close(file_handle)
        return res

    def generate(self):
        result_list = []
        for current_file in self.file_list:
            result = self.load(current_file)
            if result is not False:
                result_list.append({current_file: result})
        assemble_log.info("generate data finished")
        return result_list
