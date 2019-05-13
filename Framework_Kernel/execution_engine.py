# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:46 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : ExecutionEngine.py
# @Project : Automation-Framework
from engine import Engine
from queue import ExecuteQueue
from task import Task
from host import WindowsDeployHost,WindowsExecuteHost
from report import Report
class ExecutionEngine(Engine):
    pass

def execute():
    d=WindowsDeployHost('1','2','3','4','5','6','7','8')
    t=WindowsExecuteHost('1','2','3','4','5','6','7','8')
    task1=Task('task1')
    task2=Task('task2')
    task3=Task('task3')
    r=Report()
    task_list=[task1,task2,task3]
    exeQ=ExecuteQueue()
    exeQ.task_list=task_list
    for i in exeQ.task_list:
        exeQ.deploy(i,d)
        exeQ.execute(i)
        exeQ.check_status(i)
        exeQ.collect_result(i)
        # r.generate(i.collect_result())
    print(exeQ.task_list)
if __name__ == '__main__':
    execute()
