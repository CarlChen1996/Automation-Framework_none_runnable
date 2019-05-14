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
from Framework_Kernel.log import Log


log = Log(name='assemble')


class AssembleEngine(Engine):
    def start(self, build_list, task_list):
        log.log('start assemble engine')
        return execute(build_list, task_list)


def execute(build_list, task_list):
    assembleQueue = AssembleQueue()
    analyzor = Analyzer(['test.txt'])
    data = analyzor.load()
    # task_data = analyzor.generate(data)
    task_data = [{'name': 'task1', 'testscripts': ['t1script1', 't1scripts2', 't1scripts3'],
                  'uutlist': [{'ip': '15.83.1.1', 'hostname': 'uut1', 'version': 'win7', 'mac': '56789tyui'} ],
                  'needbuild': True},
                 {'name': 'task2', 'testscripts': ['t2script1', 't2scripts2', 't2scripts3'],
                  'uutlist': [{'ip': '15.83.1.2', 'hostname': 'uut2', 'version': 'win7', 'mac': '1234567893'} ],
                  'needbuild': True},
                 {'name': 'task3', 'testscripts': ['t3script1', 't3scripts2', 't3scripts3'],
                  'uutlist': [{'ip': '15.83.1.3', 'hostname': 'uut3', 'version': 'win10', 'mac': '987654321'} ],
                  'needbuild': False}]
    for taskitem in task_data:
        task = Task(taskitem['name'], taskitem['needbuild'])
        for script in taskitem['testscripts']:
            task.insert_script(Script(name=script))
        for uutitem in taskitem['uutlist']:
            # ------需要根据 uut的os 来实例，目前没实现，只考虑windows------------
            uut = WindowsExecuteHost(ip=uutitem['ip'], hostnamme=uutitem['hostname'], version=uutitem['version'], mac= uutitem['mac'])
            task.insert_uut_list(uut)
        log.log('inset {} to assembly queue list'.format(task.get_name()))
        assembleQueue.insert_task(task=task)
    print('-------------------------------------------')
    h_validator = HostValidator()
    s_validator = ScriptValidator()
    b_host = build_list[0]
    for task in assembleQueue.get_task_list():
        for uut in task.get_uut_list():
            h_validator.validate(uut)
        s_validator.validate(task)
        assembleQueue.build_task(task, b_host)
        task_list.append(task)
        log.log('delete {} from assemble queue list'.format(task.get_name()))
        # assembleQueue.remove_task(task)
        # print('left task:\n', assembleQueue.get_task_list())
        print('------------------------------------')
    #　＝＝＝＝＝＝＝＝＝＝通过判读build server的status随机选择要用的 build server =============
    return task_list


if __name__ == '__main__':
    execute()
