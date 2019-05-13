# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:19 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : report.py
# @Project : Automation-Framework
class Report:
    def __init__(self,name='default',type='HTML',template='1'):
        self.name=name
        self.type=type
        self.template=template

    def generate(self,result):
        print('generate html finished')

class Email:
    def __init__(self):
        pass
    def send(self,receiver='', sender='', subject='', content='', attanchments=''):
        self.receiver=receiver
        self.sender=sender
        self.sender = subject
        self.sender = content
        self.sender = attanchments
        print('send email')

class Log:
    def __init__(self,name='',type='',level=''):
        self.name=name
        self.type=type
        self.level=level
    def log(self,level,msg):
        self.level=level
        print(self.name+'-'+self.level+'-'+msg)

class Validator:
    def validate(self):
        print('validate finished')

class Host_validator(Validator):
    def validate(self,host):
        print('validate '+host+' finished')

class Script_validator(Validator):
    def validate(self,task):
        print('validate '+task+' finished')

