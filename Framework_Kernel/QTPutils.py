# -*- coding: utf-8 -*-
# @Time   : 2019/7/15 10:32
# @Author  : balance.cheng
# @Email   : balance.cheng@hp.com
# @File    : QTPutils.py
# @Project : demo
import win32com.client
import os
import re
import ftplib
import openpyxl


class QTP_HPDM:
    def __init__(self):
        self.__ftp = r'15.83.248.251'
        self.__ftp_user = r'automation'
        self.__ftp_passwd = 'Shanghai2010'
        self.__ip = "15.83.248.251"
        self.__create_filter_path = r'c:\Scripts\CreateFilter'
        self.__create_template_path = r'c:\Scripts\CreateTemplates'
        self.__send_command_path = r'c:\Scripts\SendCommand'
        self.__send_packages_path = r'c:\Scripts\SendPackages'
        self.__get_result_path = r'c:\Scripts\CaptureFiles'

    def get_mac_by_ip(self, ip):
        pattern_mac = re.compile('([a-f0-9]{2}[-:]){5}[a-f0-9]{2}', re.I)
        os.popen('ping -n 1 -w 500 {} > nul'.format(ip))
        macaddr = os.popen('arp -a {}'.format(ip))
        macaddr = pattern_mac.search(macaddr.read())
        if macaddr:
            return macaddr.group()
        else:
            return None

    def set_test_data(self, task):
        # ftp = ftplib.FTP(self.__ftp)
        root = os.path.dirname(os.path.dirname(__file__))
        test_data_path = os.path.join(root, 'Configuration\\test_data.xlsx')
        workbook = openpyxl.load_workbook(test_data_path)
        sheet_uut = workbook['UUT']
        """
        col1:IP
        col2:Mac
        col3:OS
        """
        rows = sheet_uut.max_row
        for i in range(2, rows+1):
            """
            Delete all the data in sheet
            """
            ip = sheet_uut.cell(i, 1).value
            mac = sheet_uut.cell(i, 2).value
            _os = sheet_uut.cell(i, 3).value
            print(ip, mac, _os)
            sheet_uut.delete_rows(2)
            workbook.save(test_data_path)

    def __run_qtp_script(self, testPath):
        qtp = win32com.client.DispatchEx("QuickTest.Application", self.ip)
        qtp.Launch()
        qtp.Visible = True
        qtp.Open(testPath)
        qtp.Test.Run()

    def __create_filter(self):
        """
        This Function can be put in QTP script
        """
        self.__run_qtp_script(self.__create_filter_path)

    def create_template(self):
        self.__run_qtp_script(self.__create_template_path)

    def deploy_task(self, task):
        # uut = task.uut_list[0]
        # package_path = task.exe_list[0]
        '''
        Do operation, put uutlist and package path(local path) to QTP test_data.xlsx
        '''
        self.__run_qtp_script(self.__send_packages_path)

    def execute_task(self, task):
        # uut_list = task.uut_list
        # exe_list = task.exe_list
        '''
        Do operation, put uut_list and exe_list to QTP test_data.xlsx
        exe_list[0]: local folder
        exe_list[1]: exe file name
        '''

        self.__run_qtp_script(self.__send_command_path)

    def get_result(self, task):
        self.__run_qtp_script(self.__get_result_path)


class Deploy:
    def __init__(self):
        pass

    def deploy(self, task):
        QTP_HPDM().deploy(task)


class Execute(QTP_HPDM):
    def __init__(self):
        pass

    def execute_task(self, task):
        QTP_HPDM().execute_task(task)

    def check_status(self, task):
        pass

    def collect_result(self, task):
        QTP_HPDM().get_result(task)


QTP_HPDM().set_test_data('test')
# print(__file__)
