# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:51 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : errorhandler.py
# @Project : Automation-Framework

from Framework_Kernel.log import error_handler_log


class ENGINE_CODE:
    def __init__(self):
        self.controller='00'
        self.config_engine='01'
        self.assembly_engine='02'
        self.execute_engine='03'
        self.report='04'


class ERROR_LEVEL:
    def __init__(self):
        self.terminate_framework='00'
        self.reset_framework='01'
        self.reset_engine='02'
        self.rerun_task='03'
        self.drop_task='04'
        self.continue_task='05'


class ERROR_MSG():
    def __init__(self,engine_code,error_level,msg):
        self.engine_code=engine_code
        self.error_level=error_level
        self.msg=msg
        self.error_msg=self.create_error_msg()

    def create_error_msg(self):
        return self.engine_code+self.error_level+self.msg


class ErrorHandler:
    def __init__(self, error_msg:ERROR_MSG):
        self.error_msg = error_msg.error_msg
        self.engine_code=''
        self.error_level=''
        self.error_details=''

    def handle(self):
        self.engine_code=self.error_msg[:2]
        self.error_level=self.error_msg[2:4]
        self.error_details=self.error_msg[4:]
        if self.error_level==ERROR_LEVEL().terminate_framework:
            self.terminate_framework()
        elif self.error_level==ERROR_LEVEL().reset_framework:
            self.reset_framework()
        elif self.error_level==ERROR_LEVEL().rerun_task:
            self.rerun_task()
        elif self.error_level==ERROR_LEVEL().drop_task:
            self.drop_task()
        elif self.error_level==ERROR_LEVEL().continue_task:
            self.continue_task()

    def terminate_framework(self):
        error_handler_log.critical(self.error_msg)
        print("terminate_framework")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)

    def reset_framework(self):
        error_handler_log.critical(self.error_msg)
        print("reset_framework")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)

    def reset_engine(self, engine):
        error_handler_log.critical(self.error_msg)
        print("reset_engine")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)

    def rerun_task(self):
        error_handler_log.critical(self.error_msg)
        print("rerun_task")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)

    def drop_task(self):
        error_handler_log.critical(self.error_msg)
        print("drop_task")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)

    def continue_task(self):
        error_handler_log.info(self.error_msg)
        print("continue_task")
        print(self.engine_code, ':', self.error_level, ':', self.error_details)


if __name__ == '__main__':
    error_msg_instance=ERROR_MSG(ENGINE_CODE().controller,ERROR_LEVEL().drop_task,'test msg')
    error_handle_instance=ErrorHandler(error_msg_instance)
    error_handle_instance.handle()