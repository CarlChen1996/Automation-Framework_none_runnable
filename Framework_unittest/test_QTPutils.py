# -*- coding: utf-8 -*-
# @Time    : 9/10/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_QTPutils.py
# @Project : Automation-Framework

'''
set_up:Instantiated task, instantiated QTP_HPDM and Host
test_launch_QTP: test launch QTP
test_discover_device: test discover device by QTP
test_create_template: test create template by QTP
test_deploy_package: test deploy package by QTP
test_execute_package: test execute package by QTP
test_collect_result: test collect result by QTP
'''


from Framework_Kernel import task
from Framework_Kernel.QTPutils import HPDMOperator
from Framework_Kernel.host import Host
import unittest
from unittest.mock import patch
import pywintypes


class QTPutilsTest(unittest.TestCase):
    def setUp(self):
        self.qtp = HPDMOperator()
        self.task = task.Task(name='test')
        self.deploy_host = Host(ip='15.83.240.98', mac='1A2B3C4D5E6F')

    '''
    test_launch_QTP:Method for asserting exception content not found
    e = pywintypes.com_error(-2147352567, 'Exception occurred.', (0, 'Micro Focus Unified Functional Testing',
                            'Cannot open test.', None, 0, -2146827282), None)
    '''

    def test_launch_QTP(self):
        try:
            self.qtp._HPDMOperator__run_qtp_script('')
        except Exception as e:
            self.assertIsInstance(e, pywintypes.com_error)

    @patch('Framework_Kernel.QTPutils.HPDMOperator._HPDMOperator__run_qtp_script')
    def test_discover_device(self, run_script_mock):
        self.qtp.discover_devices(self.task)
        run_script_mock.assert_called_once_with(self.qtp._HPDMOperator__discover_devices_path)

    @patch('Framework_Kernel.QTPutils.HPDMOperator._HPDMOperator__run_qtp_script')
    def test_create_template(self, run_script_mock):
        self.qtp._HPDMOperator__create_filter()
        run_script_mock.assert_called_once_with(self.qtp._HPDMOperator__create_filter_path)

    @patch('Framework_Kernel.QTPutils.HPDMOperator._HPDMOperator__initial_test_data')
    @patch('Framework_Kernel.QTPutils.HPDMOperator._HPDMOperator__upload_test_data')
    @patch('Framework_Kernel.QTPutils.HPDMOperator.discover_devices')
    @patch('Framework_Kernel.QTPutils.HPDMOperator._HPDMOperator__run_qtp_script')
    def test_deploy_package(self, run_script_mock, discover_devices_mock, upload_excek_mock, initial_mock):
        initial_mock.return_value = True
        self.qtp.deploy_task(self.task, self.deploy_host)
        upload_excek_mock.assert_called_once()
        discover_devices_mock.assert_called_once_with(self.task)
        run_script_mock.assert_called_once_with(self.qtp._HPDMOperator__send_packages_path)

    @patch('Framework_Kernel.QTPutils.HPDMOperator._HPDMOperator__run_qtp_script')
    def test_execute_package(self, run_script_mock):
        self.qtp.execute_task(self.deploy_host)
        run_script_mock.assert_called_once_with(self.qtp._HPDMOperator__send_command_path)

    @patch('Framework_Kernel.QTPutils.HPDMOperator._HPDMOperator__run_qtp_script')
    def test_collect_result(self, run_script_mock):
        self.qtp.get_result(self.deploy_host)
        run_script_mock.assert_called_once_with(self.qtp._HPDMOperator__get_result_path)
