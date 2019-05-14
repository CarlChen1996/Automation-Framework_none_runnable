# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
from Framework_Kernel.engine import Engine
from Framework_Kernel.configurator import Configurator
from Framework_Kernel.host import WindowsBuildHost, WindowsDeployHost
from Framework_Kernel.analyzer import Analyzer
from Framework_Kernel.validator import HostValidator


class ConfigurationEngine(Engine):
    def start(self, build_list, deploy_list):
        config_process(build_list, deploy_list)


def config_process(build_list, deploy_list):
    c = Configurator()
    c.config()
    analyze = Analyzer()
    analyze.load()
    analyze.generate()

    b = WindowsBuildHost(ip="192.168.1.1", hostnamme="win_build", version="1.0", mac='27832784292')
    d = WindowsDeployHost(ip="192.168.1.2", hostnamme="win_deploy", version="1.1", mac='98765432')
    v = HostValidator()
    # 下面要判断OFF的情况--------------------------------------------------------
    if v.validate(b):
        b.Status = "on"
        build_list.append(b)
    if v.validate(d):
        d.Status = "on"
        deploy_list.append(d)



if __name__ == "__main__":
    build_list = []
    deploy_list = []
    config_process()

    print(build_list)
    print(deploy_list)
