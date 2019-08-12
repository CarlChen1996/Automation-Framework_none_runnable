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

    def validate_http(self):
        pass


class ScriptValidator(Validator):
    # To validate github .py file.
    def validate(self, task):
        print('validate ' + task.get_name() + ' scripts finished')
        # controller_log.info('validate ' + task.get_name() + ' scripts finished')
        return True





if __name__ == '__main__':
    from Framework_Kernel.host import WindowsExecuteHost
    h = WindowsExecuteHost(ip='15.83.248.251',mac='12121212212')
    a = HostValidator()
    b = a.validate_uut(h)
    print(b)

