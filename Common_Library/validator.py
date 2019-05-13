# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:23 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : validator.py
# @Project : Automation-Framework
class Validator:
    def validate(self,name):
        print('validate finished')

class Host_validator(Validator):
    def validate(self,host):
        print('validate '+host+' finished')

class Script_validator(Validator):
    def validate(self,task):
        print('validate '+task+' finished')
