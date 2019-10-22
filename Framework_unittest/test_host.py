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
        self.deploy_host = host.WindowsDeployHost('1.1.1.1', 111111)
        self.deploy = host.Deploy(self.deploy_host)
        self.host_father = host.Host('1.1.1.1', 111111)
        self.windows_host = host.WindowsHost('1.1.1.2', 222222)
        self.linux_host = host.LinuxHost('1.1.1.3', 333333)
        self.windows_build_host = host.WindowsBuildHost('1.1.1.4', 444444)
        self.linux_build_host = host.LinuxBuildHost('1.1.1.5', 555555)
        self.windows_deploy_host = host.WindowsDeployHost('1.1.1.6', 666666)
        self.linux_deploy_host = host.LinuxDeployHost('1.1.1.7', 777777)
        self.windows_execute_host = host.WindowsExecuteHost('1.1.1.8', 888888)
        self.linux_execute_host = host.LinuxExecuteHost('1.1.1.9', 999999)

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

    @patch('Framework_Kernel.QTPutils.HPDMOperator.deploy_task')
    def test_deploy_task(self, deploy_mock):
        self.deploy.deploy_task(self.task)
        deploy_mock.assert_called_once_with(self.task, self.deploy_host)

    def test_get_ip(self):
        self.assertEqual(self.host_father.get_ip(), '1.1.1.1')
        self.assertEqual(self.windows_host.get_ip(), '1.1.1.2')
        self.assertEqual(self.linux_host.get_ip(), '1.1.1.3')
        self.assertEqual(self.windows_build_host.get_ip(), '1.1.1.4')
        self.assertEqual(self.linux_build_host.get_ip(), '1.1.1.5')
        self.assertEqual(self.windows_deploy_host.get_ip(), '1.1.1.6')
        self.assertEqual(self.linux_deploy_host.get_ip(), '1.1.1.7')
        self.assertEqual(self.windows_execute_host.get_ip(), '1.1.1.8')
        self.assertEqual(self.linux_execute_host.get_ip(), '1.1.1.9')

    def test_get_hostname(self):
        hostname = ''
        self.assertEqual(self.host_father.get_hostname(), hostname)
        self.assertEqual(self.windows_host.get_hostname(), hostname)
        self.assertEqual(self.linux_host.get_hostname(), hostname)
        self.assertEqual(self.windows_build_host.get_hostname(), hostname)
        self.assertEqual(self.linux_build_host.get_hostname(), hostname)
        self.assertEqual(self.windows_deploy_host.get_hostname(), hostname)
        self.assertEqual(self.linux_deploy_host.get_hostname(), hostname)
        self.assertEqual(self.windows_execute_host.get_hostname(), hostname)
        self.assertEqual(self.linux_execute_host.get_hostname(), hostname)

    def test_get_version(self):
        version = ''
        self.assertEqual(self.host_father.get_version(), version)
        self.assertEqual(self.windows_host.get_version(), version)
        self.assertEqual(self.linux_host.get_version(), version)
        self.assertEqual(self.windows_build_host.get_version(), version)
        self.assertEqual(self.linux_build_host.get_version(), version)
        self.assertEqual(self.windows_deploy_host.get_version(), version)
        self.assertEqual(self.linux_deploy_host.get_version(), version)
        self.assertEqual(self.windows_execute_host.get_version(), version)
        self.assertEqual(self.linux_execute_host.get_version(), version)

    def test_get_mac(self):
        self.assertEqual(self.host_father.get_mac(), 111111)
        self.assertEqual(self.windows_host.get_mac(), 222222)
        self.assertEqual(self.linux_host.get_mac(), 333333)
        self.assertEqual(self.windows_build_host.get_mac(), 444444)
        self.assertEqual(self.linux_build_host.get_mac(), 555555)
        self.assertEqual(self.windows_deploy_host.get_mac(), 666666)
        self.assertEqual(self.linux_deploy_host.get_mac(), 777777)
        self.assertEqual(self.windows_execute_host.get_mac(), 888888)
        self.assertEqual(self.linux_execute_host.get_mac(), 999999)

    def test_get_username(self):
        username = ''
        self.assertEqual(self.host_father.get_username(), username)
        self.assertEqual(self.windows_host.get_username(), username)
        self.assertEqual(self.linux_host.get_username(), username)
        self.assertEqual(self.windows_build_host.get_username(), username)
        self.assertEqual(self.linux_build_host.get_username(), username)
        self.assertEqual(self.windows_deploy_host.get_username(), username)
        self.assertEqual(self.linux_deploy_host.get_username(), username)
        self.assertEqual(self.windows_execute_host.get_username(), username)
        self.assertEqual(self.linux_execute_host.get_username(), username)

    def test_get_password(self):
        password = ''
        self.assertEqual(self.host_father.get_password(), password)
        self.assertEqual(self.windows_host.get_password(), password)
        self.assertEqual(self.linux_host.get_password(), password)
        self.assertEqual(self.windows_build_host.get_password(), password)
        self.assertEqual(self.linux_build_host.get_password(), password)
        self.assertEqual(self.windows_deploy_host.get_password(), password)
        self.assertEqual(self.linux_deploy_host.get_password(), password)
        self.assertEqual(self.windows_execute_host.get_password(), password)
        self.assertEqual(self.linux_execute_host.get_password(), password)

    def test_get_domain(self):
        domain = ''
        self.assertEqual(self.host_father.get_domain(), domain)
        self.assertEqual(self.windows_host.get_domain(), domain)
        self.assertEqual(self.linux_host.get_domain(), domain)
        self.assertEqual(self.windows_build_host.get_domain(), domain)
        self.assertEqual(self.linux_build_host.get_domain(), domain)
        self.assertEqual(self.windows_deploy_host.get_domain(), domain)
        self.assertEqual(self.linux_deploy_host.get_domain(), domain)
        self.assertEqual(self.windows_execute_host.get_domain(), domain)
        self.assertEqual(self.linux_execute_host.get_domain(), domain)

    @patch('Framework_Kernel.host.Build.build_task')
    def test_host_build_call(self, build_mock):
        self.windows_build_host.build_task(self.task)
        build_mock.assert_called_once_with(self.task)
        build_mock.reset_mock()
        self.linux_build_host.build_task(self.task)
        build_mock.assert_called_once_with(self.task)

    @patch('Framework_Kernel.host.Deploy.deploy_task')
    def test_host_deploy_call(self, deploy_mock):
        self.windows_deploy_host.deploy_task(self.task)
        deploy_mock.assert_called_once_with(self.task)
        deploy_mock.reset_mock()
        self.linux_deploy_host.deploy_task(self.task)
        deploy_mock.assert_called_once_with(self.task)

    @patch('Framework_Kernel.host.Execute.collect_result')
    def test_host_execute_call(self, execute_mock):
        self.windows_execute_host.collect_result(self.task)
        execute_mock.assert_called_once_with(self.task)
        execute_mock.reset_mock()
        self.linux_execute_host.collect_result(self.task)
        execute_mock.assert_called_once_with(self.task)
