# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:51 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : errorhandler.py
# @Project : Automation-Framework

from Framework_Kernel.log import error_handler_log


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
        self.rerun_task = '03'
        self.drop_task = '04'
        self.continue_task = '05'


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
            ErrorLevel().continue_task: self.continue_task
        }
        if self.error_level in self.error_handle_map_dict.keys():
            return self.error_handle_map_dict[self.error_level]

    def handle(self, **kargs):
        handle_func = self.__get_handler()
        return handle_func(**kargs)

    def terminate_framework(self):
        error_handler_log.critical(self.error_msg)
        print("terminate_framework")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)
        return 0

    def reset_framework(self):
        error_handler_log.critical(self.error_msg)
        print("reset_framework")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)

    def reset_engine(self, engine):
        error_handler_log.critical(self.error_msg)
        engine.start()
        if engine.status.is_alive():
            error_handler_log.info("[watch_executor_thread] start execution engine successfully")
            error_handler_log.info("[watch_executor_thread] execution engine pid {} current status is {}"
                                   .format(engine.status.pid, str(engine.status.is_alive())))
            return 1
        else:
            error_handler_log.info("[watch_executor_thread] can't start execution engine")
            return 0

    def rerun_task(self):
        error_handler_log.critical(self.error_msg)
        print("rerun_task")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)

    def drop_task(self, task, task_queue):
        error_handler_log.critical(self.error_msg)
        print("drop_task")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)
        task_queue.remove_task(task)
        return 0

    def continue_task(self):
        error_handler_log.info(self.error_msg)
        print("continue_task")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)


if __name__ == '__main__':
    error_msg_instance = ErrorMsg(EngineCode().controller, ErrorLevel().drop_task, 'test msg')
    error_handle_instance = ErrorHandler(error_msg_instance)
    error_handle_instance.handle()
