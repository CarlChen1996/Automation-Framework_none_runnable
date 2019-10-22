# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:23 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : Validator.py
# @Project : Automation-Framework
import os
import yaml
from Framework_Kernel.log import configuration_log, execution_log


class Validator:
    pass


class HostValidator(Validator):
    def validate_build_server(self, host):
        result = True
        if result:
            configuration_log.info('validate_build_server ' + host.get_ip() + ' pass')
            host.status = 'on'
            return True

    @staticmethod
    def __validate_QTP(host):
        return True


    @staticmethod
    def __validate_HPDM(host):
        return True

    @staticmethod
    def validate_ftp(ftp_settings):
        execution_log.info('validate_ftp ' + ftp_settings['server_address'] + ' success')
        return True


class ScriptValidator(Validator):
    # To validate github .py file.
    def validate(self, task):
        print('validate ' + task.get_name() + ' scripts finished')
        return True


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
    # self.generate_scripts_config(task)
    return task

def __load_uut_result(self):
    result = []
    if not os.path.exists(self.__test_report_root):
        os.makedirs(self.__test_report_root)
    result_file = os.path.join(self.__test_report_root, 'result.yaml')
    for i in self.__uut_list:
        uut_result_file = os.path.join(self.__test_report_root, '{}\\test_report\\{}.yaml'.format(i.get_ip(), i.get_ip()))
        if not os.path.exists(uut_result_file):
            empty_result = [{
                'uut_name': i.get_ip(),
                'case_name': 'No result return',
                'steps': [],
                'result': 'fail'
            },{
                'uut_name': i.get_ip(),
                'case_name': 'No result return',
                'steps': [],
                'result': 'pass'
            }]
            result.extend(empty_result)
            continue
        with open(uut_result_file, encoding='utf-8') as f:
            empty_result = yaml.safe_load(f.read())
            result.extend(empty_result)
    with open(result_file, 'w', encoding='utf-8') as g:
        yaml.dump(result, g)
    return result


if __name__ == '__main__':
    h = Validator()
    print()
