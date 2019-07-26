# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:23 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : Validator.py
# @Project : Automation-Framework

class Validator:
    def validate(self, name):
        print('validate finished')


class HostValidator(Validator):
    def validate(self, host):
        print('validate ' + host.get_hostname() + ' finished')
        # controller_log.info('validate ' + host.get_hostname() + ' finished')
        return True


class ScriptValidator(Validator):
    def validate(self, task):
        print('validate ' + task.get_name() + ' scripts finished')
        # controller_log.info('validate ' + task.get_name() + ' scripts finished')
        return True
