# -*- coding: utf-8 -*-
# @Time    : 7/31/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_report.py
# @Project : Automation-Framework
from Framework_Kernel import report, host, task
import os
import unittest
import shutil

'''
setUp: remove static folder and .html file
tearDown: remove static folder and .html file
test_generate_report: generate a .html file based on the result.yaml
'''


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.static_folder = '.\\Report\\report_for_unittest\\static'
        self.html = '.\\Report\\report_for_unittest\\report_for_unittest.html'
        if os.path.exists(self.static_folder):
            shutil.rmtree(self.static_folder)
        if os.path.exists(self.html):
            os.remove(self.html)
        host1 = host.WindowsExecuteHost('15.83.248.208', '')
        host2 = host.WindowsExecuteHost('15.83.250.20', '')
        self.task = task.Task(name='report_for_unittest')
        self.task.insert_uut_list(host1)
        self.task.insert_uut_list(host2)

    def tearDown(self):
        shutil.rmtree(self.static_folder)
        os.remove(self.html)

    def test_generate_report(self):
        test_report = report.Report(self.task)
        test_report.generate()
        self.assertIn('report_for_unittest.html', os.listdir('.\\Report\\report_for_unittest'))
