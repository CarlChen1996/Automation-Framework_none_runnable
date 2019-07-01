# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:23 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : Validator.py
# @Project : Automation-Framework
from Framework_Kernel.log import controller_log


class Validator:
    def validate(self, name):
        print('validate finished')


class HostValidator(Validator):
    def validate(self, host):
        controller_log.info('validate ' + host.get_hostname() + ' finished')
        return True


class ScriptValidator(Validator):
    def validate(self, task):
        controller_log.info('validate ' + task.get_name() + ' scripts finished')
        return True
