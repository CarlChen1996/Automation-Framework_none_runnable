# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:23 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : Validator.py
# @Project : Automation-Framework
import shlex
import subprocess
from Framework_Kernel.log import configuration_log, assemble_log, execution_log
import ftplib

class Validator:
    def validate(self, name):
        print('validate finished')

    def ping(self,ip):
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

    def validate_build_server(self,host):
        result = self.ping(host.get_ip())
        if result:
            configuration_log.info('validate_build_server ' + host.get_ip() + ' pass')
            host.status = 'on'
            return True
        else:
            configuration_log.info('validate_build_server ' + host.get_ip() + ' fail')
            host.status = 'off'
            return False

    def validate_deploy_server(self, host):
        result = self.ping(host.get_ip())
        if result:
            configuration_log.info('validate_deploy_server ' + host.get_ip() + ' pass')
            host.status = 'on'
            return True
        else:
            configuration_log.info('validate_deploy_server ' + host.get_ip() + ' fail')
            host.status = 'off'
            return False

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
            ftplib.FTP(ftp_settings['server_address']).login(ftp_settings['username'], ftp_settings['password'])
            execution_log.info('validate_ftp '+ftp_settings['server_address']+' success')
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


