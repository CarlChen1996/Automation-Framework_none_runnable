# -*- coding: utf-8 -*-
# @Time   : 2019/7/15 10:32
# @Author  : balance.cheng
# @Email   : balance.cheng@hp.com
# @File    : QTPutils.py
# @Project : demo
import time

import win32com.client
import os
import re
import ftplib
import openpyxl
# from Framework_Kernel.task import Task
# from Framework_Kernel.host import WindowsExecuteHost


class QTP_HPDM:
    def __init__(self):
        self.__ftp = r'15.83.248.251'
        self.__ip = "15.83.248.251"
        self.__create_filter_path = r'c:\ScriptsCopy\CreateFilter'
        self.__create_template_path = r'c:\ScriptsCopy\CreateTemplates'
        self.__send_command_path = r'c:\ScriptsCopy\SendCommand'
        self.__send_packages_path = r'c:\ScriptsCopy\SendPackages'
        self.__get_result_path = r'c:\ScriptsCopy\CaptureFiles'
        self.__discover_devices_path = r'c:\ScriptsCopy\DiscoverDevices'
        root = os.path.dirname(os.path.dirname(__file__))
        self.__test_data_path = os.path.join(root, 'Configuration\\test_data.xlsx')

    def set_test_data(self, task):
        """
        For Deploy
        """
        workbook = openpyxl.load_workbook(self.__test_data_path)
        """
        col1:IP
        col2:Mac
        """
        # ------Delete exist Data-------------------------------------------
        os_list = {"THINPRO7":"HP ThinPro 7", "WES7P":"WES7P-64", "WES10":"Win10IoT-64", "WES7E":"WES7E"}
        # print(list(os_list.values()))
        for os_item in os_list.values():
            sheet_uut = workbook['UUT_{}'.format(os_item)]
            rows = sheet_uut.max_row
            for i in range(2, rows+1):
                """
                Delete all the data in sheet
                """
                sheet_uut.delete_rows(2)
                workbook.save(self.__test_data_path)
        # ---------------------------------------------------------------------
        # ----------Set UUT Data according task uut_list---------------------------------
        for uut in task.get_uut_list():
            if uut.get_version().upper() in os_list.keys():
                sheet_uut = workbook['UUT_{}'.format(os_list[uut.get_version().upper()])]
                max_row = sheet_uut.max_row
                # print(uut.get_version(),sheet_uut.max_row)
                sheet_uut.cell(max_row+1, 1).value=uut.get_ip()
                sheet_uut.cell(max_row+1, 2).value=uut.get_mac().upper()
                print('===========================================')
                print(uut.get_ip(), uut.get_mac())
                print('===========================================')
                workbook.save(self.__test_data_path)
        # ---------Set Config Data according task uut_list exe_list ------------------
        package_path = os.path.dirname(task.get_exe_file_list()[0])
        sheet_config = workbook['Config']
        if 'LINUX' in package_path.upper():
            sheet_config.cell(2, 1).value = "Linux_{}".format(task.get_name())
        elif 'WINDOW' in package_path.upper():
            sheet_config.cell(2, 1).value = "Windows_{}".format(task.get_name())
        else:
            sheet_config.cell(2, 1).value = "Unknown_{}".format(task.get_name())
        sheet_config.cell(2, 2).value = 'c:/inetpub/ftproot{}'.format(package_path)
        workbook.save(self.__test_data_path)
        self.__upload_test_data()

    def set_execute_data(self, host, task):
        """
        This task only for support exe_file_list
        """
        ip = host.get_ip()
        version = host.get_version()
        mac = host.get_mac()
        workbook = openpyxl.load_workbook(self.__test_data_path)
        """
        col1:IP
        col2:Mac
        """
        # ------Delete exist Data-------------------------------------------
        os_list = {"THINPRO7":"HP ThinPro 7", "WES7P":"WES7P-64", "WES10":"Win10IoT-64", "WES7E":"WES7E"}
        for os_item in os_list.values():
            sheet_uut = workbook['UUT_{}'.format(os_item)]
            rows = sheet_uut.max_row
            for i in range(2, rows+1):
                """
                Delete all the data in OS sheet
                """
                sheet_uut.delete_rows(2)
                workbook.save(self.__test_data_path)
        if version in os_list.keys():
            sheet_uut = workbook['UUT_{}'.format(os_list[version.upper()])]
            max_row = sheet_uut.max_row
            sheet_uut.cell(max_row + 1, 1).value = ip
            sheet_uut.cell(max_row + 1, 2).value = mac.upper()
            workbook.save(self.__test_data_path)
        # ---Set exe file path data---------------------------
        package_path = os.path.dirname(task.get_exe_file_list()[0])
        sheet_config = workbook['Config']
        if 'LINUX' in package_path.upper():
            sheet_config.cell(2, 1).value = "Linux_{}".format(task.get_name())
        elif 'WINDOW' in package_path.upper():
            sheet_config.cell(2, 1).value = "Windows_{}".format(task.get_name())
        else:
            sheet_config.cell(2, 1).value = "Unknown_{}".format(task.get_name())
        sheet_config.cell(2, 2).value = 'c:/inetpub/ftproot{}'.format(package_path)
        workbook.save(self.__test_data_path)
        self.__upload_test_data()

    def __upload_test_data(self):
        ftp = ftplib.FTP(self.__ftp)
        ftp.login('automation','Shanghai2010')
        print(ftp.nlst())
        ftp.storbinary('STOR test_data.xlsx', open(self.__test_data_path, 'rb'), 1024)
        ftp.close()

    def __run_qtp_script(self, testPath):
        import pythoncom
        pythoncom.CoInitialize()
        qtp = win32com.client.DispatchEx("QuickTest.Application", self.__ip)
        qtp.Launch()
        qtp.Visible = True
        qtp.Open(testPath)
        qtp.Test.Run()
        pythoncom.CoUninitialize()
        time.sleep(5)

    def __create_filter(self):
        """
        This Function can be put in QTP script
        """
        self.__run_qtp_script(self.__create_filter_path)

    def discover_devices(self, task):
        self.set_test_data(task)
        self.__run_qtp_script(self.__discover_devices_path)

    def create_template(self):
        self.__run_qtp_script(self.__create_template_path)

    def deploy_task(self, task, deploy_host):
        self.set_test_data(task)
        self.discover_devices(task)
        '''
        Do operation, put uutlist and package path(local path) to QTP test_data.xlsx
        '''
        self.__ip = deploy_host.get_ip()
        self.__run_qtp_script(self.__send_packages_path)

    def execute_task(self):
        # test data is prepared after deploy
        self.__run_qtp_script(self.__send_command_path)

    # def execute_task(self, host, task):
    #     self.set_execute_data(host, task)
    #     self.__run_qtp_script(self.__send_command_path)

    def get_result(self):
        # test data is prepared after deploy
        self.__run_qtp_script(self.__get_result_path)

    # def get_result(self, task):
    #     self.set_test_data(task)
    #     self.__run_qtp_script(self.__get_result_path)


# class Deploy:
#     def __init__(self):
#         pass
#
#     def deploy(self, task):
#         QTP_HPDM().deploy_task(task)
#
#
# class Execute():
#     def __init__(self):
#         pass
#
#     def execute_task(self, task):
#         QTP_HPDM().execute_task(task)
#
#     def check_status(self, task):
#         pass
#
#     def collect_result(self, task):
#         QTP_HPDM().get_result(task)


if __name__ == '__main__':

    task = Task('precheck')
    uut1 = WindowsExecuteHost('15.83.248.208', '7C:D3:0A:05:01:97', '', 'WES10', 'Admin', 'Admin', '', 'on')
    uut2 = WindowsExecuteHost('15.83.250.20', '48:0F:CF:BC:DD:3C', '', 'WES10', 'Admin', 'Admin', '', 'on')
    uut3 = WindowsExecuteHost('15.83.250.205', '48:0F:CF:BB:7C:65', '', 'WES7E', 'Administrator', 'Administrator', '', 'on')
    uut4 = WindowsExecuteHost('15.83.250.210', '48:0F:CF:BB:7F:65', '', 'WES7E', 'Administrator', 'Administrator', '', 'on')
    task.insert_uut_list(uut1)
    task.insert_uut_list(uut2)
    task.insert_uut_list(uut3)
    task.insert_uut_list(uut4)
    task.insert_exe_file_list(r'C:\inetpub\ftproot\jenkins\windows\task_2\run.exe')
    # QTP_HPDM().set_test_data(task)
    QTP_HPDM().set_test_data(task)
