# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 2:07 PM
# @Author  : Balance
# @Email   : balance.cheng@hp.com
# @File    : Task.py
# @Project : framework
from Framework_Kernel import QTPutils


class Task:
    def __init__(self, name, email='', repository='', need_build=True):
        self.__email = email
        self.__repository = repository
        self.__script_list = []
        self.__exe_file_list = []
        self.__uut_list = []
        self.__id = 0
        self.__name = name
        self.__status = ''
        self.__state = ''
        self.__need_build = need_build
        self.start_time = ''
        self.end = ''

    # ------Below is set/get function for member-----------
    def insert_script(self, script):
        # set scripts
        self.__script_list.append(script)

    def get_script_list(self):
        # get scripts
        return self.__script_list

    def insert_exe_file_list(self, file):
        self.__exe_file_list.append(file)

    def get_exe_file_list(self):
        return self.__exe_file_list

    def insert_uut_list(self, uut):
        self.__uut_list.append(uut)

    def get_uut_list(self):
        return self.__uut_list

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_status(self):
        return self.__status

    def get_email(self):
        return self.__email

    def get_repository(self):
        return self.__repository

    def set_status(self, status):
        self.__status = status

    def get_state(self):
        return self.__state

    def set_state(self, state):
        self.__state = state

    # ---------Below is funtion for task-------------
    def build(self, host):
        host.build_task(self)

    def get_scripts(self, host):
        host.get_scripts(self)

    # def execute(self, host):
    #     # host is UUT host
    #     host.execute_task(self)

    def execute(self):
        QTPutils.QTP_HPDM().execute_task()

    def deploy(self, host):
        host.deploy_task(self)

    # def check_status(self, host):
    #     host.check_status(self)

    # def collect_result(self, host):
    #     host.collect_result(self)

    def collect_result(self):
        QTPutils.QTP_HPDM().get_result()

    def terminate(self, host):
        pass

    def get_execute_duration(self):
        pass

    def validate_host(self, validator):
        for host in self.__uut_list:
            validator.validate(host)

    def validate_scripts(self, validator):
        for script in self.__script_list:
            validator.validate(script)
