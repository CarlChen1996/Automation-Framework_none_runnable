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
        if self.is_job_exist(job_name):
            self.delete_job(job_name)
        self.connection.create_job(job_name, job_config_file)
        if self.is_job_exist(job_name):
            return True
        else:
            return False

    # TODO release common library to parse xml and replace the implementation below
    def initial_job_configuration(self, need_build):
        try:
            with open(self.job_params['template_file']) as f:
                ele_tree: et._ElementTree = et.parse(f)
                # Update Repository
                ele_repository = ele_tree.xpath(r"./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
                if ele_repository:
                    ele_repository[0].text = self.job_params['repository']
                else:
                    assemble_log.info("Repository Module doesn't exist in the template file!")
                    return False
                # Update Command
                if self.job_params['os_type'] == "windows":
                    ele_builder = ele_tree.xpath(r"./builders/hudson.tasks.BatchFile/command")
                elif self.job_params['os_type'] == "linux":
                    ele_builder = ele_tree.xpath(r"./builders/hudson.tasks.Shell/command")
                else:
                    assemble_log.info("Unknow os_type value: {}".format(self.job_params['os_type']))
                    return False
                if ele_builder:
                    if need_build:
                        ele_builder[0].text = ele_builder[0].text.replace("hello.py", self.job_params['entry_file'])
                        ele_builder[0].text = ele_builder[0].text.replace("output_name", self.job_params['result_file'])
                    else:
                        ele_builder[0].text = r"echo Don't need to build!"
                else:
                    assemble_log.info("Command Module doesn't exist in the template file!")
                    return False
                # Update Node
                ele_build_node = ele_tree.xpath(r"./assignedNode")
                if ele_build_node:
                    ele_build_node[0].text = self.job_params['build_node']
                else:
                    assemble_log.info("Node Module doesn't exist in the template file!")
                    return False
                # Update the publish path(FTP)
                ele_publisher_node = ele_tree.xpath(r"//jenkins.plugins.publish__over__ftp.BapFtpTransfer/remoteDirectory")
                if ele_publisher_node:
                    ele_publisher_node[0].text = ele_publisher_node[0].text.replace('${JOB_NAME}', self.job_params['publish_path'])
                # Update the job notification
                ele_mail_list = ele_tree.xpath(r'./publishers/hudson.tasks.Mailer/recipients')
                if ele_mail_list:
                    ele_mail_list[0].text = ",".join(self.job_params['email_to'])
                # Return file stream instead of save temporary file
                file_stream = et.tostring(ele_tree.getroot(), encoding="UTF-8").decode("utf-8")
                return file_stream
        except Exception as e:
            assemble_log.info(str(e))

    def delete_job(self, job_name):
        try:
            self.connection.delete_job(job_name)
        except Exception as e:
            assemble_log.info(str(e))

    def is_job_exist(self, job_name):
        return self.connection.job_exists(job_name)

    def build_job(self, job_name):
        try:
            queue_item = self.connection.build_job(job_name)
            return queue_item
        except Exception as e:
            assemble_log.info(str(e))
            return False

    def get_last_build_number(self, job_name):
        try:
            build_number = self.connection.get_job_info(job_name)['lastBuild']['number']
            return build_number
        except Exception as e:
            assemble_log.info(str(e))
            return False

    def get_build_result(self, job_name, build_number):
        try:
            while True:
                result = self.connection.get_build_info(job_name, build_number)['result']
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
