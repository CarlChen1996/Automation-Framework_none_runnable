# -*- coding: utf-8 -*-
# @Time    : 8/5/2019 6:00 PM
# @Author  : Kit.Liu
# @Email   : jie.liu1@hp.com
# @File    : test_validator.py
# @Project : Automation-Framework
from Framework_Kernel import validator, host
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

    def test_ping_true(self):
        self.assertTrue(validator.Validator().ping(self.ip))

    def test_ping_false(self):
        self.assertFalse(validator.Validator().ping(self.unavailable_ip))

    @patch('Framework_Kernel.validator.HostValidator.get_jenkins_node_state')
    @patch('Framework_Kernel.validator.Validator.ping')
    def test_build_server(self, ping_mock, jenkins_node_mock):
        ping_mock.return_value = True
        self.assertTrue(self.host_validator.validate_build_server(self.build_server))
        jenkins_node_mock.assert_called_once_with(self.build_server)

    @patch('Framework_Kernel.validator.Validator.ping')
    def test_unavailable_build_server(self, ping_mock):
        ping_mock.return_value = False
        self.assertFalse(self.host_validator.validate_build_server(self.unavailable_build_server))

    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_QTP')
    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_HPDM')
    def test_deploy_server(self, qtp_mock, hpdm_mock):
        qtp_mock.return_value = True
        hpdm_mock.return_value = True
        self.assertTrue(self.host_validator.validate_deploy_server(self.deploy_server))

    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_HPDM')
    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_QTP')
    def test_unavailable_deploy_server_qtp_false(self, qtp_mock, hpdm_mock):
        qtp_mock.return_value = False
        self.assertFalse(self.host_validator.validate_deploy_server(self.unavailable_deploy_server))
        self.assertFalse(hpdm_mock.called)

    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_HPDM')
    @patch('Framework_Kernel.validator.HostValidator._HostValidator__validate_QTP')
    def test_unavailable_deploy_server_hpdm_false(self, qtp_mock, hpdm_mock):
        qtp_mock.return_value = True
        hpdm_mock.return_value = False
        self.assertFalse(self.host_validator.validate_deploy_server(self.unavailable_deploy_server))

    @patch('Framework_Kernel.validator.Validator.ping')
    def test_UUT(self, ping_mock):
        ping_mock.return_value = True
        self.assertTrue(self.host_validator.validate_uut(self.uut_host))

    @patch('Framework_Kernel.validator.Validator.ping')
    def test_unavailable_UUT(self, ping_mock):
        ping_mock.return_value = False
        self.assertFalse(self.host_validator.validate_uut(self.unavailable_uut_host))

    def test_ftp(self):
        ftp = {'server_address': '15.83.240.98', 'username': r'sh\kit.liu', 'password': 'Shanghai2014'}
        self.assertTrue(self.host_validator.validate_ftp(ftp))

    def test_unavailable_ftp(self):
        ftp = {'server_address': '15.83.240.1', 'username': r'sh\kit.liu', 'password': 'Shanghai2014'}
        self.assertFalse(self.host_validator.validate_ftp(ftp))
