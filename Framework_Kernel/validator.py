# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:23 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : Validator.py
# @Project : Automation-Framework
import shlex
import subprocess

import paramiko
import pythoncom

from Framework_Kernel.log import configuration_log, assemble_log, execution_log
from Common_Library.file_transfer import FTPUtils
from win32com.client import DispatchEx


class Validator:
    def validate(self, name):
        print('validate finished')

    def ping(self, ip):
        cmd = "ping -n 1 {}".format(ip)
        args = shlex.split(cmd)
        try:
            subprocess.check_call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True

        except subprocess.CalledProcessError:
            return False


class HostValidator(Validator):
    def validate(self, host):
        print('validate ' + host.get_ip() + ' pass')
        # controller_log.info('validate ' + host.get_hostname() + ' finished')
        return True

    def validate_build_server(self, host):
        result = self.ping(host.get_ip())
        if result:
            configuration_log.info('validate_build_server ' + host.get_ip() + ' pass')
            host.status = 'on'
            return True
        else:
            configuration_log.info('validate_build_server ' + host.get_ip() + ' fail')
            host.status = 'off'
            return False

    @staticmethod
    def __validate_QTP(host):
        try:
            pythoncom.CoInitialize()
            DispatchEx('QuickTest.Application', host.get_ip())
            pythoncom.CoUninitialize()
            return True
        except Exception as e:
            configuration_log.info(e)
            return False

    @staticmethod
    def __validate_HPDM(host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh.connect(host.get_ip(), 22, host.get_username(), host.get_password())
        stdin, stdout, stderr = ssh.exec_command("sc queryex HPDMServer")
        res = stdout.readlines
        if 'OPENSERVICE FAILED 1060' in res[0].upper():
            configuration_log.info('validate_deploy_server ' + host.get_ip() +
                               ' fail, HPDM service not exist')
            return False
        for i in res:
            if 'STATE' in i.upper():
                # sample: STATE              : 4  RUNNING
                if i.split(":")[1].strip().split(" ")[-1].upper() == 'RUNNING':
                    return True
                else:
                    configuration_log.info('validate_deploy_server ' + host.get_ip() +
                                       ' fail, HPDM service is not running')
                    return False

    def validate_deploy_server(self, host):
        if not self.__validate_QTP(host):
            host.status = 'off'
            configuration_log.info('validate_deploy_server ' + host.get_ip() +
                                ' fail, QTP check fail')
            return False
        if not self.__validate_HPDM(host):
            host.status = 'off'
            configuration_log.info('validate_deploy_server ' + host.get_ip() +
                                ' fail, HPDM check fail')
            return False
        host.status = 'off'
        configuration_log.info('validate_deploy_server ' + host.get_ip() + ' pass')
        return True

    def validate_uut(self, host):
        result = self.ping(host.get_ip())
        if result:
            assemble_log.info('validate_uut ' + host.get_ip() + ' pass')
            host.status = 'on'
            return True
        else:
            assemble_log.info('validate_uut ' + host.get_ip() + ' fail')
            host.status = 'off'
            return False

    @staticmethod
    def validate_ftp(ftp_settings):
        try:
            ftp = FTPUtils(ftp_settings['server_address'], ftp_settings['username'], ftp_settings['password'])
            ftp.close()
            execution_log.info('validate_ftp ' + ftp_settings['server_address'] + ' success')
            return True
        except Exception as e:
            execution_log.error(e)
            return False


class ScriptValidator(Validator):
    # To validate github .py file.
    def validate(self, task):
        print('validate ' + task.get_name() + ' scripts finished')
        # controller_log.info('validate ' + task.get_name() + ' scripts finished')
        return True


if __name__ == '__main__':
    pass
