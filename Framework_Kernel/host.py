# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
import sys
from Framework_Kernel.log import Log


class Host:
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        self.__ip = ip
        self.__hostname = hostname
        self.__version = version
        self.__mac = mac
        self.__username = username
        self.__password = password
        self.__domain = domain
        self.status = status

    def start(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def reboot(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def shutdown(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def get_ip(self):
        return self.__ip

    def get_hostname(self):
        return self.__hostname

    def get_version(self):
        return self.__version

    def get_mac(self):
        return self.__mac

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_domain(self):
        return self.__domain

    # def get_status(self):
    #     return self.__status
    #
    # def set_status(self, status):
    #     if status == "on" or status == "off":
    #         self.__status = status
    #     else:
    #         print("status format input error, confirm your input is 'on' or 'off'")
    #     return False

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
            task.get_uut_list()[0].get_hostname()))

    def check_status(self, task):
        self.log.log('check {} status on {}'.format(
            task.get_name(),
            task.get_uut_list()[0].get_hostname()))

    def collect_result(self, task):
        self.log.log('collect {} result from {}'.format(
            task.get_name(),
            task.get_uut_list()[0].get_hostname()))


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
