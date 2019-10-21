# -*- coding: utf-8 -*-
# @Time    : 21/10/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_error_handle.py
# @Project : Automation-Framework

from Framework_Kernel import error_handler
from unittest.mock import patch, Mock
import unittest


class ErrorHandle(unittest.TestCase):
    def setUp(self):
        self.engine_code = error_handler.EngineCode()
        self.error_level = error_handler.ErrorLevel()
        self.msg = 'unittest'
        self.error_msg = error_handler.ErrorMsg('00', '00', self.msg)

    def test_get_engine_name(self):
        self.assertEqual(self.engine_code.get_engine_name('00'), 'controller')
        self.assertEqual(self.engine_code.get_engine_name('01'), 'config_engine')
        self.assertEqual(self.engine_code.get_engine_name('02'), 'assembly_engine')
        self.assertEqual(self.engine_code.get_engine_name('03'), 'execute_engine')
        self.assertEqual(self.engine_code.get_engine_name('04'), 'report')
        self.assertEqual(self.engine_code.get_engine_name('05'), 'unknown engine_code')

    def test_get_error_level(self):
        self.assertEqual(self.error_level.get_error_level('00'), 'terminate_framework')
        self.assertEqual(self.error_level.get_error_level('01'), 'reset_framework')
        self.assertEqual(self.error_level.get_error_level('02'), 'reset_engine')
        self.assertEqual(self.error_level.get_error_level('03'), 'drop_task')
        self.assertEqual(self.error_level.get_error_level('04'), 'rerun_task')
        self.assertEqual(self.error_level.get_error_level('05'), 'mark_task')
        self.assertEqual(self.error_level.get_error_level('06'), 'record_and_continue')
        self.assertEqual(self.error_level.get_error_level('07'), 'unknown level code')

    def test_create_error_msg(self):
        self.assertEqual(self.error_msg.create_error_msg(), '0000{}'.format(self.msg))
        self.assertEqual(self.error_msg.error_msg, self.error_msg.create_error_msg())

    @patch('Framework_Kernel.error_handler.EngineCode.get_engine_name')
    @patch('Framework_Kernel.error_handler.ErrorLevel.get_error_level')
    def test_create_error_msg_full(self, engine_mock, level_mock):
        engine_mock.return_value = 'terminate_framework'
        level_mock.return_value = 'controller'
        self.assertEqual(self.error_msg.create_error_msg_full(),
                         'Error Level: "{}"\nEngine: "{}"\nDetails: "{}"'.format(engine_mock.return_value,
                                                                                 level_mock.return_value, self.msg))
        self.assertEqual(self.error_msg.error_msg_full, self.error_msg.create_error_msg_full())
