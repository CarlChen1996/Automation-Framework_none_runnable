# -*- coding: utf-8 -*-
# @Time    : 9/24/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_task.py
# @Project : Automation-Framework
from Framework_Kernel import host
from Framework_Kernel.task import Task
from unittest.mock import patch
import unittest


class TaskTest(unittest.TestCase):
    def setUp(self):
        self.task = Task(name='test')
        self.host = host.WindowsBuildHost(ip='1.1.1.1', mac=666666)

    @patch('Framework_Kernel.host.Build.build_task')
    def test_build(self, build_mock):
        self.task.build(self.host)
        build_mock.assert_called_once_with(self.task)
