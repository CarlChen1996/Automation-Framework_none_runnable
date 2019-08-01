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
test_1_scan_folder: scan test_plan folder
test_2_get_task_when_task_exist: get task from test_plan when task exist
test_3_get_task_when_task_not_exist: time.sleep was called when task not exist
test_4_send_task_to_execution: sen task to execution engine by pipe
test_5_get_ack_right_from_execution_engine: get right ack to remove task
test_6_get_ack_wrong_from_execution_engine: get wrong ack will do nothing
test_7_remove_task_from_assemble_queue: remove task from assemble queue after get right ack
test_8_initial_task: initial_task after task has been load
test_9_add_task_to_assemble_queue: add task to assemble queue after initial task
'''


class AssembleEngineTest(unittest.TestCase):
    def setUp(self):
        self.pipe = Pipe()
        self.build_list = []
        self.assemble = assemble_engine.AssembleEngine(self.pipe[0], self.build_list)
        self.task_name = 'task_1'
        self.task = Task(name=self.task_name)
        self.excel_name = '.\\Configuration\\test_plan\\TEST_PLAN_unittest.xlsx'
        self.loaded_excel = '.\\Configuration\\test_plan\\Loaded_TEST_PLAN_unittest.xlsx'

    def scan_folder(self):
        excel_list = []
        for i in self.assemble.scan_folder():
            excel_list.append(i.split('\\')[-1])
        return excel_list

    def test_1_scan_folder(self):
        if os.path.exists(self.loaded_excel):
            os.rename(self.loaded_excel, self.excel_name)
            self.assertIn(os.path.basename(self.excel_name), self.scan_folder())
            os.rename(self.excel_name, self.loaded_excel)
        else:
            self.assertIn(os.path.basename(self.loaded_excel), self.scan_folder())

    @patch('Framework_Kernel.assemble_engine.AssembleEngine.generate_task')
    def test_2_get_task_when_task_exist(self, generate_task):
        file_list = ['1']
        self.assemble.get_task_from_folder(file_list)
        generate_task.assert_called_once_with(file_list)

    @patch('time.sleep')
    @patch('Framework_Kernel.assemble_engine.AssembleEngine.generate_task')
    def test_3_get_task_when_task_not_exist(self, generate_task, sleep_mock):
        file_list = []
        self.assemble.get_task_from_folder(file_list)
        generate_task.assert_not_called()
        sleep_mock.assert_called_once()

    @patch('Framework_Kernel.assemble_engine.AssembleEngine.get_signal_after_send')
    def test_4_send_task_to_execution(self, send_task):
        self.task.set_state("ASSEMBLE FINISHED")
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assemble.send_task_to_execution()
        send_task.assert_called_once_with(self.task)
        receive_task = self.pipe[1].recv()
        self.assertEqual(receive_task.get_name(), self.task_name)

    @patch('Framework_Kernel.queue_task.Queue.remove_task')
    def test_5_get_ack_right_from_execution_engine(self, remove):
        self.pipe[1].send(self.task_name)
        self.assemble.get_signal_after_send(self.task)
        remove.assert_called_once_with(self.task)

    @patch('Framework_Kernel.queue_task.Queue.remove_task')
    def test_6_get_ack_wrong_from_execution_engine(self, remove):
        self.pipe[1].send(self.task)
        self.assemble.get_signal_after_send(self.task)
        remove.assert_not_called()

    def test_7_remove_task_from_assemble_queue(self):
        self.task.set_state("ASSEMBLE FINISHED")
        self.assemble.assembleQueue.insert_task(task=self.task)
        self.assertIn(self.task, self.assemble.assembleQueue.get_task_list())
        self.pipe[1].send(self.task_name)
        self.assemble.get_signal_after_send(self.task)
        self.assertNotIn(self.task, self.assemble.assembleQueue.get_task_list())

    @patch('Framework_Kernel.task.Task.set_state')
    @patch('Framework_Kernel.queue_task.Queue.insert_task')
    def test_8_initial_task(self, insert_task, set_state):
        if os.path.exists('.\\Configuration\\test_plan\\Loaded_TEST_PLAN_unittest.xlsx'):
            os.rename('.\\Configuration\\test_plan\\Loaded_TEST_PLAN_unittest.xlsx',
                      '.\\Configuration\\test_plan\\TEST_PLAN_unittest.xlsx')
        file_list = [".\\Configuration\\test_plan\\TEST_PLAN_unittest.xlsx"]
        self.assemble.generate_task(file_list)
        set_state.assert_called_once()
        insert_task.assert_called_once()

    def test_9_add_task_to_assemble_queue(self):
        if os.path.exists('.\\Configuration\\test_plan\\Loaded_TEST_PLAN_unittest.xlsx'):
            os.rename('.\\Configuration\\test_plan\\Loaded_TEST_PLAN_unittest.xlsx',
                      '.\\Configuration\\test_plan\\TEST_PLAN_unittest.xlsx')
        file_list = [".\\Configuration\\test_plan\\TEST_PLAN_unittest.xlsx"]
        self.assemble.generate_task(file_list)
        self.assertEqual(self.assemble.assembleQueue.get_task_list()[0].get_name(), self.task_name)
