# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:27 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : ConfigurationEngine.py
# @Project : Automation-Framework
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

    b=Windows_Build_Host("1","","","","","","","")
    d=Windows_Deploy_Host("2","","","","","","","")
    v=Validator()
    v.validate(b)
    v.validate(d)
    build_list.append(b)
    deploy_list.append(d)
    con.stop()


if __name__=="__main__":
    build_list=[]
    deploy_list=[]
    config_process()

    print(build_list)
    print(deploy_list)

