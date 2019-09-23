# -*- coding: utf-8 -*-
# @Time    : 7/31/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_assemble_engine.py
# @Project : Automation-Framework
from Framework_Kernel import assemble_engine
from Framework_Kernel.task import Task
from multiprocessing import Pipe
from unittest.mock import patch
from Framework_Kernel.host import WindowsBuildHost, LinuxBuildHost, WindowsExecuteHost, LinuxExecuteHost
import unittest
import os

'''
setUp: Instantiated pipe, instantiated Assemble Engine
scan_folder: call assemble_engine to scan folder
generate_excel_list: generate excel list to called
test_scan_folder: scan Test_Plan folder
test_get_task_when_task_exist: get task from Test_Plan when task exist
test_get_task_when_task_not_exist: time.sleep was called when task not exist
test_send_task_to_execution_true: send task to execution engine by pipe while task was assembled finish
test_send_task_to_execution_false: test for task does not build success
test_send_task_to_execution_unfinished: test for task build success, but state was not set 'ASSEMBLE FINISHED'
test_get_ack_right_from_execution_engine: get right ack to remove task
test_get_ack_wrong_from_execution_engine: get wrong ack will do nothing
test_remove_task_from_assemble_queue: remove task from assemble queue after get right ack
test_generate_task: initial_task after task has been load
test_add_task_to_assemble_queue: add task to assemble queue after initial task
test_validate_task_true: test validate_task can return True after validate scripts True
test_validate_task_false: test validate_task can return False after validate scripts False
'''


class AssembleEngineTest(unittest.TestCase):
    def setUp(self):
        self.pipe = Pipe()
        self.windows_build_host = WindowsBuildHost(ip='1.1.1.1', mac=666666)
        self.linux_build_host = LinuxBuildHost(ip='1.1.1.1', mac=666666)
        self.build_list = [self.windows_build_host, self.linux_build_host]
        self.assemble = assemble_engine.AssembleEngine(self.pipe[0], self.build_list)
        self.task_name = 'task_1'
        self.task = Task(name=self.task_name)
        self.excel_name = '.\\Test_Plan\\TEST_PLAN_unittest.xlsx'
        self.loaded_excel = '.\\Test_Plan\\Loaded_TEST_PLAN_unittest.xlsx'

    def scan_folder(self):
        excel_list = []
        for i in self.assemble.scan_folder():
            excel_list.append(i.split('\\')[-1])
        return excel_list

    def generate_excel_list(self):
        if os.path.exists(self.loaded_excel):
            os.rename(self.loaded_excel, self.excel_name)
        file_list = [self.excel_name]
        return file_list

    def test_scan_folder(self):
        if os.path.exists(self.loaded_excel):
            os.rename(self.loaded_excel, self.excel_name)
            self.assertIn(os.path.basename(self.excel_name), self.scan_folder())
            os.rename(self.excel_name, self.loaded_excel)
        else:
            self.assertIn(os.path.basename(self.excel_name), self.scan_folder())

    @patch('Framework_Kernel.assemble_engine.AssembleEngine.generate_task')
    def test_get_task_when_task_exist(self, generate_task):
        file_list = ['1']
        self.assemble.get_task_from_folder(file_list)
        generate_task.assert_called_once_with(file_list)

    @patch('time.sleep')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine.generate_task')
    def test_get_task_when_task_not_exist(self, generate_task, sleep_mock):
        file_list = []
        self.assemble.get_task_from_folder(file_list)
        generate_task.assert_not_called()
        sleep_mock.assert_called_once()

    @patch('time.sleep')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine.get_signal_after_send')
    def test_send_task_to_execution_true(self, send_task, sleep_mock):
        self.task.set_status('SUCCESS')
        self.task.set_state("ASSEMBLE FINISHED")
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assemble.send_task_to_execution()
        send_task.assert_called_once_with(self.task)
        receive_task = self.pipe[1].recv()
        self.assertEqual(receive_task.get_name(), self.task_name)

    @patch('time.sleep')
    @patch('Framework_Kernel.error_handler.ErrorHandler.handle')
    def test_send_task_to_execution_false(self, error_handle_mock, sleep_mock):
        self.task.set_status('SUCCES')
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assemble.send_task_to_execution()
        error_handle_mock.assert_called_once_with(task=self.task, task_queue=self.assemble.assembleQueue)

    @patch('time.sleep')
    def test_send_task_to_execution_unfinished(self, sleep_mock):
        self.task.set_status('SUCCESS')
        self.task.set_state('ASSEMBLE')
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assemble.send_task_to_execution()
        self.assertEqual(sleep_mock.call_count, 2)

    @patch('Framework_Kernel.task_queue.Queue.remove_task')
    def test_get_ack_right_from_execution_engine(self, remove):
        self.pipe[1].send(self.task_name)
        self.assemble.get_signal_after_send(self.task)
        remove.assert_called_once_with(self.task)

    @patch('Framework_Kernel.task_queue.Queue.remove_task')
    def test_get_ack_wrong_from_execution_engine(self, remove):
        self.pipe[1].send(self.task)
        self.assemble.get_signal_after_send(self.task)
        remove.assert_not_called()

    def test_remove_task_from_assemble_queue(self):
        self.task.set_state("ASSEMBLE FINISHED")
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assertIn(self.task, self.assemble.assembleQueue.get_task_list())
        self.pipe[1].send(self.task_name)
        self.assemble.get_signal_after_send(self.task)
        self.assertNotIn(self.task, self.assemble.assembleQueue.get_task_list())

    @patch('Framework_Kernel.assemble_engine.AssembleEngine.validate_task')
    @patch('time.sleep')
    @patch('Framework_Kernel.task.Task.set_state')
    @patch('Framework_Kernel.task_queue.Queue.insert_task')
    def test_generate_task(self, insert_task, set_state, sleep_mock, validate_mock):
        validate_mock.return_value = True
        self.assemble.generate_task(self.generate_excel_list())
        set_state.assert_called_once()
        insert_task.assert_called_once()

    @patch('Framework_Kernel.assemble_engine.AssembleEngine.validate_task')
    @patch('time.sleep')
    def test_add_task_to_assemble_queue(self, sleep_mock, validate_mock):
        validate_mock.return_value = True
        self.assemble.generate_task(self.generate_excel_list())
        self.assertEqual(self.assemble.assembleQueue.get_task_list()[0].get_name(), self.task_name)

    @patch('Framework_Kernel.validator.ScriptValidator.validate')
    def test_validate_task_true(self, validate_mock):
        validate_mock.return_value = True
        self.assertTrue(self.assemble.validate_task(self.task))

    @patch('Framework_Kernel.validator.ScriptValidator.validate')
    def test_validate_task_false(self, validate_mock):
        validate_mock.return_value = False
        self.assertFalse(self.assemble.validate_task(self.task))

    def test_get_os_type_windows(self):
        self.task.insert_uut_list(WindowsExecuteHost(ip='1.1.1.1', mac=666666, version='wes'))
        self.assertEqual(self.assemble.get_os_type(self.task), 'win')

    def test_get_os_type_linux(self):
        self.task.insert_uut_list(WindowsExecuteHost(ip='1.1.1.1', mac=666666, version='tp'))
        self.assertEqual(self.assemble.get_os_type(self.task), 'linux')

    def test_get_os_type_none(self):
        self.task.insert_uut_list(WindowsExecuteHost(ip='1.1.1.1', mac=666666, version='wt'))
        self.assertEqual(self.assemble.get_os_type(self.task), '')

    @patch('Framework_Kernel.assemble_engine.AssembleEngine.get_os_type')
    def test_create_temp_task(self, os_mock):
        os_mock.return_value = 'win'
        self.task.set_state('WAIT ASSEMBLE')
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assertEqual([self.task], self.assemble.create_temp_task(os_mock.return_value))

    @patch('Framework_Kernel.assemble_engine.AssembleEngine.get_os_type')
    def test_create_temp_task_none_os(self, os_mock):
        os_mock.return_value = ''
        self.task.set_state('WAIT ASSEMBLE')
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assertEqual([], self.assemble.create_temp_task('win'))

    @patch('Framework_Kernel.assemble_engine.AssembleEngine.get_os_type')
    def test_create_temp_task_none_task(self, os_mock):
        self.task.set_state('ASSEMBLING')
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assertEqual([], self.assemble.create_temp_task('win'))
        os_mock.assert_not_called()

    def test_create_temp_node_windows(self):
        self.assertEqual(self.assemble.create_temp_node('win'), [self.windows_build_host])

    def test_create_temp_node_linux(self):
        self.assertEqual(self.assemble.create_temp_node('linux'), [self.linux_build_host])

    def test_create_temp_node_windows_busy(self):
        self.assemble._AssembleEngine__build_list = []
        self.assertEqual(self.assemble.create_temp_node('win'), [])
        self.windows_build_host.state = 'Busy'
        self.assemble._AssembleEngine__build_list = [self.windows_build_host]
        self.assertEqual(self.assemble.create_temp_node('win'), [])
        self.linux_build_host.state = 'Busy'
        self.assemble._AssembleEngine__build_list = [self.linux_build_host]
        self.assertEqual(self.assemble.create_temp_node('linux'), [])
