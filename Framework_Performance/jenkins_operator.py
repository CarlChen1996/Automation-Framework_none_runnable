# -*- coding: utf-8 -*-
# @Time   : 2019/5/29 16:48
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : jenkins_class.py
# @Project : jenkins
import time


class JenkinsServer():
    def create_job(self, job_name, job_config_file):
        print('jenkins create build job,wait 20s')
        time.sleep(20)
        return True

    def initial_job_configuration(self, need_build):
        print('building,wait 20s')
        time.sleep(20)
        return True

    def delete_job(self, job_name):
        print('delete job,wait 20s')
        time.sleep(20)

    def build_job(self, job_name):
        print('build_job,wait 20s')
        time.sleep(20)
        return True

    def get_last_build_number(self, job_name):
        build_number = time.time()
        print(build_number)
        time.sleep(1)
        return build_number

    def get_build_result(self, job_name, build_number):
        result = 'SUCCESS'
        print('get build result,wait 20')
        time.sleep(20)
        return result
