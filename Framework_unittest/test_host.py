# -*- coding: utf-8 -*-
# @Time    : 9/12/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_host.py
# @Project : Automation-Framework
from Common_Library.jenkins_operator import JenkinsServer
from Framework_Kernel import host, task
from unittest.mock import patch, MagicMock
import unittest

'''
setUp: instantiated Task, jenkins_server and host.Build
test_connect_jenkins_mock: connect jenkins can called when build task
test_create_job: test jenkins build job with parameter
test_get_result: test get result after build job success
'''


class HostTest(unittest.TestCase):
    def setUp(self):
        self.task = task.Task(name='test')
        self.task.insert_script('1')
        self.jenkins_build = host.Build()
        self.jenkins_build.job_name = ''
        self.jenkins_host = JenkinsServer()

    @patch('Framework_Kernel.host.Build.jenkins_parameter')
    def test_connect_jenkins_mock(self, connect_mock):
        connect_mock.return_value = False
        build_result = self.jenkins_build.jenkins_build(self.task)
        connect_mock.assert_called_once()
        self.assertFalse(build_result)

    @patch('Framework_Kernel.host.Build.jenkins_parameter')
    @patch('Framework_Kernel.host.Build.build_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.connect')
    def test_connect_jenkins_mock(self, connect_mock, build_job_mock, jenkins_parameter_mock):
        connect_mock.return_value = True
        build_result = self.jenkins_build.jenkins_build(self.task)
        connect_mock.assert_called_once()
        self.assertIsInstance(build_result, MagicMock)

    @patch('Common_Library.jenkins_operator.JenkinsServer.get_last_build_number')
    @patch('Common_Library.jenkins_operator.JenkinsServer.initial_job_configuration')
    @patch('Common_Library.jenkins_operator.JenkinsServer.build_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.is_job_exist')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    @patch('jenkins.Jenkins.create_job')
    def test_create_job(self, create_mock, delete_mock, job_exist_mock, build_mock, initial_mock, last_number_mock, ):
        initial_mock.return_value = True
        job_exist_mock.return_value = True
        build_mock.return_value = False
        last_number_mock.return_value = True
        job_os = 'windows'
        self.jenkins_host.connection = self.jenkins_host.connect()
        self.assertTrue(self.jenkins_build.build_job(self.task, self.jenkins_host, job_os))
        create_mock.assert_called_once_with(self.jenkins_build.job_name, initial_mock.return_value)

    @patch('Common_Library.jenkins_operator.JenkinsServer.initial_job_configuration')
    @patch('Common_Library.jenkins_operator.JenkinsServer.get_last_build_number')
    @patch('Common_Library.jenkins_operator.JenkinsServer.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.build_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    @patch('jenkins.Jenkins.get_build_info')
    def test_get_result(self, result_mock, delete_mock, build_mock, create_mock, last_number_mock, initial_mock):
        last_number_mock.side_effect = [1, 2, 2]
        create_mock.return_value = True
        build_mock.return_value = True
        result_mock.return_value = {'result': 'SUCCESS'}
        job_os = 'windows'
        self.jenkins_host.job_params['publish_path'] = '1'
        self.jenkins_host.job_params['result_file'] = '2'
        self.jenkins_host.connection = self.jenkins_host.connect()
        self.assertTrue(self.jenkins_build.build_job(self.task, self.jenkins_host, job_os))
        result_mock.assert_called_once_with(self.jenkins_build.job_name, 2)
        self.assertIn('/jenkins/windows/{0}/{1}.exe'.format(self.jenkins_host.job_params['publish_path'],
                                                            self.jenkins_host.job_params['result_file']),
                      self.task.get_exe_file_list())

    @patch('Framework_Kernel.host.Build.generate_scripts_config')
    @patch('Framework_Kernel.host.Build.jenkins_build')
    @patch('Framework_Kernel.validator.HostValidator.validate_jenkins_server')
    @patch('Framework_Kernel.task.Task.get_script_list')
    def test_build_task(self, script_mock, validate_mock, build_mock, generate_scripts_mock):
        script_mock.return_value = True
        validate_mock.return_value = True
        build_mock.return_value = True
        self.assertEqual(self.jenkins_build.build_task(self.task), self.task)

    @patch('Framework_Kernel.task.Task.get_script_list')
    def test_build_task_false_none_scripts(self, script_mock):
        script_mock.return_value = False
        self.assertFalse(self.jenkins_build.build_task(self.task))
        self.assertEqual(self.task.get_status(), 'FAIL')

    @patch('Framework_Kernel.validator.HostValidator.validate_jenkins_server')
    @patch('Framework_Kernel.task.Task.get_script_list')
    def test_build_task_false_validate(self, script_mock, validate_mock):
        script_mock.return_value = True
        validate_mock.return_value = False
        self.assertFalse(self.jenkins_build.build_task(self.task))

    @patch('Framework_Kernel.host.Build.jenkins_build')
    @patch('Framework_Kernel.validator.HostValidator.validate_jenkins_server')
    @patch('Framework_Kernel.task.Task.get_script_list')
    def test_build_task_false_build(self, script_mock, validate_mock, build_mock):
        script_mock.return_value = True
        validate_mock.return_value = True
        build_mock.return_value = False
        print(self.task)
        print(self.jenkins_build.build_task)
        print(self.jenkins_build.build_task(self.task))
        self.assertFalse(self.jenkins_build.build_task(self.task))

    def test_get_os_type_windows(self):
        self.task.insert_uut_list(host.Host(ip='1.1.1.1', mac=666666, version='wes'))
        self.assertEqual(self.jenkins_build.get_os_type(self.task), 'windows')

    def test_get_os_type_linux(self):
        self.task.insert_uut_list(host.Host(ip='1.1.1.1', mac=666666, version='tp'))
        self.assertEqual(self.jenkins_build.get_os_type(self.task), 'linux')

    def test_get_os_type_none(self):
        self.task.insert_uut_list(host.Host(ip='1.1.1.1', mac=666666, version='win'))
        self.assertEqual(self.jenkins_build.get_os_type(self.task), '')

    def test_jenkins_parameter(self):
        pass

    def test_generate_scripts_config(self):
        pass
