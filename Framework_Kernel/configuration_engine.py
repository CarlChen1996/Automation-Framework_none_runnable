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
from Framework_Kernel.validator import Validator


class ConfigurationEngine(Engine):
    def start(self, build_list, deploy_list):
        config_process(build_list, deploy_list)


def config_process(build_list, deploy_list):
    c = Configurator()
    c.config()
    analyze = Analyzer()
    analyze.load()
    analyze.generate()

    b = WindowsBuildHost("192.168.1.1", "win_build", "1.0", "123456789", "bamboo", "123456", "sh", "off")
    d = WindowsDeployHost("192.168.1.2", "win_deploy", "1.0", "987654321", "bamboo", "123456", "sh", "off")
    v = Validator()
    v.validate(b)
    v.validate(d)
    b.Status = "on"
    d.Status = "on"
    build_list.append(b)
    deploy_list.append(d)


if __name__ == "__main__":
    build_list = []
    deploy_list = []
    config_process()

    print(build_list)
    print(deploy_list)
