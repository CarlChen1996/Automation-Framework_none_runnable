# -*- coding: utf-8 -*-
# @Time    : 9/24/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_task.py
# @Project : Automation-Framework
from Common_Library import jenkins_operator
from unittest.mock import patch
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
        self.node_name = 'unittest'

    def test_connect_jenkins_true(self):
        jenkins_host = self.jenkins.connect()
        self.assertIsInstance(jenkins_host, jenkins.Jenkins)

    def test_connect_jenkins_false(self):
        self.jenkins.username = 'test'
        self.assertFalse(self.jenkins.connect())

    @patch('jenkins.Jenkins.get_all_jobs')
    def test_connect_jenkins_mock(self, jobs_mock):
        jobs_mock.side_effect = EOFError
        self.assertFalse(self.jenkins.connect())

    @patch('Common_Library.jenkins_operator.JenkinsServer.is_job_exist')
    @patch('jenkins.Jenkins.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    def test_create_job(self, delete_mock, create_mock, exist_mock):
        exist_mock.side_effect = [True, True]
        self.assertTrue(self.jenkins.create_job(self.job_name, 'test'))
        create_mock.assert_called_once_with(self.job_name, 'test')
        delete_mock.assert_called_once()

    @patch('Common_Library.jenkins_operator.JenkinsServer.is_job_exist')
    @patch('jenkins.Jenkins.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    def test_create_job_none_job(self, delete_mock, create_mock, exist_mock):
        exist_mock.side_effect = [False, True]
        self.assertTrue(self.jenkins.create_job(self.job_name, 'test'))
        create_mock.assert_called_once_with(self.job_name, 'test')
        delete_mock.assert_not_called()

    @patch('Common_Library.jenkins_operator.JenkinsServer.is_job_exist')
    @patch('jenkins.Jenkins.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    def test_create_job_false(self, delete_mock, create_mock, exist_mock):
        exist_mock.side_effect = [True, False]
        self.assertFalse(self.jenkins.create_job(self.job_name, 'test'))
        create_mock.assert_called_once_with(self.job_name, 'test')
        delete_mock.assert_called_once()

    @patch('Common_Library.jenkins_operator.JenkinsServer.is_job_exist')
    @patch('jenkins.Jenkins.create_job')
    @patch('Common_Library.jenkins_operator.JenkinsServer.delete_job')
    def test_create_job_none_job_false(self, delete_mock, create_mock, exist_mock):
        exist_mock.side_effect = [False, False]
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

    @patch('jenkins.Jenkins.job_exists')
    def test_is_job_exist(self, exist_mock):
        self.jenkins.is_job_exist(self.job_name)
        exist_mock.assert_called_once_with(self.job_name)

    @patch('jenkins.Jenkins.build_job')
    def test_build_job(self, build_mock):
        build_mock.return_value = True
        self.assertTrue(self.jenkins.build_job(self.job_name))
        build_mock.assert_called_once_with(self.job_name)

    @patch('jenkins.Jenkins.build_job')
    def test_build_job_false(self, build_mock):
        build_mock.side_effect = EOFError
        self.assertFalse(self.jenkins.build_job(self.job_name))
        build_mock.assert_called_once_with(self.job_name)

    @patch('jenkins.Jenkins.get_job_info')
    def test_get_last_build_number(self, info_mock):
        info_mock.return_value = {'lastBuild': {'number': True}}
        self.assertTrue(self.jenkins.get_last_build_number(self.job_name))
        info_mock.assert_called_once_with(self.job_name)

    @patch('jenkins.Jenkins.get_job_info')
    def test_get_last_build_number_false(self, info_mock):
        info_mock.side_effect = EOFError
        self.assertFalse(self.jenkins.get_last_build_number(self.job_name))
        info_mock.assert_called_once_with(self.job_name)

    @patch('time.sleep')
    @patch('jenkins.Jenkins.get_build_info')
    def test_get_build_result(self, info_mock, sleep_mock):
        info_mock.side_effect = [{'result': None}, {'result': False}, {'result': True}]
        self.assertTrue(self.jenkins.get_build_result(self.job_name, 1))
        self.assertEqual(sleep_mock.call_count, 2)

    @patch('jenkins.Jenkins.get_build_info')
    def test_get_build_result_false(self, info_mock):
        info_mock.side_effect = EOFError
        self.assertFalse(self.jenkins.get_build_result(self.job_name, 1))

    @patch('jenkins.Jenkins.node_exists')
    def test_is_node_exist(self, node_mock):
        node_mock.return_value = True
        self.assertTrue(self.jenkins.is_node_exist(self.node_name))

    @patch('jenkins.Jenkins.node_exists')
    def test_is_node_exist_false(self, node_mock):
        node_mock.return_value = False
        self.assertFalse(self.jenkins.is_node_exist(self.node_name))

    @patch('jenkins.Jenkins.get_node_info')
    def test_is_node_online(self, node_mock):
        node_mock.return_value = {'offline': False}
        self.assertTrue(self.jenkins.is_node_online(self.node_name))

    @patch('jenkins.Jenkins.get_node_info')
    def test_is_node_online_false(self, node_mock):
        node_mock.return_value = {'offline': True}
        self.assertFalse(self.jenkins.is_node_online(self.node_name))

    @patch('jenkins.Jenkins.get_node_info')
    def test_get_jenkins_node_state_idle(self, node_mock):
        node_mock.return_value = {'idle': True}
        self.assertEqual(self.jenkins.get_jenkins_node_state(self.node_name), 'Idle')

    @patch('jenkins.Jenkins.get_node_info')
    def test_get_jenkins_node_state_busy(self, node_mock):
        node_mock.return_value = {'idle': False}
        self.assertEqual(self.jenkins.get_jenkins_node_state(self.node_name), 'Busy')
