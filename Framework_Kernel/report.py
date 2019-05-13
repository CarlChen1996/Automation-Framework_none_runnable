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
        print(result)

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




