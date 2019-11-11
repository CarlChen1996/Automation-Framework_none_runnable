# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:38
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : Analyzer.py
# @Project : demo
import os
import threading

from Common_Library.file_operator import YamlFile
from Common_Library.file_operator import XlsxFile
from Framework_Kernel.log import assemble_log


class Analyzer:
    def __init__(self):
        pass

    def analyze_file(self, file):
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
            return res
        f.close(file_handle)
        return res

    def analyze_files_in_list(self, file_list):
        result_list = []
        for current_file in file_list:
            result = self.analyze_file(current_file)
            if result is not False:
                result_list.append({current_file: result})
        assemble_log.info("generate data finished")
        return result_list


class FrameworkSettings:
    _instance_lock = threading.Lock()
    framework_settings = Analyzer().analyze_file(os.path.join(
            (os.path.abspath(r".\Configuration")), "config_framework_list.yml"))

    def __init__(self, *args, **kwargs):
        self.__framework_settings = FrameworkSettings.framework_settings
        self.ftp_settings = self.__framework_settings['ftp_settings']
        self.jenkins_settings = self.__framework_settings['jenkins_settings']
        self.qtp_settings = self.__framework_settings['qtp_settings']
        self.hpdm_settings = self.__framework_settings['hpdm_settings']
        self.email_settings = self.__framework_settings['email_settings']
        self.report_settings = self.__framework_settings['report_settings']
        self.log_settings = self.__framework_settings['log_settings']
        self.global_settings = self.__framework_settings['global_settings']

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with FrameworkSettings._instance_lock:
                if not hasattr(cls, '_instance'):
                    FrameworkSettings._instance = super().__new__(cls)
            return FrameworkSettings._instance
        else:
            return FrameworkSettings._instance
