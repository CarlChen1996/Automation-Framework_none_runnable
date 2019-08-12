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


class AnalyzerTest(unittest.TestCase):
    def read_log(self, log_name):
        file = self.get_log_file(log_name)
        with open(file, 'w') as f:
            return f.readlines()[-1]

    def get_log_file(self, log_name):
        folder = self.get_newest_file('.\\Log')
        log_folder = os.path.join(folder, log_name)
        return os.path.join(log_folder, self.get_newest_file(log_folder))

    @staticmethod
    def get_newest_file(log_path):
        lists = os.listdir(log_path)
        lists.sort(key=lambda fn: os.path.getmtime(log_path + '\\' + fn))
        return os.path.join(log_path, lists[-1])

    def setUp(self):
        self.log_name = 'unittest'
        self.log = log.Log(name=self.log_name)

    @patch('logging.Logger.critical')
    def test_log_critical(self, critical_mock):
        self.log.critical('test')
        critical_mock.assert_called_once_with('test')

    @patch('logging.Logger.warning')
    def test_log_warning(self, warning_mock):
        self.log.warning('test')
        warning_mock.assert_called_once_with('test')

    @patch('logging.Logger.error')
    def test_log_error(self, error_mock):
        self.log.error('test')
        error_mock.assert_called_once_with('test')

    @patch('logging.Logger.info')
    def test_log_info(self, info_mock):
        self.log.info('test')
        info_mock.assert_called_once_with('test')

    @patch('logging.Logger.debug')
    def test_log_debug(self, debug_mock):
        self.log.debug('test')
        debug_mock.assert_called_once_with('test')

    def test_write_high_level_log(self):
        pass

    def test_write_low_level_log(self):
        pass

    @patch('logging.Formatter')
    def test_custom_separator_False(self, separator_mock):
        separator = ':'
        user_console = False
        log.Log(name=self.log_name, level='INFO', separator=separator, use_console=user_console)
        separator_mock.assert_called_once_with("[%(asctime)s] {} %(name)s {} [%(levelname)s] {} %(message)s"
                                               .format(separator, separator, separator))
        self.assertEqual(separator_mock.call_count, 1)

    @patch('logging.Formatter')
    def test_custom_separator_True(self, separator_mock):
        separator = ':'
        user_console = True
        log.Log(name=self.log_name, level='INFO', separator=separator, use_console=user_console)
        self.assertEqual(separator_mock.call_count, 2)


if __name__ == '__main__':
    unittest.main()
