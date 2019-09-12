# -*- coding: utf-8 -*-
# @Time    : 9/12/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_host.py
# @Project : Automation-Framework
from Common_Library.jenkins_operator import JenkinsServer
from Framework_Kernel import host, task
from unittest.mock import patch
import unittest
import jenkins

'''
setUp: instantiated Task, jenkins_server and host.Build
test_connect_jenkins_true: connect jenkins with correct url, username, token
test_connect_jenkins_false: connect jenkins with incorrect url, username, token
test_connect_jenkins_mock: connect jenkins can called when build task
test_create_job: test jenkins build job with parameter
test_get_result: test get result after build job success
'''


class HostTest(unittest.TestCase):
    def setUp(self):
        self.task = task.Task(name='test')
        self.task.insert_script('1')
        self.build_task = host.Build()
        self.jenkins_build = host.Build()
        self.jenkins_host = JenkinsServer()

    def test_connect_jenkins_true(self):
        jenkins_host = JenkinsServer().connect()
        self.assertIsInstance(jenkins_host, jenkins.Jenkins)

    def test_connect_jenkins_false(self):
        jenkins_host = JenkinsServer()
        jenkins_host.username = 'test'
        self.assertFalse(jenkins_host.connect())

    @patch('Framework_Kernel.host.Build.jenkins_parameter')
    @patch('Framework_Kernel.host.Build.build_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.connect')
    def test_connect_jenkins_mock(self, connect_mock, build_job_mock, jenkins_parameter_mock):
        self.jenkins_build.jenkins_build(self.task)
        connect_mock.assert_called_once()

    @patch('Framework_Kernel.host.Build.get_unique_job_name')
    @patch('Common_Library.jenkins_operator.JenkinsServer.get_last_build_number')
    @patch('Common_Library.jenkins_operator.JenkinsServer.initial_job_configuration')
    @patch('Common_Library.jenkins_operator.JenkinsServer.build_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.is_job_exist')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    @patch('jenkins.Jenkins.create_job')
    def test_create_job(self, create_mock, delete_mock, job_exist_mock, build_mock, initial_mock, last_number_mock,
                        unique_job_mock):
        initial_mock.return_value = True
        job_exist_mock.return_value = True
        unique_job_mock.return_value = True
        build_mock.return_value = False
        last_number_mock.return_value = True
        job_os = 'windows'
        self.jenkins_host.connection = self.jenkins_host.connect()
        self.assertTrue(self.jenkins_build.build_job(self.task, self.jenkins_host, job_os))
        create_mock.assert_called_once_with(unique_job_mock.return_value, initial_mock.return_value)

    @patch('Common_Library.jenkins_operator.JenkinsServer.initial_job_configuration')
    @patch('Framework_Kernel.host.Build.get_unique_job_name')
    @patch('Common_Library.jenkins_operator.JenkinsServer.get_last_build_number')
    @patch('Common_Library.jenkins_operator.JenkinsServer.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.build_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    @patch('jenkins.Jenkins.get_build_info')
    def test_get_result(self, result_mock, delete_mock, build_mock, create_mock, last_number_mock, unique_job_mock,
                        initial_mock):
        last_number_mock.side_effect = [1, 2, 2]
        unique_job_mock.return_value = True
        create_mock.return_value = True
        build_mock.return_value = True
        result_mock.return_value = {'result': 'SUCCESS'}
        job_os = 'windows'
        self.jenkins_host.job_params['publish_path'] = '1'
        self.jenkins_host.job_params['result_file'] = '2'
        self.jenkins_host.connection = self.jenkins_host.connect()
        self.assertTrue(self.jenkins_build.build_job(self.task, self.jenkins_host, job_os))
        result_mock.assert_called_once_with(unique_job_mock.return_value, 2)
        self.assertIn('/jenkins/windows/{0}/{1}.exe'.format(self.jenkins_host.job_params['publish_path'],
                                                            self.jenkins_host.job_params['result_file']),
                      self.task.get_exe_file_list())
