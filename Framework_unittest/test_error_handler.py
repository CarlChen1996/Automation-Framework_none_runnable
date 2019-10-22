# -*- coding: utf-8 -*-
# @Time    : 21/10/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_error_handle.py
# @Project : Automation-Framework

from Framework_Kernel import error_handler, task, task_queue
from unittest.mock import patch
import unittest
from multiprocessing import Process
import time
from Common_Library import email_operator


class ErrorHandle(unittest.TestCase):
    def setUp(self):
        self.engine_code = error_handler.EngineCode()
        self.error_level = error_handler.ErrorLevel()
        self.msg = 'unittest'
        self.level = '00'
        self.engine = '01'
        self.error_msg = error_handler.ErrorMsg(self.engine, self.level, self.msg)
        self.error_handler = error_handler.ErrorHandler(self.error_msg)
        self.mail_receiver = ['email']
        self.task = task.Task(name='test')
        self.task_queue = task_queue.Queue()

    def test_get_engine_name(self):
        self.assertEqual(self.engine_code.get_engine_name('00'), 'controller')
        self.assertEqual(self.engine_code.get_engine_name('01'), 'config_engine')
        self.assertEqual(self.engine_code.get_engine_name('02'), 'assembly_engine')
        self.assertEqual(self.engine_code.get_engine_name('03'), 'execute_engine')
        self.assertEqual(self.engine_code.get_engine_name('04'), 'report')
        self.assertEqual(self.engine_code.get_engine_name('05'), 'unknown engine_code')

    def test_get_error_level(self):
        self.assertEqual(self.error_level.get_error_level('00'), 'terminate_framework')
        self.assertEqual(self.error_level.get_error_level('01'), 'reset_framework')
        self.assertEqual(self.error_level.get_error_level('02'), 'reset_engine')
        self.assertEqual(self.error_level.get_error_level('03'), 'drop_task')
        self.assertEqual(self.error_level.get_error_level('04'), 'rerun_task')
        self.assertEqual(self.error_level.get_error_level('05'), 'mark_task')
        self.assertEqual(self.error_level.get_error_level('06'), 'record_and_continue')
        self.assertEqual(self.error_level.get_error_level('07'), 'unknown level code')

    def test_create_error_msg(self):
        self.assertEqual(self.error_msg.create_error_msg(), '{}{}{}'.format(self.engine, self.level, self.msg))
        self.assertEqual(self.error_msg.error_msg, self.error_msg.create_error_msg())

    @patch('Framework_Kernel.error_handler.ErrorLevel.get_error_level')
    @patch('Framework_Kernel.error_handler.EngineCode.get_engine_name')
    def test_create_error_msg_full(self, engine_mock, level_mock):
        level_mock.return_value = 'terminate_framework'
        engine_mock.return_value = 'controller'
        # level = 00, engine = 01 terminate_framework , config_engine assertNotEqual
        self.assertEqual(self.error_msg.create_error_msg_full(),
                         'Error Level: "{}"\nEngine: "{}"\nDetails: "{}"'.format(level_mock.return_value,
                                                                                 engine_mock.return_value, self.msg))
        self.assertNotEqual(self.error_msg.error_msg_full, self.error_msg.create_error_msg_full())

    @patch('Framework_Kernel.error_handler.ErrorLevel.get_error_level')
    @patch('Framework_Kernel.error_handler.EngineCode.get_engine_name')
    def test_get_handler(self, engine_mock, level_mock):
        level_mock.return_value = 'terminate_framework'
        engine_mock.return_value = 'controller'
        # level = 00, engine = 01 terminate_framework , config_engine assertNotEqual
        self.assertNotEqual(self.error_handler.error_msg_full,
                            'Error Level: "{}"\nEngine: "{}"\nDetails: "{}"'.format(level_mock.return_value,
                                                                                    engine_mock.return_value, self.msg))
        self.assertEqual(self.error_handler.error_msg, '{}{}{}'.format(self.engine, self.level, self.msg))
        self.assertEqual(self.error_handler.engine_code, '')
        self.assertEqual(self.error_handler.error_level, '')
        self.assertEqual(self.error_handler.error_details, '')
        # level = 00 terminate_framework
        self.assertEqual(self.error_handler._ErrorHandler__get_handler(), self.error_handler.terminate_framework)
        self.assertEqual(self.error_handler.engine_code, self.engine)
        self.assertEqual(self.error_handler.error_level, self.level)
        self.assertEqual(self.error_handler.error_details, self.msg)

    @patch('Framework_Kernel.error_handler.ErrorHandler.reset_engine')
    @patch('Framework_Kernel.error_handler.ErrorHandler.terminate_framework')
    @patch('Framework_Kernel.error_handler.ErrorHandler._ErrorHandler__get_handler')
    def test_handle(self, handler_mock, terminate_mock, reset_mock):
        terminate_mock.return_value = True
        handler_mock.return_value = self.error_handler.terminate_framework
        self.assertTrue(self.error_handler.handle())
        terminate_mock.assert_called_once_with()
        handler_mock.return_value = self.error_handler.reset_engine
        self.assertTrue(self.error_handler.handle(engine='unittest', mail_receiver=self.mail_receiver))
        reset_mock.assert_called_once_with(engine='unittest', mail_receiver=self.mail_receiver)

    @patch('Framework_Kernel.error_handler.ErrorHandler._ErrorHandler__get_handler')
    def test_handle_false(self, handler_mock):
        handler_mock.return_value = False
        self.assertFalse(self.error_handler.handle())

    @patch('Framework_Kernel.error_handler.ErrorHandler.notice')
    def test_terminate_framework(self, notice_mock):
        self.assertFalse(self.error_handler.terminate_framework(self.mail_receiver))
        notice_mock.assert_called_once_with(self.mail_receiver)

    @patch('Framework_Kernel.error_handler.ErrorHandler.notice')
    def test_reset_framework(self, notice_mock):
        self.assertTrue(self.error_handler.reset_framework(self.mail_receiver))
        notice_mock.assert_called_once_with(self.mail_receiver)

    @patch('Framework_Kernel.error_handler.ErrorHandler.notice')
    def test_reset_engine(self, notice_mock):
        p = DelayProcess()
        p.start()
        p.proc.terminate()
        self.assertTrue(self.error_handler.reset_engine(p, self.mail_receiver))
        notice_mock.assert_called_once_with(self.mail_receiver)

    @patch('Framework_Kernel.error_handler.ErrorHandler.notice')
    def test_reset_engine_false(self, notice_mock):
        p = DelayProcess()
        p.start()
        p.proc.terminate()
        with patch('multiprocessing.Process.start') as start_mock:
            self.assertFalse(self.error_handler.reset_engine(p, self.mail_receiver))
            notice_mock.assert_called_once_with(self.mail_receiver)

    @patch('Framework_Kernel.error_handler.ErrorHandler.notice')
    def test_rerun_task(self, notice_mock):
        self.assertTrue(self.error_handler.rerun_task(self.mail_receiver))
        notice_mock.assert_called_once_with(self.mail_receiver)

    @patch('Framework_Kernel.error_handler.ErrorHandler.notice')
    def test_drop_task(self, notice_mock):
        self.task_queue.insert_task(task=self.task)
        self.assertIn(self.task, self.task_queue.get_task_list())
        self.assertFalse(self.error_handler.drop_task(self.task, self.task_queue, self.mail_receiver))
        notice_mock.assert_called_once_with(self.mail_receiver)
        self.assertNotIn(self.task, self.task_queue.get_task_list())

    @patch('Framework_Kernel.error_handler.ErrorHandler.notice')
    def test_record_and_continue(self, notice_mock):
        self.assertTrue(self.error_handler.rerun_task(self.mail_receiver))
        notice_mock.assert_called_once_with(self.mail_receiver)

    @patch('Framework_Kernel.error_handler.ErrorHandler.notice')
    def test_mark_task(self, notice_mock):
        state = 'unittest'
        self.assertTrue(self.error_handler.mark_task(self.task, state, self.mail_receiver))
        self.assertEqual(self.task.get_state(), state)
        notice_mock.assert_called_once_with(self.mail_receiver)

    @patch('Common_Library.email_operator.Email.send_email')
    def test_notice(self, email_mock):
        self.error_handler.notice([])
        email_mock.assert_called_once_with('Error Handle Notice Of Automation Framework',
                                           [email_operator.Email().default_receiver], self.error_handler.error_msg_full,
                                           'plain')
        email_mock.reset_mock()
        self.error_handler.notice(self.mail_receiver)
        default_receiver = [email_operator.Email().default_receiver]
        default_receiver.extend(self.mail_receiver)
        email_mock.assert_called_once_with('Error Handle Notice Of Automation Framework', default_receiver,
                                           self.error_handler.error_msg_full, 'plain')


class DelayProcess:
    def start(self):
        self.proc = Process(target=self.delay_process)
        self.proc.daemon = True
        self.status = self.proc
        self.proc.start()

    @staticmethod
    def delay_process():
        time.sleep(1)
