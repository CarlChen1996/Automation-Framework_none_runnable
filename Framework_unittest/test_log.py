# -*- coding: utf-8 -*-
# @Time    : 8/12/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_log.py
# @Project : Automation-Framework
from Framework_Kernel import log
from unittest.mock import patch
import unittest
import os

'''
read_log: read last log message
get_log_file: get the newest log file
get_newest_file: get get the newest file from directory
test_lower_level_log: lower level log message can not be log
test_equal_level_log: equal level log message can be log
test_higher_level_log: lower level log message can be log
test_custom_level: log with custom level
test_custom_separator: log with custom separator
test_log_critical: critical method can be called
test_log_error: error method can be called
test_log_warning: warning method can be called
test_log_info: info method can be called
test_log_debug: debug method can be called
test_custom_console_False: test without user console
test_custom_console_True: test with user console
'''


log_folder_name = 'unittest'
unittest_log = log.Log(name=log_folder_name, level='INFO')
custom_log_name = 'custom'
custom_separator = '?'
custom_log = log.Log(name=custom_log_name, level='ERROR', separator=custom_separator)


class LogTest(unittest.TestCase):
    def read_log(self, log_name):
        file = self.get_log_file(log_name)
        with open(file, 'r') as f:
            try:
                log_msg = f.readlines()[-1]
            except Exception as e:
                if type(e) == IndexError:
                    log_msg = ''
                else:
                    print(e)
                    return False
            return log_msg

    def get_log_file(self, log_name):
        folder = self.get_newest_file('.\\Log')
        log_folder = os.path.join(folder, log_name)
        return self.get_newest_file(log_folder)

    @staticmethod
    def get_newest_file(log_path):
        lists = os.listdir(log_path)
        lists.sort(key=lambda fn: os.path.getmtime(log_path + '\\' + fn))
        return os.path.join(log_path, lists[-1])

    def test_lower_level_log(self):
        unittest_log.debug('lower level log')
        log_msg = self.read_log(log_folder_name)
        if log_msg is False:
            log_msg = ''
            print('read lower level log raise exception')
        self.assertNotIn('lower level log', log_msg)

    def test_equal_level_log(self):
        unittest_log.info('equal level log')
        log_msg = self.read_log(log_folder_name)
        if log_msg is False:
            log_msg = ''
            print('read equal level log raise exception')
        self.assertIn('equal level log', log_msg)

    def test_higher_level_log(self):
        unittest_log.warning('higher level log')
        log_msg = self.read_log(log_folder_name)
        if log_msg is False:
            log_msg = ''
            print('read higher level log raise exception')
        self.assertIn('higher level log', log_msg)

    def test_custom_level(self):
        custom_log.info('custom level log')
        log_msg = self.read_log(custom_log_name)
        if log_msg is False:
            log_msg = ''
            print('read custom level log raise exception')
        self.assertNotIn('custom level log', log_msg)
        custom_log.error('write log with custom level')
        log_msg = self.read_log(custom_log_name)
        if log_msg is False:
            log_msg = ''
            print('read custom level log raise exception')
        self.assertIn('write log with custom level', log_msg)

    def test_custom_separator(self):
        custom_log.error('write log with custom separator')
        log_msg = self.read_log(custom_log_name)
        if log_msg is False:
            log_msg = ''
            print('read custom separator log raise exception')
        self.assertIn(custom_separator, log_msg)

    @patch('logging.Logger.critical')
    def test_log_critical(self, critical_mock):
        unittest_log.critical('test')
        critical_mock.assert_called_once_with('test')

    @patch('logging.Logger.error')
    def test_log_error(self, error_mock):
        unittest_log.error('test')
        error_mock.assert_called_once_with('test')

    @patch('logging.Logger.warning')
    def test_log_warning(self, warning_mock):
        unittest_log.warning('test')
        warning_mock.assert_called_once_with('test')

    @patch('logging.Logger.info')
    def test_log_info(self, info_mock):
        unittest_log.info('test')
        info_mock.assert_called_once_with('test')

    @patch('logging.Logger.debug')
    def test_log_debug(self, debug_mock):
        unittest_log.debug('test')
        debug_mock.assert_called_once_with('test')

    @patch('logging.Formatter')
    def test_custom_console_False(self, separator_mock):
        user_console = False
        log.Log(name='user_console', level='INFO', separator=custom_separator, use_console=user_console)
        separator_mock.assert_called_once_with("[%(asctime)s] {} %(name)s {} [%(levelname)s] {} %(message)s"
                                               .format(custom_separator, custom_separator, custom_separator))
        self.assertEqual(separator_mock.call_count, 1)

    @patch('logging.Formatter')
    def test_custom_console_True(self, separator_mock):
        user_console = True
        log.Log(name='user_console', level='INFO', separator=custom_separator, use_console=user_console)
        self.assertEqual(separator_mock.call_count, 2)
