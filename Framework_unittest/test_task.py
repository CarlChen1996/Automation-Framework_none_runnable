# -*- coding: utf-8 -*-
# @Time    : 9/24/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_task.py
# @Project : Automation-Framework
from Framework_Kernel import host, script
from Framework_Kernel.task import Task
from unittest.mock import patch
import unittest


class TaskTest(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.task = Task(name=self.name)
        self.uut = host.Host(ip='1.1.1.1', mac=666666)
        self.build_host = host.WindowsBuildHost(ip='1.1.1.1', mac=666666)
        self.deploy_host = host.WindowsDeployHost(ip='1.1.1.1', mac=666666)
        self.script = script.Script(name='script')

    def test_get_script(self):
        self.assertEqual(self.task.get_script_list(), [])

    def test_insert_script(self):
        self.task.insert_script(self.script)
        self.assertIn(self.script, self.task.get_script_list())

    def test_insert_exe_file(self):
        exe_file = 1
        self.task.insert_exe_file_list(exe_file)
        self.assertIn(exe_file, self.task.get_exe_file_list())

    def test_get_exe_file(self):
        self.assertEqual(self.task.get_exe_file_list(), [])

    def test_insert_uut(self):
        self.task.insert_uut_list(self.uut)
        self.assertIn(self.uut, self.task.get_uut_list())

    def test_get_uut(self):
        self.assertEqual(self.task.get_uut_list(), [])

    def test_get_name(self):
        self.assertEqual(self.task.get_name(), self.name)

    def test_get_status(self):
        self.assertEqual(self.task.get_status(), '')

    def test_set_status(self):
        status = 'Idle'
        self.task.set_status(status)
        self.assertEqual(self.task.get_status(), status)

    def test_get_state(self):
        self.assertEqual(self.task.get_state(), '')

    def test_set_state(self):
        state = 'Idle'
        self.task.set_state(state)
        self.assertEqual(self.task.get_state(), state)

    def test_get_email(self):
        self.assertEqual(self.task.get_email(), [])
        email = ['smtp1.hp.com']
        task = Task(name=self.name, email=email)
        self.assertEqual(task.get_email(), email)

    def test_get_repository(self):
        self.assertEqual(self.task.get_repository(), '')
        repository = 'http://hp.com'
        task = Task(name=self.name, repository=repository)
        self.assertEqual(task.get_repository(), repository)

    @patch('Framework_Kernel.host.Build.build_task')
    def test_build(self, build_mock):
        self.task.build(self.build_host)
        build_mock.assert_called_once_with(self.task)

    @patch('Framework_Kernel.host.Deploy.deploy_task')
    def test_deploy(self, deploy_mock):
        self.task.deploy(self.deploy_host)
        deploy_mock.assert_called_once_with(self.task)

    @patch('Framework_Kernel.QTPutils.HPDMOperator.execute_task')
    def test_execute(self, execute_mock):
        self.task.execute(self.deploy_host)
        execute_mock.assert_called_once_with(self.deploy_host)

    @patch('Framework_Kernel.QTPutils.HPDMOperator.get_result')
    def test_collect_result(self, get_result_mock):
        self.task.collect_result(self.deploy_host)
        get_result_mock.assert_called_once_with(self.deploy_host)
