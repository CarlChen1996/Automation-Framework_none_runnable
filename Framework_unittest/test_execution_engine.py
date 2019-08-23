# -*- coding: utf-8 -*-
# @Time    : 7/31/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_execution_engine.py
# @Project : Automation-Framework
from Framework_Kernel import execution_engine, host
from Framework_Kernel.task import Task
from multiprocessing import Pipe
from unittest.mock import patch
import unittest

'''
setUp: Instantiated pipe and send task, instantiated Execution Engine
test_add_task_to_execution_mock: when add task to queue in Execution Engine, insert_task can be called
test_add_task_to_execution: add task to execution queue after pipe receive task
test_send_signal: Execution Engine can send signal after pipe receive task
test_send_email: send email can be called
test_remove_task_from_execution_queue_mock: remove task can be called by mock
test_remove_task_from_execution_queue: remove task can be called
'''


class ExecutionEngineTest(unittest.TestCase):
    def setUp(self):
        self.pipe = Pipe()
        self.deploy_list = []
        self.execution = execution_engine.ExecutionEngine(self.deploy_list, self.pipe[0])
        self.task_name = 'report_for_unittest'
        host1 = host.WindowsExecuteHost('15.83.248.208', '')
        host2 = host.WindowsExecuteHost('15.83.250.20', '')
        self.task = Task(name=self.task_name)
        self.task.insert_uut_list(host1)
        self.task.insert_uut_list(host2)
        self.pipe[1].send(self.task)

    @patch('Framework_Kernel.task_queue.Queue.insert_task')
    def test_add_task_to_execution_mock(self, insert_task):
        self.execution.insert_task_to_queue()
        insert_task.assert_called_once()

    def test_add_task_to_execution(self):
        self.assertEqual(self.execution.execution_queue.get_task_list(), [])
        self.execution.insert_task_to_queue()
        self.assertEqual(self.execution.execution_queue.get_task_list()[0].get_name(), self.task_name)

    def test_send_signal(self):
        self.execution.insert_task_to_queue()
        self.assertEqual(self.pipe[1].recv(), self.task_name)

    @patch('Framework_Kernel.report.Report.remove_report_folder')
    @patch('Framework_Kernel.execution_engine.ExecutionEngine.email_parameter')
    @patch('Common_Library.email_operator.Email.send_email')
    def test_send_email(self, email_mock, message_mock, remove_folder_mock):
        message_mock.return_value = '', '', '', '', ''
        self.execution.execution_queue.insert_task(task=self.task)
        self.execution.send_report(self.task)
        email_mock.assert_called_once()

    @patch('Framework_Kernel.execution_engine.ExecutionEngine.email_parameter')
    @patch('Framework_Kernel.report.Report.remove_report_folder')
    @patch('Common_Library.email_operator.Email.send_email')
    @patch('Framework_Kernel.task_queue.Queue.remove_task')
    def test_remove_task_from_execution_queue_mock(self, remove_task_mock, email_mock, remove_folder_mock,
                                                   message_mock):
        message_mock.return_value = '', '', '', '', ''
        self.execution.execution_queue.insert_task(task=self.task)
        self.assertIn(self.task, self.execution.execution_queue.get_task_list())
        self.execution.send_report(self.task)
        remove_task_mock.assert_called_once_with(self.task)

    @patch('Framework_Kernel.execution_engine.ExecutionEngine.email_parameter')
    @patch('Framework_Kernel.report.Report.remove_report_folder')
    @patch('Common_Library.email_operator.Email.send_email')
    def test_remove_task_from_execution_queue(self, email_mock, remove_folder_mock, message_mock):
        message_mock.return_value = '', '', '', '', ''
        self.execution.execution_queue.insert_task(task=self.task)
        self.assertIn(self.task, self.execution.execution_queue.get_task_list())
        self.execution.send_report(self.task)
        self.assertNotIn(self.task, self.execution.execution_queue.get_task_list())


if __name__ == '__main__':
    unittest.main()
