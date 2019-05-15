# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:46 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : ExecutionEngine.py
# @Project : Automation-Framework
from Framework_Kernel.engine import Engine
from Framework_Kernel.queue import ExecuteQueue
'''
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsDeployHost, WindowsExecuteHost
'''
from Framework_Kernel.report import Report
from Framework_Kernel.log import Log

log = Log('Execution')


class ExecutionEngine(Engine):
    def start(self, deploy_list, task_list):

        execute(deploy_list, task_list)
        print('=======================================')
        print('       waitting for new task ...')
        print('=======================================')


def execute(deploy_list, task_list):
    d = deploy_list[0]

    exeQ = ExecuteQueue()
    # -----------execute结束后需要同时删除task list-----------------
    exeQ.task_list = task_list.copy()
    # ----------循环里面添加 刷新list的方法 ---------------------
    for i in exeQ.task_list[:]:
        exeQ.deploy(i, d)
        exeQ.execute(i)
        # --------需要得到返回值 ------------------
        exeQ.check_status(i)
        exeQ.collect_result(i)
        r = Report(i.get_name(),i.get_script_list())
        r.generate()
        exeQ.task_list.remove(i)
        log.log('removed {} from execute queue'.format(i.get_name()))
        print('task left in execute queue: {}'.format(len(exeQ.task_list)))
        print('---------------------------------------------------------------')
    print('All task execution finished')


if __name__ == '__main__':
    execute()
