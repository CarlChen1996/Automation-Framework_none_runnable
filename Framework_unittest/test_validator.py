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
test_unavailable_build_server: check return value with unavailable build ip
test_deploy_server: check connectivity of deploy server
test_unavailable_deploy_server: check return value with unavailable deploy ip
test_UUT: check connectivity of UUT
test_unavailable_UUT: check return value with unavailable uut ip
test_ftp: check connectivity of ftp server
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

    def test_build_server(self):
        self.assertTrue(self.host_validator.validate_build_server(self.build_server))

    def test_unavailable_build_server(self):
        self.assertFalse(self.host_validator.validate_build_server(self.unavailable_build_server))

    def test_deploy_server(self):
        self.assertTrue(self.host_validator.validate_deploy_server(self.deploy_server))

    def test_unavailable_deploy_server(self):
        self.assertFalse(self.host_validator.validate_deploy_server(self.unavailable_deploy_server))

    def test_UUT(self):
        self.assertTrue(self.host_validator.validate_uut(self.uut_host))

    def test_unavailable_UUT(self):
        self.assertFalse(self.host_validator.validate_uut(self.unavailable_uut_host))

    def test_ftp(self):
        ftp = {'server_address': '15.83.240.98', 'username': r'sh\kit.liu', 'password': 'Shanghai2014'}
        self.assertTrue(self.host_validator.validate_ftp(ftp))

    def test_unavailable_ftp(self):
        ftp = {'server_address': '15.83.240.1', 'username': r'sh\kit.liu', 'password': 'Shanghai2014'}
        self.assertFalse(self.host_validator.validate_ftp(ftp))
