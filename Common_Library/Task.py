# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 2:07 PM
# @Author  : Balance
# @Email   : balance.cheng@hp.com
# @File    : Task.py
# @Project : framework



class Task:
    def __init__(self, name, need_build=True):
        self._script_list = []
        self._exe_list = []
        self._uut_list = []
        self._id = 0
        self._name = name
        self._status = ''
        self._state = ''
        self._need_build = need_build

    # ------Below is set/get function for member-----------
    def insert_script(self, script):
        # set scripts
        self._script_list.append(script)

    def get_script_list(self):
        # get scripts
        return self._script_list

    def insert_exe_list(self, file):
        self._exe_list.append(file)

    def get_exe_list(self):
        return self._exe_list

    def insert_uut_list(self, uut):
        self._uut_list.append(uut)

    def get_uut_list(self):
        return self._uut_list

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status == status

    def get_state(self):
        return self._state

    def set_state(self, state):
        self._state = state

    # ---------Below is funtion for task-------------
    def build(self, host):
        host.build(self)

    def get_scripts(self, host):
        host.get_scripts(self)

    def execute(self, host):
        host.execute_task(self)

    def deploy(self, host):
        host.deploy(self)

    def check_status(self, host):
        host.check_status(self)

    def collect_result(self, host):
        host.collect_result(self)

    def terminate(self, host):
        pass

    def get_exe_duration(self):
        pass

    def validate_host(self, validator):
        for host in self._uut_list:
            validator.validate(host)

    def validate_scripts(self, validator):
        for script in self._script_list:
            validator.validate(script)

