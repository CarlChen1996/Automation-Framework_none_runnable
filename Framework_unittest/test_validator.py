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
test_build_server: check connectivity of build server
test_deploy_server: check connectivity of deploy server
test_UUT: check connectivity of UUT
test_https: check connectivity of https server
'''


class AnalyzerTest(unittest.TestCase):
    def setUp(self):
        self.build_server = host.Host(ip='15.83.240.98', mac='1A2B3C4D5E6F7G8H', hostname='build_server')
        self.deploy_server = host.Host(ip='15.83.240.98', mac='1A2B3C4D5E6F7G8H', hostname='deploy_server')
        self.uut_host = host.Host(ip='15.83.240.98', mac='1A2B3C4D5E6F7G8H', hostname='uut_host')
        self.host_validator = validator.HostValidator()

    def test_build_server(self):
        self.assertTrue(self.host_validator.validate(self.build_server))

    def test_deploy_server(self):
        self.assertTrue(self.host_validator.validate(self.deploy_server))

    def test_UUT(self):
        self.assertTrue(self.host_validator.validate(self.uut_host))

    @patch('Framework_Kernel.validator.Validator.validate')
    def test_https(self, validate_mock):
        validator.Validator().validate('test')
        validate_mock.assert_called_once_with('test')
