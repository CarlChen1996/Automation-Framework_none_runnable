# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:27 PM
# @Author  : balance
# @Email   : balance.cheng@hp.com
# @File    : AssembleEngine.py
# @Project : Automation-Framework
from engine import Engine
from queue import AssembleQueue
from analyzer import Analyzer
from task import Task
from host import WindowsExecuteHost
from validator import HostValidator
from validator import ScriptValidator


class AssembleEngine(Engine):
    def __init__(self):
        Engine.__init__()


def execute():
    assembleQueue = AssembleQueue()
    analyzor =Analyzer()
    data = analyzor.load('test.txt')
    # task_data = analyzor.generate(data)
    task_data = [{'name':'task1','testscripts':['t1script1','t1scripts2','t1scripts3'],'testtc':['15.83.1.1'],'needbuild':True},
                 {'name':'task2','testscripts':['t2script1','t2scripts2','t2scripts3'],'testtc':['15.83.1.2'],'needbuild':True},
                 {'name':'task3','testscripts':['t3script1','t3scripts2','t3scripts3'],'testtc':['15.83.1.3'],'needbuild':False}]
    task1 = Task(task_data[0]['name'],task_data[0]['needbuild'])
    for script in task_data[0]['testscripts']:
        task1.insert_script(script)

    uut = WindowsExecuteHost('15.83.1.1', 'host1', 'win7', 'mac1', 'user1', 'password1', 'domain1', 'oneline')
    task1.insert_uut_list(uut)
    task2 = Task(task_data[1]['name'], task_data[1]['needbuild'])
    for script in task_data[1]['testscripts']:
        task2.insert_script(script)
    uut = WindowsExecuteHost('15.83.1.2', 'host2', 'win7', 'mac2', 'user2', 'password2', 'domain2', 'oneline')
    task2.insert_uut_list(uut)
    task3 = Task(task_data[2]['name'], task_data[2]['needbuild'])
    for script in task_data[2]['testscripts']:
        task3.insert_script(script)
    uut = WindowsExecuteHost('15.83.1.3', 'host3', 'win7', 'mac3', 'user3', 'password3', 'domain3', 'oneline')
    task3.insert_uut_list(uut)
    assembleQueue.insert_task(task=task1)
    assembleQueue.insert_task(task=task2)
    assembleQueue.insert_task(task=task3)
    h_validator = HostValidator()
    h_validator.validate(task1.get_uut_list()[0].IP)
    h_validator.validate(task2.get_uut_list()[0].IP)
    h_validator.validate(task3.get_uut_list()[0].IP)
    s_validator = ScriptValidator()
    for temp in task1.get_script_list():
        s_validator.validate(temp)
    for temp in task2.get_script_list():
        s_validator.validate(temp)
    for temp in task3.get_script_list():
        s_validator.validate(temp)
    print('-----------------------')
    assembleQueue.build_task(task1)
    assembleQueue.build_task(task2)
    assembleQueue.build_task(task3)


execute()
