# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
import sys


class Host():
    def __init__(self, ip, hostnamme, version, mac, username, password, domain,
                 status):
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
    def get_scripts(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def build(self):
        print(sys._getframe().f_code.co_name + "  finished")


class Deploy:
    def deploy(self, task):
        print(sys._getframe().f_code.co_name + task + "  finished")


class Execute:
    def execute_task(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def check_status(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def collect_result(self):
        print(sys._getframe().f_code.co_name + "  finished")


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
