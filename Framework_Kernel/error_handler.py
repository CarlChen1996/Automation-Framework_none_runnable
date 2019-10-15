# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:51 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : errorhandler.py
# @Project : Automation-Framework

from Framework_Kernel.log import error_handler_log
from Common_Library import email_operator


class EngineCode:
    def __init__(self):
        self.controller = '00'
        self.config_engine = '01'
        self.assembly_engine = '02'
        self.execute_engine = '03'
        self.report = '04'


class ErrorLevel:
    def __init__(self):
        self.terminate_framework = '00'
        self.reset_framework = '01'
        self.reset_engine = '02'
        self.drop_task = '03'
        self.rerun_task = '04'
        self.mark_task = '05'
        self.record_and_continue = '06'


class ErrorMsg():
    def __init__(self, engine_code, error_level, msg):
        self.engine_code = engine_code
        self.error_level = error_level
        self.msg = msg
        self.error_msg = self.create_error_msg()

    def create_error_msg(self):
        return self.engine_code + self.error_level + self.msg


class ErrorHandler:
    def __init__(self, error_msg: ErrorMsg):
        self.error_msg = error_msg.error_msg
        self.engine_code = ''
        self.error_level = ''
        self.error_details = ''

    def __get_handler(self):
        self.engine_code = self.error_msg[:2]
        self.error_level = self.error_msg[2:4]
        self.error_details = self.error_msg[4:]
        self.error_handle_map_dict = {
            ErrorLevel().terminate_framework: self.terminate_framework,
            ErrorLevel().reset_framework: self.reset_framework,
            ErrorLevel().reset_engine: self.reset_engine,
            ErrorLevel().rerun_task: self.rerun_task,
            ErrorLevel().drop_task: self.drop_task,
            ErrorLevel().record_and_continue: self.record_and_continue,
            ErrorLevel().mark_task: self.mark_task
        }
        if self.error_level in self.error_handle_map_dict.keys():
            return self.error_handle_map_dict[self.error_level]
        else:
            return False

    def handle(self, **kargs):
        handle_func = self.__get_handler()
        if handle_func:
            return handle_func(**kargs)
        else:
            print('unknown error level')
            return False

    def terminate_framework(self, mail_receiver):
        error_handler_log.critical(self.error_msg)
        self.notice(mail_receiver)
        return 0

    def reset_framework(self, mail_receiver):
        error_handler_log.critical(self.error_msg)
        self.notice(mail_receiver)
        return 1

    def reset_engine(self, engine, mail_receiver):
        error_handler_log.critical(self.error_msg)
        self.notice(mail_receiver)
        engine.start()
        if engine.status.is_alive():
            error_handler_log.info("[watch_executor_thread] start execution engine successfully")
            error_handler_log.info("[watch_executor_thread] execution engine pid {} current status is {}"
                                   .format(engine.status.pid, str(engine.status.is_alive())))
            return 1
        else:
            error_handler_log.info("[watch_executor_thread] can't start execution engine")
            return 0

    def rerun_task(self, mail_receiver):
        error_handler_log.critical(self.error_msg)
        self.notice(mail_receiver)
        return 1

    def drop_task(self, task, task_queue, mail_receiver):
        error_handler_log.critical(self.error_msg)
        self.notice(mail_receiver)
        task_queue.remove_task(task)
        return 0

    def record_and_continue(self, mail_receiver):
        error_handler_log.info(self.error_msg)
        self.notice(mail_receiver)
        return 1

    def mark_task(self, task, state, mail_receiver):
        error_handler_log.info(self.error_msg)
        self.notice(mail_receiver)
        task.set_state(state)
        return 1

    def notice(self, mail_receiver):
        email = email_operator.Email()
        receiver = [email.default_receiver]
        if mail_receiver:
            receiver.extend(mail_receiver)
        email.send_email("error handle notice", receiver, self.error_msg, 'plain')


if __name__ == '__main__':
    error_msg_instance = ErrorMsg(EngineCode().controller, ErrorLevel().drop_task, 'test msg')
    error_handle_instance = ErrorHandler(error_msg_instance)
    error_handle_instance.handle()
