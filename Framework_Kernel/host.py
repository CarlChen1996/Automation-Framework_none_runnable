# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
import sys


class Host():
    def __init__(self, ip, mac, hostnamme='', version='', username='', password='', domain='',
                 status='off'):
        self.ip = ip
        self.hostnamme = hostnamme
        self.version = version
        self.mac = mac
        self.username = username
        self.password = password
        self.domain = domain
        self.status = status

    def start(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def reboot(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def shutdown(self):
        print(sys._getframe().f_code.co_name + "  finished")


class WindowsHost(Host):
    pass


class LinuxHost(Host):
    pass


class Build:
    def get_scripts(self, task):
        for script in task.get_script_list():
            print('get scripts: {} PASS'.format(script.name))

    def build(self, task):
        for script in task.get_script_list():
            print('build ' + script.name + ' PASS')
        task.insert_exe_list(task.get_name() + 'Exe')
        task.insert_exe_list(task.get_name() + ' Folder Path')


class Deploy:
    def deploy(self, task):
        print('deploy exe name:' + task.get_exe_list()[0] + ' Pass')
        print('deploy exe folder:' + task.get_exe_list()[1])


class Execute:
    def execute_task(self, task):
        print('execute task: {} PASS'.format(task.get_exe_list()[0]))

    def check_status(self, task):
        print('check task: {} status'.format(task.get_exe_list()[0]))

    def collect_result(self, task):
        print('collect task: {} result'.format(task.get_exe_list()[0]))


class WindowsBuildHost(WindowsHost, Build):
    pass


class WindowsDeployHost(WindowsHost, Deploy):
    pass


class WindowsExecuteHost(WindowsHost, Execute):
    pass


class LinuxBuild(LinuxHost, Build):
    pass


class Linux_Execute(LinuxHost, Execute):
    pass


if __name__ == "__main__":
    b = WindowsBuildHost("", "", "", "", "", "", "", "")
    b.build()
    d = WindowsDeployHost("", "", "", "", "", "", "", "")
    d.deploy()
    e = WindowsExecuteHost("", "", "", "", "", "", "", "")
    e.check_status()
    e.collect_result()
