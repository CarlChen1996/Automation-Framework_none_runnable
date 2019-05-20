# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
import sys
from Framework_Kernel.log import Log


class Host():
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        self.ip = ip
        self.hostname = hostname
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
    def __init__(self):
        self.log = Log('build_host')

    def get_scripts(self, task):
        for script in task.get_script_list():
            pass
        self.log.log('get  {} scripts PASS'.format(task.get_name()))

    def build(self, task):
        for script in task.get_script_list():
            pass
        self.log.log('build ' + task.get_name() + ' PASS')
        task.insert_exe_list(task.get_name() + '.exe')
        task.insert_exe_list(task.get_name())


class Deploy:
    def __init__(self):
        self.log = Log('deploy_host')

    def deploy(self, task):
        self.log.log('deploy package: ' + task.get_name() + ' Pass')


class Execute:
    def __init__(self):
        self.log = Log('uut')

    def execute_task(self, task):
        self.log.log('execute {} on  {}'.format(
            task.get_name(),
            task.get_uut_list()[0].hostname))

    def check_status(self, task):
        self.log.log('check {} status on {}'.format(
            task.get_name(),
            task.get_uut_list()[0].hostname))

    def collect_result(self, task):
        self.log.log('collect {} result from {}'.format(
            task.get_name(),
            task.get_uut_list()[0].hostname))


class WindowsBuildHost(WindowsHost, Build):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        WindowsHost.__init__(self, ip, mac, hostname, version, username,
                             password, domain, status)
        Build.__init__(self)

    pass


class WindowsDeployHost(WindowsHost, Deploy):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        WindowsHost.__init__(self, ip, mac, hostname, version, username,
                             password, domain, status)
        Deploy.__init__(self)

    pass


class WindowsExecuteHost(WindowsHost, Execute):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        WindowsHost.__init__(self, ip, mac, hostname, version, username,
                             password, domain, status)
        Execute.__init__(self)

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
