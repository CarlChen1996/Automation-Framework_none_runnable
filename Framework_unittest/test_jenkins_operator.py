# -*- coding: utf-8 -*-
# @Time    : 9/24/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_task.py
# @Project : Automation-Framework
from Common_Library import jenkins_operator
from unittest.mock import patch, Mock
import jenkins
import unittest

'''
test_connect_jenkins_true: connect jenkins with correct url, username, token
test_connect_jenkins_false: connect jenkins with incorrect url, username, token
'''


class JenkinsTest(unittest.TestCase):
    def setUp(self):
        self.jenkins = jenkins_operator.JenkinsServer()
        self.job_name = 'unittest'
        self.jenkins.connection = jenkins.Jenkins(url=self.jenkins.url, username=self.jenkins.username,
                                                  password=self.jenkins.token)

    def test_connect_jenkins_true(self):
        jenkins_host = self.jenkins.connect()
        self.assertIsInstance(jenkins_host, jenkins.Jenkins)

    def test_connect_jenkins_false(self):
        self.jenkins.username = 'test'
        self.assertFalse(self.jenkins.connect())

    @patch('jenkins.Jenkins.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    def test_create_job(self, delete_mock, create_mock):
        jenkins_operator.JenkinsServer.is_job_exist = Mock(side_effect=[True, True])
        self.assertTrue(self.jenkins.create_job(self.job_name, 'test'))
        create_mock.assert_called_once_with(self.job_name, 'test')
        delete_mock.assert_called_once()

    @patch('jenkins.Jenkins.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    def test_create_job_none_job(self, delete_mock, create_mock):
        jenkins_operator.JenkinsServer.is_job_exist = Mock(side_effect=[False, True])
        self.assertTrue(self.jenkins.create_job(self.job_name, 'test'))
        create_mock.assert_called_once_with(self.job_name, 'test')
        delete_mock.assert_not_called()

    @patch('jenkins.Jenkins.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    def test_create_job_false(self, delete_mock, create_mock):
        jenkins_operator.JenkinsServer.is_job_exist = Mock(side_effect=[True, False])
        self.assertFalse(self.jenkins.create_job(self.job_name, 'test'))
        create_mock.assert_called_once_with(self.job_name, 'test')
        delete_mock.assert_called_once()

    @patch('jenkins.Jenkins.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    def test_create_job_none_job_false(self, delete_mock, create_mock):
        jenkins_operator.JenkinsServer.is_job_exist = Mock(side_effect=[False, False])
        self.assertFalse(self.jenkins.create_job(self.job_name, 'test'))
        create_mock.assert_called_once_with(self.job_name, 'test')
        delete_mock.assert_not_called()

    def test_initial_job_configuration(self):
        pass

    @patch('jenkins.Jenkins.delete_job')
    def test_delete_job(self, delete_mock):
        self.jenkins.delete_job(self.job_name)
        delete_mock.assert_called_once_with(self.job_name)

    @patch('Framework_Kernel.log.Log.info')
    @patch('jenkins.Jenkins.delete_job')
    def test_delete_job_except(self, delete_mock, log_mock):
        delete_mock.side_effect = AttributeError
        self.jenkins.delete_job(self.job_name)
        delete_mock.assert_called_once_with(self.job_name)
        log_mock.assert_called_once()
