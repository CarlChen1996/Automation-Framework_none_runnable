# -*- coding: utf-8 -*-
# @Time    : 8/5/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_validator.py
# @Project : Automation-Framework
from Framework_Kernel import validator, host, task, script
from unittest.mock import patch
import unittest

'''
setUp: Initialize variables
test_ping_true: ping to available ip
test_ping_false: ping to unavailable ip
test_build_server: check connectivity of build server
test_unavailable_build_server: check return value with unavailable build ip
test_deploy_server: check connectivity of deploy server
test_unavailable_deploy_server_qtp_false: check return value with unavailable qtp server
test_unavailable_deploy_server_hpdm_false: check return value with unavailable hpdm server
test_UUT: check connectivity of UUT
test_unavailable_UUT: check return value with unavailable uut ip
test_ftp: check connectivity of ftp server
test_unavailable_ftp
'''


class ValidatorTest(unittest.TestCase):
    def setUp(self):
        self.ip = '15.83.240.98'
        self.unavailable_ip = '10.10.10.10'
        self.mac = '1A2B3C4D5E6F7G8H'
        self.build_server = host.Host(ip=self.ip, mac=self.mac, hostname='build_server')
        self.deploy_server = host.Host(ip=self.ip, mac=self.mac, hostname='deploy_server')
        self.uut_host = host.Host(ip=self.ip, mac=self.mac, hostname='uut_host')
        self.unavailable_build_server = host.Host(ip=self.unavailable_ip, mac=self.mac,
                                                  hostname='unavailable_build_server')
        self.unavailable_deploy_server = host.Host(ip=self.unavailable_ip, mac=self.mac,
                                                   hostname='unavailable_deploy_server')
        self.unavailable_uut_host = host.Host(ip=self.unavailable_ip, mac=self.mac,
                                              hostname='unavailable_uut_host')
        self.host_validator = validator.HostValidator()
        self.script_validator = validator.ScriptValidator()
        self.task = task.Task(name='test')

    def test_ping_true(self):
        self.assertTrue(validator.Validator().ping(self.ip))

    def test_ping_false(self):
        self.assertFalse(validator.Validator().ping(self.unavailable_ip))

    def test_validate_jenkins_server(self):
        self.assertTrue(self.host_validator.validate_jenkins_server())

    @patch('jenkins.Jenkins.get_info')
    def test_validate_jenkins_server_false(self, jenkins_mock):
        jenkins_mock.side_effect = EOFError
        self.assertFalse(self.host_validator.validate_jenkins_server())

    @patch('Framework_Kernel.validator.HostValidator.get_jenkins_node_state')
    @patch('Framework_Kernel.validator.Validator.ping')
    def test_build_server(self, ping_mock, jenkins_node_mock):
        ping_mock.return_value = True
        jenkins_node_mock.return_value = True
        self.assertTrue(self.host_validator.validate_build_server(self.build_server))
        jenkins_node_mock.assert_called_once_with(self.build_server)
        self.assertEqual(self.build_server.status, 'on')

    @patch('Framework_Kernel.validator.HostValidator.get_jenkins_node_state')
    @patch('Framework_Kernel.validator.Validator.ping')
    def test_build_server_ping_false(self, ping_mock, jenkins_node_mock):
        ping_mock.return_value = False
        self.assertFalse(self.host_validator.validate_build_server(self.unavailable_build_server))
        jenkins_node_mock.asset_not_called()
        self.assertEqual(self.build_server.status, 'off')

    @patch('Framework_Kernel.validator.HostValidator.get_jenkins_node_state')
    @patch('Framework_Kernel.validator.Validator.ping')
    def test_build_server_jenkins_false(self, ping_mock, jenkins_node_mock):
        ping_mock.return_value = True
        jenkins_node_mock.return_value = False
        self.assertFalse(self.host_validator.validate_build_server(self.build_server))
        jenkins_node_mock.assert_called_once_with(self.build_server)
        self.assertEqual(self.build_server.status, 'off')

    @patch('Common_Library.jenkins_operator.JenkinsServer.get_jenkins_node_state')
    def test_get_jenkins_node_state(self, jenkins_mock):
        jenkins_mock.return_value = 'Idle'
        self.assertTrue(self.host_validator.get_jenkins_node_state(self.build_server))

    @patch('Common_Library.jenkins_operator.JenkinsServer.get_jenkins_node_state')
    def test_get_jenkins_node_state_false(self, jenkins_mock):
        jenkins_mock.side_effect = EOFError
        self.assertFalse(self.host_validator.get_jenkins_node_state(self.build_server))

    def test_validate_QTP(self):
        pass

    def test_validate_HPDM(self):
        pass

    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_QTP')
    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_HPDM')
    def test_deploy_server(self, qtp_mock, hpdm_mock):
        qtp_mock.return_value = True
        hpdm_mock.return_value = True
        self.assertTrue(self.host_validator.validate_deploy_server(self.deploy_server))
        qtp_mock.assert_called_once_with(self.deploy_server)
        hpdm_mock.assert_called_once_with(self.deploy_server)
        self.assertEqual(self.deploy_server.status, 'on')

    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_HPDM')
    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_QTP')
    def test_unavailable_deploy_server_qtp_false(self, qtp_mock, hpdm_mock):
        qtp_mock.return_value = False
        self.assertFalse(self.host_validator.validate_deploy_server(self.unavailable_deploy_server))
        qtp_mock.assert_called_once_with(self.unavailable_deploy_server)
        hpdm_mock.assert_not_called()
        self.assertEqual(self.unavailable_deploy_server.status, 'off')

    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_HPDM')
    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_QTP')
    def test_unavailable_deploy_server_hpdm_false(self, qtp_mock, hpdm_mock):
        qtp_mock.return_value = True
        hpdm_mock.return_value = False
        self.assertFalse(self.host_validator.validate_deploy_server(self.unavailable_deploy_server))
        qtp_mock.assert_called_once_with(self.unavailable_deploy_server)
        hpdm_mock.assert_called_once_with(self.unavailable_deploy_server)
        self.assertEqual(self.unavailable_deploy_server.status, 'off')

    @patch('Framework_Kernel.validator.Validator.ping')
    def test_UUT(self, ping_mock):
        ping_mock.return_value = True
        self.assertTrue(self.host_validator.validate_uut(self.uut_host))
        self.assertEqual(self.uut_host.status, 'on')

    @patch('Framework_Kernel.validator.Validator.ping')
    def test_unavailable_UUT(self, ping_mock):
        ping_mock.return_value = False
        self.assertFalse(self.host_validator.validate_uut(self.unavailable_uut_host))
        self.assertEqual(self.unavailable_uut_host.status, 'off')

    def test_ftp(self):
        ftp = {'server_address': '15.83.240.98', 'username': r'sh\kit.liu', 'password': 'Shanghai2014'}
        self.assertTrue(self.host_validator.validate_ftp(ftp))

    def test_unavailable_ftp(self):
        ftp = {'server_address': '15.83.240.1', 'username': r'sh\kit.liu', 'password': 'Shanghai2014'}
        self.assertFalse(self.host_validator.validate_ftp(ftp))

    @patch('Framework_Kernel.validator.ScriptValidator.get_git_scripts')
    def test_script_validate(self, git_mock):
        git_mock.return_value = ['1', '2']
        self.task.insert_script(script.Script(name='1'))
        self.assertTrue(validator.ScriptValidator().validate(self.task))
        git_mock.assert_called_once_with(self.task)

    @patch('Framework_Kernel.validator.ScriptValidator.get_git_scripts')
    def test_script_validate_equal(self, git_mock):
        git_mock.return_value = ['1', '2']
        self.task.insert_script(script.Script(name='1'))
        self.task.insert_script(script.Script(name='2'))
        self.assertTrue(validator.ScriptValidator().validate(self.task))
        git_mock.assert_called_once_with(self.task)

    @patch('Framework_Kernel.validator.ScriptValidator.get_git_scripts')
    def test_script_validate_false(self, git_mock):
        git_mock.return_value = ['1', '2']
        self.task.insert_script(script.Script(name='1'))
        self.task.insert_script(script.Script(name='2'))
        self.task.insert_script(script.Script(name='3'))
        self.assertFalse(validator.ScriptValidator().validate(self.task))
        git_mock.assert_called_once_with(self.task)

    def test_handle_remove_read_only(self):
        pass

    def test_get_git_scripts(self):
        pass
