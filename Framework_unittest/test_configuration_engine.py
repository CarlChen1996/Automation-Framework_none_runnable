# -*- coding: utf-8 -*-
# @Time    : 9/17/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_configuration_engine.py
# @Project : Automation-Framework
from Framework_Kernel import configuration_engine, host
from unittest.mock import patch
import unittest

'''
setUp: instantiated Configuration Engine and WindowsBuildHost, LinuxBuildHost, WindowsDeployHost
test_run: test for configuration_engine.run
test_analyze_server_file_mock: test analyze server file can get correct return value by mock
test_analyze_server_file: test analyze server file can get correct return value
test_init_server: init server when server is True
test_init_server_false: init server when server is False
test_validate_server: validate server
test_validate_server_false_mock_windows_build: validate server fail
test_validate_server_false_mock_Linux_build: validate server fail
test_validate_server_false_mock_deploy: validate server fail
test_validate_server_false: validate with incorrect server
'''


class ConfigurationEngineTest(unittest.TestCase):
    def setUp(self):
        self.configuration = configuration_engine.ConfigurationEngine()
        self.windows_build_server = host.WindowsBuildHost(ip='15.83.248.252', mac=27832784292,
                                                          hostname='Build_Node_W_1', version=1.0,
                                                          username='Automation', password='Shanghai2010', domain='sh')
        self.linux_build_server = host.LinuxBuildHost(ip='15.83.248.253', mac=27832784292, hostname='Build_Node_TP_1',
                                                      version=1.0,
                                                      username='automation', password='Shanghai2010', domain='sh')
        self.deploy_server = host.WindowsDeployHost(ip='15.83.248.251', mac=5666666, hostname='Deploy_Node_1',
                                                    version=1.0,
                                                    username='Administrator', password='Shanghai2010', domain=None)

    @patch('Framework_Kernel.configuration_engine.ConfigurationEngine.get_server_list')
    @patch('Framework_Kernel.configuration_engine.ConfigurationEngine._ConfigurationEngine__init_server')
    @patch('Framework_Kernel.configuration_engine.ConfigurationEngine.validate_server')
    def test_run(self, validate_mock, init_server_mock, get_server_mock):
        get_server_mock.return_value = ['1']
        init_server_mock.return_value = '2'
        validate_mock.return_value = True
        validate_server = self.configuration.run()
        self.assertEqual(self.configuration.receive_signal.recv(), list(init_server_mock.return_value))
        self.assertEqual(validate_server, list(init_server_mock.return_value))

    @patch('Framework_Kernel.analyzer.Analyzer.analyze_file')
    def test_analyze_server_file_mock(self, analyze_file_mock):
        self.assertEqual(self.configuration.get_server_list(), analyze_file_mock.return_value)

    def test_analyze_server_file(self):
        self.assertEqual(self.configuration.get_server_list(),
                         [{'name': 'Build_Node_W_1', 'os': 'windows', 'function': 'build',
                           'hostname': 'Build_Node_W_1', 'ip': '15.83.248.252', 'mac': 27832784292,
                           'version': 1.0, 'username': 'Automation', 'password': 'Shanghai2010', 'domain': 'sh'},
                          {'name': 'Build_Node_W_2', 'os': 'windows', 'function': 'build',
                           'hostname': 'Build_Node_W_2', 'ip': '15.83.248.207', 'mac': 27832784292,
                           'version': 1.0, 'username': 'Automation', 'password': 'Shanghai2010', 'domain': 'sh'},
                          {'name': 'Build_Node_TP_1', 'os': 'linux', 'function': 'build',
                           'hostname': 'Build_Node_TP_1', 'ip': '15.83.248.253', 'mac': 27832784292,
                           'version': 1.0, 'username': 'automation', 'password': 'Shanghai2010', 'domain': 'sh'},
                          {'name': 'Deploy_Node_1', 'os': 'windows', 'function': 'deploy',
                           'hostname': 'Deploy_Node_1', 'ip': '15.83.248.251', 'mac': 5666666,
                           'version': 1.0, 'username': 'Administrator', 'password': 'Shanghai2010', 'domain': None},
                          {'name': 'Deploy_Node_2', 'os': 'windows', 'function': 'deploy',
                           'hostname': 'Deploy_Node_2', 'ip': '15.83.248.204', 'mac': 5666666,
                           'version': 1.0, 'username': 'Administrator', 'password': 'Shanghai2010', 'domain': None}])

    def test_init_server(self):
        server_item = {'name': 'Build_Node_W_1', 'os': 'windows', 'function': 'build',
                       'hostname': 'Build_Node_W_1', 'ip': '15.83.248.252', 'mac': 27832784292,
                       'version': 1.0, 'username': 'Automation', 'password': 'Shanghai2010', 'domain': 'sh'}
        self.assertIsInstance(self.configuration._ConfigurationEngine__init_server(server_item), host.WindowsBuildHost)
        server_item = {'name': 'Build_Node_W_1', 'os': 'windows', 'function': 'deploy',
                       'hostname': 'Build_Node_W_1', 'ip': '15.83.248.252', 'mac': 27832784292,
                       'version': 1.0, 'username': 'Automation', 'password': 'Shanghai2010', 'domain': 'sh'}
        self.assertIsInstance(self.configuration._ConfigurationEngine__init_server(server_item), host.WindowsDeployHost)
        server_item = {'name': 'Build_Node_W_1', 'os': 'linux', 'function': 'build',
                       'hostname': 'Build_Node_W_1', 'ip': '15.83.248.252', 'mac': 27832784292,
                       'version': 1.0, 'username': 'Automation', 'password': 'Shanghai2010', 'domain': 'sh'}
        self.assertIsInstance(self.configuration._ConfigurationEngine__init_server(server_item), host.LinuxBuildHost)
        server_item = {'name': 'Build_Node_W_1', 'os': 'linux', 'function': 'deploy',
                       'hostname': 'Build_Node_W_1', 'ip': '15.83.248.252', 'mac': 27832784292,
                       'version': 1.0, 'username': 'Automation', 'password': 'Shanghai2010', 'domain': 'sh'}
        self.assertIsInstance(self.configuration._ConfigurationEngine__init_server(server_item), host.LinuxDeployHost)

    def test_init_server_false(self):
        server_item = {'name': 'Build_Node_W_1', 'os': 'windows', 'function': 'b',
                       'hostname': 'Build_Node_W_1', 'ip': '15.83.248.252', 'mac': 27832784292,
                       'version': 1.0, 'username': 'Automation', 'password': 'Shanghai2010', 'domain': 'sh'}
        self.assertFalse(self.configuration._ConfigurationEngine__init_server(server_item))

    def test_validate_server(self):
        self.assertTrue(self.configuration.validate_server(self.windows_build_server))
        self.assertTrue(self.configuration.validate_server(self.linux_build_server))
        self.assertTrue(self.configuration.validate_server(self.deploy_server))

    @patch('Framework_Kernel.validator.HostValidator.validate_jenkins_server')
    def test_validate_server_false_mock_windows_build(self, validate_mock):
        validate_mock.return_value = False
        self.assertFalse(self.configuration.validate_server(self.windows_build_server))

    @patch('Framework_Kernel.validator.HostValidator.validate_jenkins_server')
    def test_validate_server_false_mock_Linux_build(self, validate_mock):
        validate_mock.return_value = False
        self.assertFalse(self.configuration.validate_server(self.linux_build_server))

    @patch('Framework_Kernel.validator.HostValidator.validate_deploy_server')
    def test_validate_server_false_mock_deploy(self, validate_mock):
        validate_mock.return_value = False
        self.assertFalse(self.configuration.validate_server(self.deploy_server))

    def test_validate_server_false(self):
        server = host.WindowsExecuteHost(ip='15.83.248.251', mac=5666666, hostname='Deploy_Node_1', version=1.0,
                                         username='Administrator', password='Shanghai2010', domain=None)
        self.assertFalse(self.configuration.validate_server(server))
