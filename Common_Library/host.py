# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
import sys
class Host():
    def __init__(self,IP,HostName,version,Mac,Username,Password ,Domain ,Status):
        self.IP=IP
        self.HostName=HostName
        self.version=version
        self.Mac=Mac
        self.Username=Username
        self.Password=Password
        self.Domain=Domain
        self.Status=Status
    def start(self):
        print(sys._getframe().f_code.co_name + "  finished")
    def reboot(self):
        print(sys._getframe().f_code.co_name + "  finished")
    def shutdown(self):
        print(sys._getframe().f_code.co_name + "  finished")
class Windows_host(Host):
    pass
class Linux_host(Host):
    pass

class Build:
    def getScripts(self):
        print(sys._getframe().f_code.co_name + "  finished")
    def build(self):
        print(sys._getframe().f_code.co_name + "  finished")
class Deploy:
    def deploy(self,task):
        print(sys._getframe().f_code.co_name +task+"  finished")
class Execute:
    def execute_task(self):
        print(sys._getframe().f_code.co_name + "  finished")
    def check_status(self):
        print(sys._getframe().f_code.co_name + "  finished")
    def collect_result(self):
        print(sys._getframe().f_code.co_name + "  finished")

class Windows_Build_Host(Windows_host,Build):
    pass

class Windows_Deploy_Host(Windows_host,Deploy):
    pass

class Windows_Execute_Host(Windows_host,Execute):
    pass

class Linux_Build(Linux_host,Build):
    pass

class Linux_Execute(Linux_host,Execute):
    pass


if __name__=="__main__":
    b=Windows_Build_Host("","","","","","","","")
    b.build()
    d=Windows_Deploy_Host("","","","","","","","")
    d.deploy()
    e=Windows_Execute_Host("","","","","","","","")
    e.check_status()
    e.collect_result()

