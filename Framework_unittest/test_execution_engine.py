# -*- coding: utf-8 -*-
# @Time    : 7/31/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_execution_engine.py
# @Project : Automation-Framework
from Framework_Kernel import execution_engine, host
from Framework_Kernel.task import Task
from multiprocessing import Pipe
from unittest.mock import patch, Mock
import unittest
import threading
import time

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
        self.deploy_host = host.WindowsDeployHost('1.1.1.1', 666666)
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

    @patch('Common_Library.email_operator.Email._Email__init_connection')
    @patch('os.remove')
    @patch('Framework_Kernel.report.Report.remove_report_folder')
    @patch('Framework_Kernel.execution_engine.ExecutionEngine.email_parameter')
    @patch('Common_Library.email_operator.Email.send_email')
    def test_send_email(self, email_mock, message_mock, remove_folder_mock, remove_mock, connect_mock):
        message_mock.return_value = '', '', '', '', ''
        self.execution.execution_queue.insert_task(task=self.task)
        self.execution.send_report(self.task)
        email_mock.assert_called_once()

    @patch('Common_Library.email_operator.Email._Email__init_connection')
    @patch('os.remove')
    @patch('Framework_Kernel.execution_engine.ExecutionEngine.email_parameter')
    @patch('Framework_Kernel.report.Report.remove_report_folder')
    @patch('Common_Library.email_operator.Email.send_email')
    @patch('Framework_Kernel.task_queue.Queue.remove_task')
    def test_remove_task_from_execution_queue_mock(self, remove_task_mock, email_mock, remove_folder_mock,
                                                   message_mock, remove_mock, connect_mock):
        message_mock.return_value = '', '', '', '', ''
        self.execution.execution_queue.insert_task(task=self.task)
        self.assertIn(self.task, self.execution.execution_queue.get_task_list())
        self.execution.send_report(self.task)
        remove_task_mock.assert_called_once_with(self.task)

    @patch('Common_Library.email_operator.Email._Email__init_connection')
    @patch('os.remove')
    @patch('Framework_Kernel.execution_engine.ExecutionEngine.email_parameter')
    @patch('Framework_Kernel.report.Report.remove_report_folder')
    @patch('Common_Library.email_operator.Email.send_email')
    def test_remove_task_from_execution_queue(self, email_mock, remove_folder_mock, message_mock, remove_mock,
                                              connect_mock):
        message_mock.return_value = '', '', '', '', ''
        self.execution.execution_queue.insert_task(task=self.task)
        self.assertIn(self.task, self.execution.execution_queue.get_task_list())
        self.execution.send_report(self.task)
        self.assertNotIn(self.task, self.execution.execution_queue.get_task_list())

    def test_load_config(self):
        pass

    @patch('Framework_Kernel.execution_engine.ExecutionEngine.deploy')
    @patch('Framework_Kernel.execution_engine.ExecutionEngine.download_result')
    @patch('Framework_Kernel.execution_engine.ExecutionEngine.send_report')
    def test_execute(self, report_mock, download_mock, deploy_mock):
        self.execution.current_thread_count = 2
        self.execution._ExecutionEngine__execute(self.task, self.deploy_host)
        deploy_mock.assert_called_once_with(self.deploy_host, self.task)
        download_mock.assert_called_once()
        report_mock.assert_called_once_with(self.task)
        self.assertEqual(self.execution.current_thread_count, 1)
        self.assertEqual(self.task.get_state(), 'Execute Finished')
        self.assertEqual(self.deploy_host.state, 'Idle')

    @patch('Framework_Kernel.execution_engine.ExecutionEngine.deploy')
    @patch('Framework_Kernel.execution_engine.ExecutionEngine.download_result')
    @patch('Framework_Kernel.execution_engine.ExecutionEngine.send_report')
    def test_execute_except(self, report_mock, download_mock, deploy_mock):
        deploy_mock.side_effect = EOFError
        self.execution.current_thread_count = 2
        self.execution._ExecutionEngine__execute(self.task, self.deploy_host)
        deploy_mock.assert_called_once_with(self.deploy_host, self.task)
        download_mock.assert_not_called()
        report_mock.assert_not_called()
        self.assertEqual(self.execution.current_thread_count, 1)
        self.assertEqual(self.task.get_state(), 'Assemble Finished')
        self.assertEqual(self.deploy_host.state, 'Idle')

    @patch('threading.Thread.start')
    @patch('threading.Thread.join')
    def test_create_execute_thread(self, join_mock, start_mock):
        self.execution._ExecutionEngine__temp_task_list = [self.task]
        self.execution._ExecutionEngine__temp_host_list = [self.deploy_host]
        self.execution.current_thread_count = 1
        self.execution.max_thread_count = 2
        self.execution.create_execute_thread()
        self.assertEqual(self.task.get_state(), 'Executing')
        self.assertEqual(self.deploy_host.state, 'Busy')
        start_mock.assert_called_once()
        join_mock.assert_called_once()

    @patch('Framework_Kernel.execution_engine.ExecutionEngine._ExecutionEngine__fresh_temp_host_list')
    @patch('Framework_Kernel.execution_engine.ExecutionEngine._ExecutionEngine__fresh_temp_task_list')
    @patch('threading.Thread.start')
    @patch('threading.Thread.join')
    def test_create_execute_thread_none_task_node(self, join_mock, start_mock, task_mock, host_mock):
        task_mock.return_value = self.execution._ExecutionEngine__temp_task_list.append(self.task)
        host_mock.return_value = self.execution._ExecutionEngine__temp_host_list.append(self.deploy_host)
        self.execution.current_thread_count = 1
        self.execution.max_thread_count = 2
        self.execution.create_execute_thread()
        self.assertEqual(self.task.get_state(), 'Executing')
        self.assertEqual(self.deploy_host.state, 'Busy')
        start_mock.assert_called_once()
        join_mock.assert_called_once()

    def modify_current_thread_count(self):
        time.sleep(0.1)
        self.execution.current_thread_count = 2

    @patch('threading.Thread.join')
    def test_create_execute_thread_equal_thread(self, join_mock):
        self.execution._ExecutionEngine__temp_task_list = [self.task]
        self.execution._ExecutionEngine__temp_host_list = [self.deploy_host]
        self.execution.current_thread_count = 3
        self.execution.max_thread_count = 3
        p = threading.Thread(target=self.modify_current_thread_count)
        p.daemon = False
        p.start()
        with patch('time.sleep') as sleep_mock:
            with patch('threading.Thread.start') as start_mock:
                self.execution.create_execute_thread()
                sleep_mock.assert_called_with(self.execution.loop_interval)
                start_mock.assert_called_once()
                join_mock.assert_called_once()

    @patch('threading.Thread.join')
    def test_create_execute_thread_more_than_max_thread(self, join_mock):
        self.execution._ExecutionEngine__temp_task_list = [self.task]
        self.execution._ExecutionEngine__temp_host_list = [self.deploy_host]
        self.execution.current_thread_count = 4
        self.execution.max_thread_count = 3
        p = threading.Thread(target=self.modify_current_thread_count)
        p.daemon = False
        p.start()
        with patch('time.sleep') as sleep_mock:
            with patch('threading.Thread.start') as start_mock:
                self.execution.create_execute_thread()
                sleep_mock.assert_called_with(self.execution.loop_interval)
                start_mock.assert_called_once()
                join_mock.assert_called_once()

    @patch('Framework_Kernel.task.Task.set_state')
    @patch('threading.Thread.start')
    @patch('threading.Thread.join')
    def test_create_execute_thread_except(self, join_mock, start_mock, state_mock):
        join_mock.side_effect = [EOFError, None]
        self.execution._ExecutionEngine__temp_task_list = [self.task]
        self.execution._ExecutionEngine__temp_host_list = [self.deploy_host]
        self.execution.current_thread_count = 1
        self.execution.max_thread_count = 2
        self.execution.create_execute_thread()
        self.assertEqual(start_mock.call_count, 2)
        self.assertEqual(join_mock.call_count, 2)
        self.assertEqual(state_mock.call_count, 3)
        self.assertEqual(self.execution.current_thread_count, 2)

    @patch('Framework_Kernel.task.Task.collect_result')
    @patch('Framework_Kernel.task.Task.execute')
    @patch('Framework_Kernel.task.Task.deploy')
    def test_deploy(self, deploy_mock, execute_mock, collect_mock):
        self.execution.deploy(self.deploy_host, self.task)
        deploy_mock.assert_called_once_with(self.deploy_host)
        execute_mock.assert_called_once_with(self.deploy_host)
        collect_mock.assert_called_once_with(self.deploy_host)

    @patch('Framework_Kernel.task_queue.Queue.get_task_list')
    @patch('time.sleep')
    def test_fresh_temp_task_list(self, sleep_mock, task_list_mock):
        task = Task(name='Test')
        task.set_state('Assemble')
        self.task.set_state('Assemble Finished')
        task_list_mock.side_effect = [[], [task], [self.task]]
        self.execution._ExecutionEngine__fresh_temp_task_list()
        self.assertEqual(sleep_mock.call_count, 2)
        self.assertIn(self.task, self.execution._ExecutionEngine__temp_task_list)

    def refresh_deploy_list(self):
        time.sleep(0.1)
        self.deploy_host.state = 'Idle'
        self.deploy_list.append(self.deploy_host)

    def test_fresh_temp_host_list(self):
        p = threading.Thread(target=self.refresh_deploy_list)
        p.daemon = False
        p.start()
        with patch('time.sleep') as sleep_mock:
            self.execution._ExecutionEngine__fresh_temp_host_list()
            self.assertIn(self.deploy_host, self.execution._ExecutionEngine__temp_host_list)
            sleep_mock.assert_called_with(self.execution.loop_interval)

    def refresh_deploy_list_state(self):
        time.sleep(0.1)
        self.deploy_host.state = 'Idle'

    def test_fresh_temp_host_list_state(self):
        self.deploy_host.state = 'Busy'
        self.deploy_list.append(self.deploy_host)
        p = threading.Thread(target=self.refresh_deploy_list_state)
        p.daemon = False
        p.start()
        with patch('time.sleep') as sleep_mock:
            self.execution._ExecutionEngine__fresh_temp_host_list()
            self.assertIn(self.deploy_host, self.execution._ExecutionEngine__temp_host_list)
            sleep_mock.assert_called_with(self.execution.loop_interval)

    def test_download_result(self):
        pass

    def test_email_parameter(self):
        pass

    @patch('multiprocessing.Process.start')
    def test_start(self, start_mock):
        self.execution.start()
        start_mock.assert_called_once()

    @patch('multiprocessing.Process.start')
    @patch('multiprocessing.Process.terminate')
    def test_stop(self, stop_mock, start_mock):
        self.execution.start()
        self.execution.stop()
        stop_mock.assert_called_once()
