# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:46 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : ExecutionEngine.py
# @Project : Automation-Framework
from Framework_Kernel.engine import Engine
from Framework_Kernel.queue import ExecuteQueue
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsDeployHost, WindowsExecuteHost
from Framework_Kernel.report import Report


class ExecutionEngine(Engine):
    def start(self, deploy_list, task_list):
        execute(deploy_list, task_list)


def execute(deploy_list, task_list):
    d = deploy_list[0]
    r = Report()
    exeQ = ExecuteQueue()
    # -----------execute结束后需要同时删除task list-----------------
    exeQ.task_list = task_list.copy()
    # ----------循环里面添加 刷新list的方法 ---------------------
    for i in exeQ.task_list:
        exeQ.deploy(i, d)
        exeQ.execute(i)
        # --------需要得到返回值 ------------------
        exeQ.check_status(i)
        exeQ.collect_result(i)
        r.generate(i.collect_result(i.get_uut_list()[0]))
        # exeQ.task_list.remove(i)
        # print('removed {}'.format(i.get_name()))
        print(task_list)
        print(exeQ.get_task_list())
        task_list.remove(i)
    # for i in task_list:
    #     uuts = i.get_uut_list()
    #     for uut in uuts:
    #         print('================')
    #         print(uut.hostnamme)
    #         print('================')


if __name__ == '__main__':
    pass