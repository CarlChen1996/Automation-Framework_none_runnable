# -*- coding: utf-8 -*-
# @Time    : 10/17/2019 1:27 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : performance_test.py
# @Project : Automation-Framework
import _ast
import os
import psutil
import time
import pandas as pd
import astunparse
import yaml
import ast
from copy import deepcopy
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
            open(root+'/Framework_Performance/validator_and_others.py', 'r+', encoding='utf-8')as f2,\
            open(root+'/Framework_kernel/host.py', 'r+', encoding='utf-8')as f3,\
            open(root+'/Framework_kernel/report.py', 'r+', encoding='utf-8')as f4,\
            open(root+'/Framework_kernel/execution_engine.py', 'r+', encoding='utf-8')as f5:
        validator = f1.read()
        validator_node = ast.parse(validator)
        fake_validator = f2.read()
        fake_validator_node = ast.parse(fake_validator)
        host = f3.read()
        host_node = ast.parse(host)
        report = f4.read()
        report_node = ast.parse(report)
        execution_engine = f5.read()
        execution_engine_node = ast.parse(execution_engine)
        # print(ast.dump(fake_validator_node))
        validator_map_dict = {
            'validate_jenkins_server': fake_validator_node.body[5].body[0],
            'validate_build_server': fake_validator_node.body[5].body[1],
            '__validate_QTP': fake_validator_node.body[5].body[2],
            '__validate_HPDM': fake_validator_node.body[5].body[3],
            'validate_uut': fake_validator_node.body[5].body[4],
            'validate_ftp': fake_validator_node.body[5].body[5],
            'validate': fake_validator_node.body[6].body[0],
            'build_task': fake_validator_node.body[-3],
            '__load_uut_result': fake_validator_node.body[-2],
            'send_report': fake_validator_node.body[-1],
        }
        # skip validate
        for i in validator_node.body:
            i_index = validator_node.body.index(i)
            if isinstance(i, _ast.ClassDef) and i.name == 'HostValidator':
                print(validator_node.body[i_index])
                for j in i.body:
                    j_index = i.body.index(j)
                    if isinstance(j, _ast.FunctionDef) and j.name in validator_map_dict.keys():
                        validator_node.body[i_index].body[j_index] = validator_map_dict[j.name]
            if isinstance(i, _ast.ClassDef) and i.name == 'ScriptValidator':
                for j in i.body:
                    j_index = i.body.index(j)
                    if isinstance(j, _ast.FunctionDef) and j.name in validator_map_dict.keys():
                        validator_node.body[i_index].body[j_index] = validator_map_dict[j.name]
        validator_source = astunparse.unparse(validator_node)
        f1.seek(0, 0)
        f1.truncate()
        f1.write(validator_source)
        # host skip generate script yml
        for h in host_node.body:
            h_index = host_node.body.index(h)
            if isinstance(h, _ast.ClassDef) and h.name == 'Build':
                # print(host_node.body[h_index])
                for j in h.body:
                    j_index = h.body.index(j)
                    if isinstance(j, _ast.FunctionDef) and j.name in validator_map_dict.keys():
                        host_node.body[h_index].body[j_index] = validator_map_dict[j.name]
                        host_source = astunparse.unparse(host_node)
                        f3.seek(0, 0)
                        f3.truncate()
                        f3.write(host_source)
        # report cancel error handler
        for r in report_node.body:
            r_index = report_node.body.index(r)
            if isinstance(r, _ast.ClassDef) and r.name == 'Report':
                # print(host_node.body[h_index])
                for j in r.body:
                    j_index = r.body.index(j)
                    if isinstance(j, _ast.FunctionDef) and j.name in validator_map_dict.keys():
                        report_node.body[r_index].body[j_index] = validator_map_dict[j.name]
                        report_source = astunparse.unparse(report_node)
                        f4.seek(0, 0)
                        f4.truncate()
                        f4.write(report_source)
        # execution_engine cancel email
        for e in execution_engine_node.body:
            e_index = execution_engine_node.body.index(e)
            if isinstance(e, _ast.ClassDef) and e.name == 'ExecutionEngine':
                # print(host_node.body[h_index])
                for j in e.body:
                    j_index = e.body.index(j)
                    if isinstance(j, _ast.FunctionDef) and j.name in validator_map_dict.keys():
                        execution_engine_node.body[e_index].body[j_index] = validator_map_dict[j.name]
                        report_source = astunparse.unparse(execution_engine_node)
                        f5.seek(0, 0)
                        f5.truncate()
                        f5.write(report_source)


def replace_qtp():
    with open(root+'/Framework_kernel/QTPutils.py', 'r+', encoding='utf-8') as f1, \
            open(root+'/Framework_Performance/QTPutils.py', 'r+', encoding='utf-8')as f2:
        qtp = f1.read()
        fake_qtp = f2.read()
        qtp_node = ast.parse(qtp)
        fake_qtp_node = ast.parse(fake_qtp)
        qtp_map_dict = {
            'deploy_task': fake_qtp_node.body[-1].body[-3],
            'execute_task': fake_qtp_node.body[-1].body[-2],
            'get_result': fake_qtp_node.body[-1].body[-1],
        }
        # print(ast.dump(jenkins_node))
        for i in qtp_node.body:
            i_index = qtp_node.body.index(i)
            if isinstance(i, _ast.ClassDef) and i.name == 'HPDMOperator':
                # print(jenkins_node.body[i_index])
                for j in i.body:
                    j_index = i.body.index(j)
                    if isinstance(j, _ast.FunctionDef) and j.name in qtp_map_dict.keys():
                        qtp_node.body[i_index].body[j_index] = qtp_map_dict[j.name]
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
        jenkins_map_dict = {
            'get_build_result': fake_jenkins_node.body[-1].body[-1],
            'get_last_build_number': fake_jenkins_node.body[-1].body[-2],
            'build_job': fake_jenkins_node.body[-1].body[-3],
            'delete_job': fake_jenkins_node.body[-1].body[-4],
            'initial_job_configuration': fake_jenkins_node.body[-1].body[-5],
            'create_job': fake_jenkins_node.body[-1].body[-6],
        }
        # print(ast.dump(jenkins_node))
        for i in jenkins_node.body:
            i_index = jenkins_node.body.index(i)
            if isinstance(i, _ast.ClassDef) and i.name == 'JenkinsServer':
                # print(jenkins_node.body[i_index])
                for j in i.body:
                    j_index = i.body.index(j)
                    if isinstance(j, _ast.FunctionDef) and j.name in jenkins_map_dict.keys():
                        jenkins_node.body[i_index].body[j_index] = jenkins_map_dict[j.name]
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

