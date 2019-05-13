# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
from Common_Library.Engine import Engine
from Common_Library.Configurator import Configurator
from Common_Library.host import Windows_Build_Host,Windows_Deploy_Host
from Common_Library.Analyzer import Analyzer
from Common_Library.Validator import Validator

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

    b=Windows_Build_Host("192.168.1.1","win_build","1.0","123456789","bamboo","123456","sh","off")
    d=Windows_Deploy_Host("192.168.1.2","win_deploy","1.0","987654321","bamboo","123456","sh","off")
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

