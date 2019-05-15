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
from Framework_Kernel.log import Log
import os

log = Log(name='configuration')


class ConfigurationEngine(Engine):
    def start(self, build_list, deploy_list):
        log.log('start configurator')
        config_process(build_list, deploy_list)


def config_process(build_list, deploy_list):
    c = Configurator()
    c.config()

    env_host = os.path.join((os.path.abspath(r".\Configuration")),
                            "env_host.yml")
    analyze = Analyzer([env_host])
    env_host_res = analyze.load()
    env_host_data = analyze.generate(env_host_res)

    build_host_data = env_host_data[0][0]

    deploy_host_data = env_host_data[0][1]
    b_ip = build_host_data.get("ip")
    b_hostname = build_host_data.get("hostname")
    b_version = build_host_data.get("version")
    b_mac = build_host_data.get("mac")

    d_ip = deploy_host_data.get("ip")
    d_hostname = deploy_host_data.get("hostname")
    d_version = deploy_host_data.get("version")
    d_mac = deploy_host_data.get("mac")
    b = WindowsBuildHost(ip=b_ip,
                         hostname=b_hostname,
                         version=b_version,
                         mac=b_mac)
    log.log('Init {}'.format(b.hostname))
    d = WindowsDeployHost(ip=d_ip,
                          hostname=d_hostname,
                          version=d_version,
                          mac=d_mac)
    log.log('Init {}'.format(d.hostname))
    # b = WindowsBuildHost(
    #                       ip="192.168.1.1",
    #                       hostname="windows_Build_server1",
    #                       version="1.0",
    #                       mac='27832784292')

    # d = WindowsDeployHost(
    #                       ip="192.168.1.2",
    #                       hostname="windows_Deploy_server1",
    #                       version="1.1",
    #                       mac='98765432')

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
