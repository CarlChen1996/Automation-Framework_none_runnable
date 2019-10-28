# -*- coding: utf-8 -*-
# @Time    : 10/28/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_scripts.py
# @Project : Automation-Framework
from Framework_Kernel import script
import unittest


class ScriptsTest(unittest.TestCase):
    def setUp(self):
        self.scripts_name = 'unittest'
        self.scripts = script.Script(name=self.scripts_name)

    def test_get_status(self):
        self.assertEqual(self.scripts.get_status(), 'NoRun')
        self.scripts.set_status('test')
        self.assertEqual(self.scripts.get_status(), 'test')

    def test_set_status(self):
        self.scripts.set_status('test')
        self.assertEqual(self.scripts.get_status(), 'test')

    def test_get_name(self):
        self.assertEqual(self.scripts.get_name(), self.scripts_name)
