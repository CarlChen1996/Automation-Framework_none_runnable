# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:23 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : Validator.py
# @Project : Automation-Framework
import shlex
import subprocess
from Framework_Kernel.log import configuration_log,assemble_log


class Validator:
    def validate(self, name):
        print('validate finished')


class HostValidator(Validator):
    def validate(self, host):
        print('validate ' + host.get_ip() + ' pass')
        # controller_log.info('validate ' + host.get_hostname() + ' finished')
        return True

    @staticmethod
    def validate_build_server(host):
        result = ping(host.get_ip())
        if result:
            configuration_log.info('validate ' + host.get_ip() + ' pass')
            host.status = 'on'
            return True
        else:
            configuration_log.info('validate ' + host.get_ip() + ' fail')
            host.status = 'off'
            return False

    @staticmethod
    def validate_deploy_server(host):
        result = ping(host.get_ip())
        if result:
            configuration_log.info('validate ' + host.get_ip() + ' pass')
            host.status = 'on'
            return True
        else:
            configuration_log.info('validate ' + host.get_ip() + ' fail')
            host.status = 'off'
            return False

    @staticmethod
    def validate_uut(host):
        result = ping(host.get_ip())
        if result:
            assemble_log.info('validate ' + host.get_ip() + ' pass')
            host.status = 'on'
            return True
        else:
            assemble_log.info('validate ' + host.get_ip() + ' fail')
            host.status = 'off'
            return False

    def validate_http(self):
        pass


class ScriptValidator(Validator):
    def validate(self, task):
        print('validate ' + task.get_name() + ' scripts finished')
        # controller_log.info('validate ' + task.get_name() + ' scripts finished')
        return True


def ping(ip):
    cmd = "ping -n 1 {}".format(ip)
    args = shlex.split(cmd)
    try:
        subprocess.check_call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True

    except subprocess.CalledProcessError:
        return False


if __name__ == '__main__':
    from Framework_Kernel.host import WindowsExecuteHost
    h=WindowsExecuteHost(ip='15.83.248.251',mac='12121212212')
    a=HostValidator.validate_uut(h)
    print(a)

