# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
import sys
import os
import time
from Framework_Kernel.log import assemble_log, execution_log
from Framework_Kernel import QTPutils
from Framework_Kernel.analyzer import Analyzer
from Common_Library import file_operator, file_transfer, jenkins_operator
from Framework_Kernel.validator import HostValidator
import datetime


class Host:
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        self.__ip = ip
        self.__hostname = hostname
        self.__version = version
        self.__mac = mac
        self.__username = username
        self.__password = password
        self.__domain = domain
        self.status = status
        self.state = 'Idle'

    def start(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def reboot(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def shutdown(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def get_ip(self):
        return self.__ip

    def get_hostname(self):
        return self.__hostname

    def get_version(self):
        return self.__version

    def get_mac(self):
        return self.__mac

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_domain(self):
        return self.__domain


class WindowsHost(Host):
    pass


class LinuxHost(Host):
    pass


class Build:
    def __init__(self):
        self.log = assemble_log

    def get_scripts(self, task):
        # for script in task.get_script_list():
        pass
        # self.log.info('get  {} scripts PASS'.format(task.get_name()))

    def jenkins_build(self, task):
        jenkins_host = jenkins_operator.JenkinsServer()
        if not jenkins_host.connect():
            return False
        job_os = self.get_os_type(task)
        self.jenkins_parameter(task, jenkins_host, job_os)
        return self.build_job(task, jenkins_host, job_os)

    def jenkins_parameter(self, task, jenkins_host, job_os):
        build_time = str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        self.job_name = task.get_name() + build_time
        if job_os == 'windows':
            jenkins_host.job_params = {
                'os_type': job_os,
                'repository': task.get_repository(),
                'build_node': self._Host__hostname,
                'template_file': jenkins_host.config_module_win,
                'entry_file': 'run.py',
                'result_file': 'run',
                'publish_path': self.job_name,
                'email_to': task.get_email()
            }
        elif job_os == 'linux':
            jenkins_host.job_params = {
                'os_type': job_os,
                'repository': task.get_repository(),
                'build_node': self._Host__hostname,
                'template_file': jenkins_host.config_module_linux,
                'entry_file': 'run.py',
                'result_file': 'run',
                'publish_path': self.job_name,
                'email_to': task.get_email()
            }

    def build_job(self, task, jenkins_host, job_os):
        last_build_number = jenkins_host.get_last_build_number(self.job_name)
        if jenkins_host.create_job(self.job_name, jenkins_host.initial_job_configuration()) and jenkins_host.build_job(self.job_name):
            while last_build_number == jenkins_host.get_last_build_number(self.job_name):
                # self.log.info('New build record is not available, wait 5 seconds')
                time.sleep(5)
            current_build_number = jenkins_host.get_last_build_number(self.job_name)
            build_result = jenkins_host.get_build_result(self.job_name, current_build_number)
            task.set_status(build_result)
            jenkins_host.delete_job(self.job_name)
            if build_result == 'SUCCESS':
                if job_os == 'windows':
                    task.insert_exe_file_list(
                        r'/jenkins/windows/' + jenkins_host.job_params['publish_path'] + r'/' + jenkins_host.job_params['result_file'] + '.exe')
                elif job_os == 'linux':
                    task.insert_exe_file_list(r'/jenkins/linux/' + jenkins_host.job_params['publish_path'] + r'/' + jenkins_host.job_params['result_file'])
            task.folder_name = task.get_exe_file_list()[0].split('/')[-2]
        return task

    def get_os_type(self, task):
        build_server_os = ''
        for i in task.get_uut_list():
            if 'wes' in i.get_version().lower():
                build_server_os = 'windows'
            elif 'tp' in i.get_version().lower():
                build_server_os = 'linux'
        return build_server_os

    def build_task(self, task):
        # Check if script empty
        if not task.get_script_list():
            task.set_status("FAIL")
            return False
        jenkins_host_validator = HostValidator()
        if jenkins_host_validator.validate_jenkins_server():
            if not self.jenkins_build(task):
                return False
        else:
            return False
        # self.log.info('build ' + task.get_name() + task.get_status())
        self.generate_scripts_config(task)
        return task

    def generate_scripts_config(self, task):
        # self.log.info("generate script config file")
        scripts_config = os.path.join(os.getcwd(), 'script.yml')
        scripts = [{i.get_name(): i.get_status()} for i in task.get_script_list()]
        file_operator.YamlFile.save(scripts, scripts_config)
        store_dir = os.path.join(os.path.dirname(task.get_exe_file_list()[0]), 'test_data')
        # self.log.info("upload script config file to {}".format(store_dir))
        remote_base_path = store_dir
        # Retrive FTP Settings from configuration file
        config_file = os.path.join(os.getcwd(), r'.\Configuration\config_framework_list.yml')
        analyze_hanlder = Analyzer()
        ftp_settings = analyze_hanlder.analyze_file(config_file)['ftp_settings']
        ftp_util = file_transfer.FTPUtils(ftp_settings['server_address'], ftp_settings['username'],
                                          ftp_settings['password'])
        ftp_util.change_dir(remote_base_path)
        ftp_util.upload_file(scripts_config, 'script.yml')
        ftp_util.close()
        os.remove(scripts_config)


class Deploy:
    def __init__(self, host):
        self.log = execution_log
        self.host = host

    def deploy_task(self, task):
        QTPutils.HPDMOperator.deploy_task(task, self.host)
        self.log.info('deploy package: ' + task.get_name() + ' Pass')


class Execute:
    def __init__(self, host):
        self.log = execution_log
        self.host = host

    def execute_task(self, task):
        QTPutils.HPDMOperator.execute_task(self.host, task)
        self.log.info('execute {} on  {}'.format(
            task.get_name(),
            task.get_uut_list()[0].get_hostname()))

    def check_status(self, task):
        self.log.info('check {} status on {}'.format(
            task.get_name(),
            task.get_uut_list()[0].get_hostname()))

    def collect_result(self, task):
        QTPutils.HPDMOperator.get_result(task)
        self.log.info('collect {} result from {}'.format(
            task.get_name(),
            task.get_uut_list()[0].get_hostname()))


class WindowsBuildHost(WindowsHost, Build):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        WindowsHost.__init__(self, ip, mac, hostname, version, username,
                             password, domain, status)
        Build.__init__(self)


class LinuxBuildHost(LinuxHost, Build):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        LinuxHost.__init__(self, ip, mac, hostname, version, username, password, domain, status)
        Build.__init__(self)


class WindowsDeployHost(WindowsHost, Deploy):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        WindowsHost.__init__(self, ip, mac, hostname, version, username, password, domain, status)
        Deploy.__init__(self, self)


class WindowsExecuteHost(WindowsHost, Execute):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        WindowsHost.__init__(self, ip, mac, hostname, version, username,
                             password, domain, status)
        Execute.__init__(self, self)


class LinuxDeployHost(LinuxHost, Deploy):
    pass


class LinuxExecuteHost(LinuxHost, Execute):
    pass


if __name__ == "__main__":
    b = WindowsBuildHost("", "", "", "", "", "", "", "")
    b.build()
    d = WindowsDeployHost("", "", "", "", "", "", "", "")
    d.deploy_task()
    e = WindowsExecuteHost("", "", "", "", "", "", "", "")
    e.check_status()
    e.collect_result()
