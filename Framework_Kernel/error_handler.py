# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:51 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : errorhandler.py
# @Project : Automation-Framework


class ErrorHandler:
    def __init__(self, error_code):
        self.error_code = error_code

    def handle(self, error_code):
        pass

    def exit(self):
        pass

    def reset_framework(self):
        pass

    def reset(self, engine):
        pass

    def continue_work(self):
        pass
