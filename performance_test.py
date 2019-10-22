# -*- coding: utf-8 -*-
# @Time    : 10/17/2019 1:27 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : performance_test.py
# @Project : Automation-Framework
import os
import psutil
import time
import pandas as pd
import astunparse
import yaml
import ast
from threading import Thread
from subprocess import Popen


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
    with open(root+'/Configuration/config_server_list.yml', 'w', encoding='utf-8') as f:
        yaml.dump(data, f)


def replace_files():
    replace_validator()
    replace_qtp()
    replace_jenkins()


def replace_validator():
    with open(root+'/Framework_kernel/validator.py', 'r+', encoding='utf-8') as f1, \
            open(root+'/Framework_Performance/validator.py', 'r+', encoding='utf-8')as f2,\
            open(root+'/Framework_kernel/host.py', 'r+', encoding='utf-8')as f3,\
            open(root+'/Framework_kernel/report.py', 'r+', encoding='utf-8')as f4:
        validator = f1.read()
        validator_node = ast.parse(validator)
        fake_validator = f2.read()
        fake_validator_node = ast.parse(fake_validator)
        host = f3.read()
        host_node = ast.parse(host)
        report = f4.read()
        report_node = ast.parse(report)
        # validator
        validator_node.body[16].body[2] = fake_validator_node.body[4].body[0]
        validator_node.body[16].body[4] = fake_validator_node.body[4].body[1]
        validator_node.body[16].body[5] = fake_validator_node.body[4].body[2]
        validator_node.body[16].body[8] = fake_validator_node.body[4].body[3]
        validator_node.body[17].body[0] = fake_validator_node.body[5].body[0]
        # print(ast.dump(validator_node.body[-1]))
        # host
        host_node.body[12].body[-2] = fake_validator_node.body[-3]
        # report
        report_node.body[-1].body[-2] = fake_validator_node.body[-2]
        validator_source = astunparse.unparse(validator_node)
        host_source = astunparse.unparse(host_node)
        report_source = astunparse.unparse(report_node)
        # print(validator_source)
        f1.seek(0, 0)
        f1.truncate()
        f1.write(validator_source)
        f3.seek(0, 0)
        f3.truncate()
        f3.write(host_source)
        f4.seek(0, 0)
        f4.truncate()
        f4.write(report_source)


def replace_qtp():
    with open(root+'/Framework_kernel/QTPutils.py', 'r+', encoding='utf-8') as f1, \
            open(root+'/Framework_Performance/QTPutils.py', 'r+', encoding='utf-8')as f2:
        qtp = f1.read()
        fake_qtp = f2.read()
        qtp_node = ast.parse(qtp)
        fake_qtp_node = ast.parse(fake_qtp)
        qtp_node.body[-1].body[-3] = fake_qtp_node.body[-1].body[-3]
        qtp_node.body[-1].body[-2] = fake_qtp_node.body[-1].body[-2]
        qtp_node.body[-1].body[-1] = fake_qtp_node.body[-1].body[-1]
        qtp_source = astunparse.unparse(qtp_node)
        f1.seek(0, 0)
        f1.truncate()
        f1.write(qtp_source)


def replace_jenkins():
    with open(root+'/Common_Library/jenkins_operator.py', 'r+', encoding='utf-8') as f1, \
            open(root+'/Framework_Performance/jenkins_operator.py', 'r+', encoding='utf-8')as f2:
        jenkins = f1.read()
        fake_jenkins = f2.read()
        jenkins_node = ast.parse(jenkins)
        fake_jenkins_node = ast.parse(fake_jenkins)
        jenkins_node.body[-1].body[-4] = fake_jenkins_node.body[-1].body[-1]
        jenkins_node.body[-1].body[-5] = fake_jenkins_node.body[-1].body[-2]
        jenkins_node.body[-1].body[-6] = fake_jenkins_node.body[-1].body[-3]
        jenkins_node.body[-1].body[-8] = fake_jenkins_node.body[-1].body[-4]
        jenkins_node.body[-1].body[-9] = fake_jenkins_node.body[-1].body[-5]
        jenkins_node.body[-1].body[-10] = fake_jenkins_node.body[-1].body[-6]
        jenkins_source = astunparse.unparse(jenkins_node)
        f1.seek(0, 0)
        f1.truncate()
        f1.write(jenkins_source)


if __name__ == '__main__':
    # get root path
    root = os.getcwd()
    with open(root+'/Configuration/config_performance_test.yml') as f:
        settings = yaml.safe_load(f)
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

