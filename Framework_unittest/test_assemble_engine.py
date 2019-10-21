# -*- coding: utf-8 -*-
# @Time    : 7/31/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_assemble_engine.py
# @Project : Automation-Framework
from Framework_Kernel import assemble_engine
from Framework_Kernel.task import Task
from multiprocessing import Pipe
from unittest.mock import patch, call, Mock
from Framework_Kernel.host import WindowsBuildHost, LinuxBuildHost, WindowsExecuteHost, LinuxExecuteHost
import unittest
import os
import time
import threading

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
        self.task = Task(name=self.task_name, email=['jie.liu1@hp.com'])
        self.excel_name = '.\\Test_Plan\\TEST_PLAN_unittest.xlsx'
        self.loaded_excel = '.\\Test_Plan\\Loaded_TEST_PLAN_unittest.xlsx'
        self.uut_windows = WindowsExecuteHost(ip='1.1.1.1', mac=666666, version='wes')
        self.uut_linux = LinuxExecuteHost(ip='1.1.1.1', mac=666666, version='tp')

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
        error_handle_mock.assert_called_once_with(task=self.task, state='unknown', mail_receiver=self.task.get_email())

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

    @patch('Common_Library.email_operator.Email._Email__init_connection')
    @patch('Common_Library.email_operator.Email.send_email')
    @patch('Framework_Kernel.task_queue.Queue.remove_task')
    def test_get_ack_wrong_from_execution_engine(self, remove, email_mock, connect_mock):
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

    @patch('Framework_Kernel.validator.HostValidator.validate_uut')
    @patch('Framework_Kernel.validator.ScriptValidator.validate')
    def test_validate_task_true(self, script_mock, uut_mock):
        self.task.insert_uut_list(self.uut_windows)
        uut_mock.return_value = True
        script_mock.return_value = True
        self.assertTrue(self.assemble.validate_task(self.task))

    @patch('Common_Library.email_operator.Email._Email__init_connection')
    @patch('Common_Library.email_operator.Email.send_email')
    @patch('Framework_Kernel.validator.HostValidator.validate_uut')
    @patch('Framework_Kernel.validator.ScriptValidator.validate')
    def test_validate_task_false(self, script_mock, uut_mock, email_mock, connect_mock):
        self.task.insert_uut_list(self.uut_windows)
        script_mock.return_value = False
        self.assertFalse(self.assemble.validate_task(self.task))
        uut_mock.assert_not_called()
        script_mock.return_value = True
        uut_mock.return_value = False
        self.assertFalse(self.assemble.validate_task(self.task))
        uut_mock.assert_called_once_with(self.uut_windows)

    def test_get_os_type_windows(self):
        self.task.insert_uut_list(self.uut_windows)
        self.assertEqual(self.assemble.get_os_type(self.task), 'win')

    def test_get_os_type_linux(self):
        self.task.insert_uut_list(self.uut_linux)
        self.assertEqual(self.assemble.get_os_type(self.task), 'linux')

    def test_get_os_type_none(self):
        self.task.insert_uut_list(WindowsExecuteHost(ip='1.1.1.1', mac=666666, version='wt'))
        self.assertEqual(self.assemble.get_os_type(self.task), '')

    @patch('time.sleep')
    @patch('Framework_Kernel.task_queue.Queue.get_task_list')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine.get_os_type')
    def test_refresh_temp_task_list(self, os_mock, task_queue_mock, sleep_mock):
        self.task.set_state('WAIT ASSEMBLE')
        task_queue_mock.side_effect = [[], [self.task]]
        os_mock.return_value = 'win'
        os = 'win'
        temp_task_list = []
        self.assertIn(self.task, self.assemble._AssembleEngine__refresh_temp_task_list(os, temp_task_list))
        sleep_mock.assert_called_once_with(self.assemble.loop_interval)
        self.assertEqual(task_queue_mock.call_count, 2)

    @patch('time.sleep')
    @patch('Framework_Kernel.task_queue.Queue.get_task_list')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine.get_os_type')
    def test_refresh_temp_task_list_false_task(self, os_mock, task_queue_mock, sleep_mock):
        task = Task(name='test')
        task.set_state('wait')
        self.task.set_state('WAIT ASSEMBLE')
        task_queue_mock.side_effect = [[task], [self.task]]
        os_mock.return_value = 'win'
        os = 'win'
        temp_task_list = []
        self.assertIn(self.task, self.assemble._AssembleEngine__refresh_temp_task_list(os, temp_task_list))
        sleep_mock.assert_called_once_with(self.assemble.loop_interval)
        self.assertEqual(task_queue_mock.call_count, 2)

    @patch('time.sleep')
    @patch('Framework_Kernel.task_queue.Queue.get_task_list')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine.get_os_type')
    def test_refresh_temp_task_list_false_os(self, os_mock, task_queue_mock, sleep_mock):
        self.task.set_state('WAIT ASSEMBLE')
        task_queue_mock.side_effect = [[self.task], [self.task]]
        os_mock.side_effect = ['linux', 'win']
        os = 'win'
        temp_task_list = []
        self.assertIn(self.task, self.assemble._AssembleEngine__refresh_temp_task_list(os, temp_task_list))
        sleep_mock.assert_called_once_with(self.assemble.loop_interval)
        self.assertEqual(task_queue_mock.call_count, 2)

    @staticmethod
    def refresh_node_list(build_node_list, build_host):
        time.sleep(0.1)
        build_node_list.append(build_host)

    def test_refresh_node_task_list(self):
        self.linux_build_host.state = 'Idle'
        self.assemble._AssembleEngine__build_node_list = []
        p = threading.Thread(target=self.refresh_node_list,
                             args=(self.assemble._AssembleEngine__build_node_list, self.linux_build_host))
        p.daemon = False
        p.start()
        temp_node_list = []
        build_node_type = LinuxBuildHost
        with patch('time.sleep') as time_mock:
            self.assertIn(self.linux_build_host,
                          self.assemble._AssembleEngine__refresh_temp_node_list(temp_node_list, build_node_type))
            time_mock.assert_called_with(self.assemble.loop_interval)

    def set_host_state(self):
        time.sleep(0.1)
        self.linux_build_host.state = 'Idle'

    def test_refresh_node_task_list_false_host_state(self):
        self.linux_build_host.state = 'Busy'
        self.assemble._AssembleEngine__build_node_list = [self.linux_build_host]
        p = threading.Thread(target=self.set_host_state)
        p.daemon = False
        p.start()
        temp_node_list = []
        build_node_type = LinuxBuildHost
        with patch('time.sleep') as time_mock:
            self.assertIn(self.linux_build_host,
                          self.assemble._AssembleEngine__refresh_temp_node_list(temp_node_list, build_node_type))
            time_mock.assert_called_with(self.assemble.loop_interval)

    def set_host_type(self):
        time.sleep(0.1)
        self.assemble._AssembleEngine__build_node_list = [self.linux_build_host]

    def test_refresh_node_task_list_false_host_type(self):
        self.linux_build_host.state = 'Idle'
        self.windows_build_host.state = 'Idle'
        self.assemble._AssembleEngine__build_node_list = [self.windows_build_host]
        p = threading.Thread(target=self.set_host_type)
        p.daemon = False
        p.start()
        temp_node_list = []
        build_node_type = LinuxBuildHost
        with patch('time.sleep') as time_mock:
            self.assertIn(self.linux_build_host,
                          self.assemble._AssembleEngine__refresh_temp_node_list(temp_node_list, build_node_type))
            time_mock.assert_called_with(self.assemble.loop_interval)

    @patch('time.sleep')
    @patch('threading.Thread.start')
    @patch('threading.Thread.join')
    def test_create_build_thread(self, join_mock, start_mock, sleep_mock):
        os = 'win'
        build_node_type = WindowsBuildHost
        temp_task_list = [self.task]
        temp_node_list = [self.windows_build_host]
        self.assemble.current_thread_count_win = 1
        max_thread = 2
        self.assemble.create_build_thread(os, build_node_type, temp_task_list, temp_node_list, max_thread)
        start_mock.assert_called_once()
        join_mock.assert_called_once()
        self.assertEqual(self.task.get_state(), 'ASSEMBLING')
        self.assertEqual(self.windows_build_host.state, 'Busy')
        self.assertEqual(self.assemble.current_thread_count_win, 2)

    def modify_current_thread_count(self):
        time.sleep(0.1)
        self.assemble.current_thread_count_win = 2

    @patch('threading.Thread.join')
    def test_create_build_thread_equal_thread(self, join_mock):
        os = 'win'
        build_node_type = WindowsBuildHost
        temp_task_list = [self.task]
        temp_node_list = [self.windows_build_host]
        self.assemble.current_thread_count_win = 4
        max_thread = 4
        p = threading.Thread(target=self.modify_current_thread_count)
        p.daemon = False
        p.start()
        with patch('time.sleep') as sleep_mock:
            with patch('threading.Thread.start') as start_mock:
                self.assemble.create_build_thread(os, build_node_type, temp_task_list, temp_node_list, max_thread)
                sleep_mock.assert_called_with(self.assemble.loop_interval)
        start_mock.assert_called_once()
        join_mock.assert_called_once()
        self.assertEqual(self.assemble.current_thread_count_win, 3)

    @patch('threading.Thread.join')
    def test_create_build_thread_more_than_max_thread(self, join_mock):
        os = 'win'
        build_node_type = WindowsBuildHost
        temp_task_list = [self.task]
        temp_node_list = [self.windows_build_host]
        self.assemble.current_thread_count_win = 5
        max_thread = 4
        p = threading.Thread(target=self.modify_current_thread_count)
        p.daemon = False
        p.start()
        with patch('time.sleep') as sleep_mock:
            with patch('threading.Thread.start') as start_mock:
                self.assemble.create_build_thread(os, build_node_type, temp_task_list, temp_node_list, max_thread)
                sleep_mock.assert_called_with(self.assemble.loop_interval)
        start_mock.assert_called_once()
        join_mock.assert_called_once()
        self.assertEqual(self.assemble.current_thread_count_win, 3)

    @patch('time.sleep')
    @patch('threading.Thread.start')
    @patch('threading.Thread.join')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine._AssembleEngine__refresh_temp_task_list')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine._AssembleEngine__refresh_temp_node_list')
    def test_create_build_thread_none_task_node(self, node_mock, task_mock, join_mock, start_mock, sleep_mock):
        node_mock.return_value = [self.windows_build_host]
        task_mock.return_value = [self.task]
        os = 'win'
        build_node_type = WindowsBuildHost
        temp_task_list = []
        temp_node_list = []
        self.assemble.current_thread_count_win = 1
        max_thread = 2
        self.assemble.create_build_thread(os, build_node_type, temp_task_list, temp_node_list, max_thread)
        task_mock.assert_called_once_with(os, temp_task_list)
        node_mock.assert_called_once_with(temp_node_list, build_node_type)
        start_mock.assert_called_once()
        join_mock.assert_called_once()
        self.assertEqual(self.assemble.current_thread_count_win, 2)

    @patch('Framework_Kernel.task.Task.set_state')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine._AssembleEngine__refresh_temp_task_list')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine._AssembleEngine__refresh_temp_node_list')
    @patch('time.sleep')
    @patch('threading.Thread.start')
    @patch('threading.Thread.join')
    def test_create_build_thread_except(self, join_mock, start_mock, sleep_mock, node_mock, task_mock, state_mock):
        node_mock.return_value = [self.windows_build_host]
        task_mock.return_value = [self.task]
        join_mock.side_effect = [EOFError, None]
        os = 'win'
        build_node_type = WindowsBuildHost
        temp_task_list = [self.task]
        temp_node_list = [self.windows_build_host]
        self.assemble.current_thread_count_win = 1
        max_thread = 2
        self.assemble.create_build_thread(os, build_node_type, temp_task_list, temp_node_list, max_thread)
        self.assertEqual(start_mock.call_count, 2)
        self.assertEqual(join_mock.call_count, 2)
        self.assertEqual(state_mock.call_count, 3)
        self.assertEqual(self.assemble.current_thread_count_win, 2)

    def test_build_win(self):
        task = Mock(spec=Task)
        node = Mock(spec=WindowsBuildHost)
        os = 'win'
        current_thread_count_win = 2
        self.assemble.current_thread_count_win = current_thread_count_win
        self.assemble.build(task, node, os)
        task_mock_list = [call.get_name(), call.build(node), call.get_status(), call.get_exe_file_list(),
                          call.get_name(), call.set_state('Assemble Finished')]
        node_mock_list = [call.get_hostname(), call.get_hostname()]
        self.assertEqual(task.mock_calls, task_mock_list)
        self.assertEqual(node.mock_calls, node_mock_list)
        self.assertEqual(self.assemble.current_thread_count_win, current_thread_count_win - 1)

    def test_build_linux(self):
        task = Mock(spec=Task)
        node = Mock(spec=LinuxBuildHost)
        os = 'linux'
        current_thread_count_linux = 2
        self.assemble.current_thread_count_linux = current_thread_count_linux
        self.assemble.build(task, node, os)
        task_mock_list = [call.get_name(), call.build(node), call.get_status(), call.get_exe_file_list(),
                          call.get_name(), call.set_state('Assemble Finished')]
        node_mock_list = [call.get_hostname(), call.get_hostname()]
        self.assertEqual(task.mock_calls, task_mock_list)
        self.assertEqual(node.mock_calls, node_mock_list)
        self.assertEqual(self.assemble.current_thread_count_linux, current_thread_count_linux - 1)

    @patch('Framework_Kernel.task.Task.build')
    def test_build_except_win(self, build_mock):
        build_mock.side_effect = AttributeError
        current_thread_count_win = 2
        os = 'win'
        self.assemble.current_thread_count_win = current_thread_count_win
        self.assemble.build(self.task, self.windows_build_host, os)
        self.assertEqual(self.task.get_state(), 'WAIT ASSEMBLE')
        self.assertEqual(self.windows_build_host.state, 'Idle')
        self.assertEqual(self.assemble.current_thread_count_win, current_thread_count_win - 1)

    @patch('Framework_Kernel.task.Task.build')
    def test_build_except_linux(self, build_mock):
        build_mock.side_effect = AttributeError
        current_thread_count_linux = 2
        os = 'linux'
        self.assemble.current_thread_count_linux = current_thread_count_linux
        self.assemble.build(self.task, self.linux_build_host, os)
        self.assertEqual(self.task.get_state(), 'WAIT ASSEMBLE')
        self.assertEqual(self.linux_build_host.state, 'Idle')
        self.assertEqual(self.assemble.current_thread_count_linux, current_thread_count_linux - 1)

    def test_load_config(self):
        pass

    @patch('multiprocessing.Process.start')
    def test_start(self, start_mock):
        self.assemble.start()
        start_mock.assert_called_once()

    @patch('multiprocessing.Process.start')
    @patch('multiprocessing.Process.terminate')
    def test_stop(self, stop_mock, start_mock):
        self.assemble.start()
        self.assemble.stop()
        stop_mock.assert_called_once()

    def test_get_current(self):
        self.assemble.current_thread_count_win = 0
        self.assemble.current_thread_count_linux = 0
        self.assertEqual(self.assemble.get_current('win'), 0)
        self.assertEqual(self.assemble.get_current('win', 1), 1)
        self.assertEqual(self.assemble.get_current('linux'), 0)
        self.assertEqual(self.assemble.get_current('linux', 1), 1)
