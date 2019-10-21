# -*- coding: utf-8 -*-
# @Time   : 2019/5/29 16:48
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : jenkins_class.py
# @Project : jenkins


import jenkins
import time
import os
from lxml import etree as et
from Framework_Kernel.analyzer import Analyzer
from Framework_Kernel.log import assemble_log


class JenkinsServer():
    def __init__(self):
        self.settings = self.__load_settings()
        self.url = self.settings['server_address']
        self.username = self.settings['username']
        self.token = self.settings['token']
        self.connection: jenkins.Jenkins = None
        self.job_params = {
            'os_type': None,
            'repository': None,
            'build_node': None,
            'template_file': None,
            'entry_file': None,
            'result_file': None,
            'publish_path': None,
            'email_to': None
        }
        self.config_module_win = os.path.join(os.getcwd(), self.settings['build_job_windows'])
        self.config_module_linux = os.path.join(os.getcwd(), self.settings['build_job_linux'])

    def __load_settings(self):
        config_file = os.path.join(os.getcwd(), r'.\Configuration\config_framework_list.yml')
        analyer = Analyzer()
        jenkins_settings = analyer.analyze_file(config_file)['jenkins_settings']
        return jenkins_settings

    def connect(self):
        try:
            self.connection = jenkins.Jenkins(self.url, username=self.username, password=self.token)
            self.connection.get_all_jobs()
        except Exception as e:
            assemble_log.info(str(e))
            self.connection = False
        return self.connection

    def create_job(self, job_name, job_config_file):
        print('jenkins create build job')
        return True

    # TODO release common library to parse xml and fake the implementation below
    def initial_job_configuration(self, need_build):
        try:
            print('@@@@@@@@@building,wait 10s@@@@@@@@')
            time.sleep(10)
            return True
        except Exception as e:
            assemble_log.info(str(e))

    def delete_job(self, job_name):
        try:
            print('delete job')
        except Exception as e:
            assemble_log.info(str(e))

    def is_job_exist(self, job_name):
        return self.connection.job_exists(job_name)

    def build_job(self, job_name):
        try:
            return True
        except Exception as e:
            assemble_log.info(str(e))
            return False

    def get_last_build_number(self, job_name):
        try:
            build_number = time.time()
            print(build_number)
            time.sleep(1)
            return build_number
        except Exception as e:
            assemble_log.info(str(e))
            return False

    def get_build_result(self, job_name, build_number):
        try:
            while True:
                result = 'SUCCESS'
                if result:
                    return result
                else:
                    assemble_log.info("wait {} build {} result".format(job_name, build_number))
                    time.sleep(5)
        except Exception as e:
            assemble_log.info(str(e))
            return False

    def is_node_exist(self, node_name):
        return self.connection.node_exists(node_name)

    def is_node_online(self, node_name):
        node_info = self.connection.get_node_info(node_name, 0)
        is_off = node_info['offline']
        status = not is_off
        return status

    def get_jenkins_node_state(self, host_name):
        node_info = self.connection.get_node_info(host_name)
        if node_info.get('idle'):
            return 'Idle'
        else:
            return 'Busy'
