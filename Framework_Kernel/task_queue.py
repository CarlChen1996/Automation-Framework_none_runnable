# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 2:06 PM
# @Author  : Balance
# @Email   : balance.cheng@hp.com
# @File    : Queue.py
# @Project : framework


class Queue:
    def __init__(self):
        self.__task_list = []

    def insert_task(self, index=0, task=''):
        if index == 0:
            self.__task_list.append(task)
        else:
            self.__task_list.insert(index, task)

    def remove_task(self, task):
        self.__task_list.remove(task)

    def set_order(self, index, task):
        pass

    def clear(self):
        self.__task_list = []

    def get_task_list(self):
        return self.__task_list
