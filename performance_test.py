# -*- coding: utf-8 -*-
# @Time    : 10/17/2019 1:27 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : performance_test.py
# @Project : Automation-Framework
import os
import psutil
import shutil
import sys
import time
import pandas as pd
import yaml
from multiprocessing import Process
from threading import Thread
from subprocess import Popen,PIPE

def generate_test_plan(count, interval, delay):
    start_time = time.time()
    timer = 0
    for i in range(count):
        plan = pd.read_excel(root+'/Test_Plan/Loaded_TEST_PLAN_template.xlsx', sheet_name=None)
        plan['config']['VALUE'][0] += '_' + str(i + 1)
        writer = pd.ExcelWriter(root+'/Test_Plan/TEST_PLAN_p_{}.xlsx'.format(i + 1))
        for sheet in plan:
            pd.DataFrame(plan[sheet]).to_excel(writer, index=False, header=True, sheet_name=sheet)
        writer.close()
        timer += 1
        if timer == interval:
            time.sleep(delay)
            timer = 0
    end_time = time.time()
    print(end_time - start_time)


def generate_node(build_node_w_count, build_node_tp_count, deploy_node_w_count):
    data = []
    for i in range(build_node_w_count):
        build_node_w = {'name': 'Build_Node_W_{}'.format(i + 1),
                        'os': 'windows',
                        'function': 'build',
                        'hostname': 'Build_Node_W_{}'.format(i + 1),
                        'ip': '15.83.248.252',
                        'mac': '27832784292',
                        'version': '1.0',
                        'username': 'Automation',
                        'password': 'Shanghai2010',
                        'domain': 'sh'}
        data.append(build_node_w)
    for i in range(build_node_tp_count):
        build_node_tp = {'name': 'Build_Node_TP_{}'.format(i + 1),
                         'os': 'linux',
                         'function': 'build',
                         'hostname': 'Build_Node_TP_{}'.format(i + 1),
                         'ip': '15.83.248.253',
                         'mac': '27832784292',
                         'version': '1.0',
                         'username': 'automation',
                         'password': 'Shanghai2010',
                         'domain': 'sh'}
        data.append(build_node_tp)
    for i in range(deploy_node_w_count):
        deploy_node_w = {'name': 'Deploy_Node_{}'.format(i + 1),
                         'os': 'windows',
                         'function': 'deploy',
                         'hostname': 'Deploy_Node_{}'.format(i + 1),
                         'ip': '15.83.248.251',
                         'mac': '5666666',
                         'version': '1.0',
                         'username': 'Administrator',
                         'password': 'Shanghai2010',
                         'domain': ''}
        data.append(deploy_node_w)
    with open(src_config, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)


def replace_files():
    shutil.copy(src_config, dst_config)
    shutil.copy(src_jenkins, dst_jenkins)
    shutil.copy(src_qtp, dst_qtp)
    shutil.copy(src_validator, dst_validator)


def backup_files():
    shutil.copy(dst_config + src_config, 'source')
    shutil.copy(dst_jenkins + src_jenkins, 'source')
    shutil.copy(dst_qtp + src_qtp, 'source')
    shutil.copy(dst_validator + src_validator, 'source')


def recovery_files():
    shutil.copy('source' + src_config, dst_config)
    shutil.copy('source' + src_jenkins, dst_jenkins)
    shutil.copy('source' + src_qtp, dst_qtp)
    shutil.copy('source' + src_validator, dst_validator)


if __name__ == '__main__':
    # get root path
    root = os.getcwd()
    with open(root+'/Configuration/config_performance_test.yml') as f:
        settings = yaml.safe_load(f)
    src_config = root+'/Framework_Performance/config_server_list.yml'
    src_jenkins = root+'/Framework_Performance/jenkins_operator.py'
    src_qtp = root+'/Framework_Performance/QTPutils.py'
    src_validator = root+'/Framework_Performance/validator.py'
    dst_config = root + '/Configuration'
    dst_jenkins = root + '/Common_Library'
    dst_qtp = root + '/Framework_Kernel'
    dst_validator = root + '/Framework_Kernel'
    # generate server config file
    generate_node(settings['build_node_win'], settings['build_node_lin'], settings['deploy_server'])
    # replace files
    replace_files()
    # start generate test plans
    t = Thread(target=generate_test_plan, args=(settings['test_plan_count'], settings['generate_plan_interval'],
                                               settings['generate_plan_delay']))
    t.start()
    # run controller
    f = Popen('python {}/controller.py 02'.format(root))
    p = psutil.Process(f.pid)
    while True:
        print('Pid:', f.pid, ', Used Memory:', p.memory_info().rss / 1024 / 1024, 'MB')
        time.sleep(10)
    # f.wait()
    # t.join()


