# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:27 PM
# @Author  : balance
# @Email   : balance.cheng@hp.com
# @File    : AssembleEngine.py
# @Project : Automation-Framework
from Framework_Kernel.engine import Engine
from Framework_Kernel.queue import AssembleQueue
from Framework_Kernel.analyzer import Analyzer
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsExecuteHost
from Framework_Kernel.validator import HostValidator
from Framework_Kernel.validator import ScriptValidator
from Framework_Kernel.script import Script


class AssembleEngine(Engine):
    def start(self, build_list):
        return execute(build_list)


def execute(build_list):
    assembleQueue = AssembleQueue()
    analyzor = Analyzer(['test.txt'])
    data = analyzor.load()
    # task_data = analyzor.generate(data)
    task_data = [{'name': 'task1', 'testscripts': ['t1script1', 't1scripts2', 't1scripts3'], 'testtc': ['15.83.1.1'],
                  'needbuild': True},
                 {'name': 'task2', 'testscripts': ['t2script1', 't2scripts2', 't2scripts3'], 'testtc': ['15.83.1.2'],
                  'needbuild': True},
                 {'name': 'task3', 'testscripts': ['t3script1', 't3scripts2', 't3scripts3'], 'testtc': ['15.83.1.3'],
                  'needbuild': False}]
    #  ------------循环处理task数据， 生成task---------------------------------
    task1 = Task(task_data[0]['name'], task_data[0]['needbuild'])
    for script in task_data[0]['testscripts']:
        task1.insert_script(Script(name=script))
    # -------------UUT是一个list，需要循环产生，----------------------
    uut = WindowsExecuteHost(ip='15.83.1.1', hostnamme='host1', version='win7', mac='mac1')
    task1.insert_uut_list(uut)
    task2 = Task(task_data[1]['name'], task_data[1]['needbuild'])
    for script in task_data[1]['testscripts']:
        task2.insert_script(Script(name=script))
    uut = WindowsExecuteHost(ip='15.83.1.2', hostnamme='host2', version='win7', mac='mac2')
    task2.insert_uut_list(uut)
    task3 = Task(task_data[2]['name'], task_data[2]['needbuild'])
    for script in task_data[2]['testscripts']:
        task3.insert_script(Script(name=script))
    uut = WindowsExecuteHost(ip='15.83.1.3', hostnamme='host3', version='win7', mac='mac3')
    # ------------- validate 后要手动修改host的status属性 ------------------------------------
    task3.insert_uut_list(uut)
    assembleQueue.insert_task(task=task1)
    assembleQueue.insert_task(task=task2)
    assembleQueue.insert_task(task=task3)
    h_validator = HostValidator()
    h_validator.validate(task1.get_uut_list()[0])
    h_validator.validate(task2.get_uut_list()[0])
    h_validator.validate(task3.get_uut_list()[0])
    s_validator = ScriptValidator()
    for temp in assembleQueue.get_task_list():
        s_validator.validate(temp)
    print('-----------------------')
    #　＝＝＝＝＝＝＝＝＝＝通过判读build server的status随机选择要用的 build server =============
    b_host = build_list[0]
    assembleQueue.build_task(task1, b_host)
    assembleQueue.build_task(task2, b_host)
    assembleQueue.build_task(task3, b_host)

    return assembleQueue.get_task_list()


if __name__ == '__main__':
    execute()
