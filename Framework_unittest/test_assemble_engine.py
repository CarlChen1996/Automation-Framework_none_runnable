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
test_send_task_to_execution_false: remove task while task was assembled fail
test_get_ack_right_from_execution_engine: get right ack to remove task
test_get_ack_wrong_from_execution_engine: get wrong ack will do nothing
test_remove_task_from_assemble_queue: remove task from assemble queue after get right ack
test_initial_task: initial_task after task has been load
test_add_task_to_assemble_queue: add task to assemble queue after initial task
test_send_task_to_execution_true
'''


class AssembleEngineTest(unittest.TestCase):
    def setUp(self):
        self.pipe = Pipe()
        self.build_list = []
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
            self.assertIn(os.path.basename(self.loaded_excel), self.scan_folder())

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
    @patch('Common_Library.email_operator.Email.send_email')
    @patch('Framework_Kernel.task_queue.Queue.remove_task')
    def test_send_task_to_execution_false(self, remove_task, email_mock, sleep_mock):
        self.task.set_status('SUCCES')
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assemble.send_task_to_execution()
        remove_task.assert_called_once_with(self.task)

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

    @patch('time.sleep')
    @patch('Framework_Kernel.task.Task.set_state')
    @patch('Framework_Kernel.task_queue.Queue.insert_task')
    def test_initial_task(self, insert_task, set_state, sleep_mock):
        self.assemble.generate_task(self.generate_excel_list())
        set_state.assert_called_once()
        insert_task.assert_called_once()

    def test_add_task_to_assemble_queue(self):
        self.assemble.generate_task(self.generate_excel_list())
        self.assertEqual(self.assemble.assembleQueue.get_task_list()[0].get_name(), self.task_name)
