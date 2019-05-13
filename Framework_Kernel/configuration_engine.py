# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
from engine import Engine
from configurator import Configurator
from host import WindowsBuildHost,WindowsDeployHost
from analyzer import Analyzer
from validator import Validator

class ConfigurationEngine(Engine):
    pass

def config_process():
    con=ConfigurationEngine()
    con.start()
    c=Configurator()
    c.config()
    analyze=Analyzer()
    analyze.load()
    analyze.generate()

    b=WindowsBuildHost("192.168.1.1","win_build","1.0","123456789","bamboo","123456","sh","off")
    d=WindowsDeployHost("192.168.1.2","win_deploy","1.0","987654321","bamboo","123456","sh","off")
    v=Validator()
    v.validate(b)
    v.validate(d)
    b.Status="on"
    d.Status = "on"
    build_list.append(b)
    deploy_list.append(d)
    con.stop()


if __name__=="__main__":
    build_list=[]
    deploy_list=[]
    config_process()

    print(build_list)
    print(deploy_list)

