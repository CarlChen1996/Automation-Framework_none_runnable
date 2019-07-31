from Framework_Kernel import analyzer
from Common_Library import file
from unittest.mock import patch
import os
import unittest


'''
setUp: define excel name without Loaded prefix before test
tearDown: define excel name with Loaded prefix after test
test_load_excel: load excel by function analyzer.Analyzer.load
test_read_excel: read excel by function file.XlsxFile.read
'''


excel_content = {
    'name': 'task_1', 'email': ['jie.liu1@hp.com'], 'needbuild': True, 'repository': 'https://hp.com',
    'uutlist': [{'ip': '15.83.250.1', 'mac': '13354k31sa', 'os': 'wes7p'},
                {'ip': '15.83.250.2', 'mac': '13354k31sb', 'os': 'wes7p'}],
    'testscripts': ['script2', 'script4', 'script3', 'script6']}


class AnalyzerTest(unittest.TestCase):
    def setUp(self):
        self.excel_name = '.\\Configuration\\test_plan\\TEST_PLAN_unittest.xlsx'
        self.loaded_excel = '.\\Configuration\\test_plan\\Loaded_TEST_PLAN_unittest.xlsx'
        if os.path.exists(self.loaded_excel):
            os.rename(self.loaded_excel, self.excel_name)

    def tearDown(self):
        os.rename(self.excel_name, self.loaded_excel)

    @patch('Common_Library.file.XlsxFile.read', return_value=excel_content)
    def test_load_excel(self, excel_read):
        file_list = [self.excel_name]
        excel_list = analyzer.Analyzer(file_list)
        self.assertEqual(excel_list.load(), [{file_list[0]: excel_read.return_value}])

    def test_read_excel(self):
        excel_file = file.XlsxFile(os.path.dirname(self.excel_name), os.path.basename(self.excel_name))
        self.assertEqual(excel_file.read(excel_file.open()), excel_content)
