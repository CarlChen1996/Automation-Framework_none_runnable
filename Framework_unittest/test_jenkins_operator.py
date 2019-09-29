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

    def test_connect_jenkins_true(self):
        jenkins_host = self.jenkins.connect()
        self.assertIsInstance(jenkins_host, jenkins.Jenkins)

    def test_connect_jenkins_false(self):
        self.jenkins.username = 'test'
        self.assertFalse(self.jenkins.connect())
