# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
from Framework_Kernel.engine import Engine
from Framework_Kernel.host import WindowsBuildHost, WindowsDeployHost, LinuxBuildHost, LinuxDeployHost
from Framework_Kernel.analyzer import Analyzer
from Framework_Kernel.validator import HostValidator
from Framework_Kernel.log import configuration_log
import os
from multiprocessing import Process, Pipe
from Framework_Kernel.error_handler import ErrorMsg, ErrorLevel, ErrorHandler, EngineCode


class ConfigurationEngine(Engine):
    def __init__(self):
        self.build_server_list = []
        self.deploy_server_list = []
        self.receive_signal, self.send_signal = Pipe()
        self.config_server_list = os.path.join(
            (os.path.abspath(r".\Configuration")), "config_server_list.yml")
        self.list_status = False
        self.server_map_dict = {
            ('windows', 'build'): WindowsBuildHost,
            ('windows', 'deploy'): WindowsDeployHost,
            ('linux', 'build'): LinuxBuildHost,
            ('linux', 'deploy'): LinuxDeployHost
        }

    def start(self):
        self.build_server_list.clear()
        self.deploy_server_list.clear()
        self.__configuration_process = Process(target=self.run, args=())
        self.__configuration_process.start()
        self.status = self.__configuration_process
        receive_signal = self.receive_signal.recv()
        for valid_server in receive_signal:
            if isinstance(valid_server, (WindowsBuildHost, LinuxBuildHost)):
                self.build_server_list.append(valid_server)
                configuration_log.info("Add Build Host {}".format(
                    valid_server.get_hostname()))
            elif isinstance(valid_server, (WindowsDeployHost, LinuxDeployHost)):
                self.deploy_server_list.append(valid_server)
                configuration_log.info("Add Deploy Host {}".format(
                    valid_server.get_hostname()))
        self.list_status = True
        return self.list_status

    def get_server_list(self):
        server_list_analyzer = Analyzer()
        server_list = server_list_analyzer.analyze_file(
            self.config_server_list)
        return server_list

    def __init_server(self, server_item):
        current_key = (server_item['os'], server_item['function'])
        if current_key in self.server_map_dict.keys():
            server = self.server_map_dict[current_key](
                ip=server_item['ip'],
                hostname=server_item['hostname'],
                version=server_item['version'],
                mac=server_item['mac'],
                username=server_item['username'],
                password=server_item['password'],
                domain=server_item['domain'])
            configuration_log.info('Init {}'.format(server_item['hostname']))
        else:
            print('Invalid server type {}'.format(current_key))
            server = False
        return server

    def validate_server(self, server):
        validator = HostValidator()
        validation_result = False
        if isinstance(server, (WindowsBuildHost, LinuxBuildHost)) and validator.validate_jenkins_server():
            validation_result = validator.validate_build_server(server)
        elif isinstance(server, (WindowsDeployHost, LinuxDeployHost)):
            validation_result = validator.validate_deploy_server(server)
        # TODO Need to check more here
        return validation_result

    def run(self):
        configuration_log.info("Start configuration, Engine PID is {}".format(
            str(os.getpid())))
        server_list_result = self.get_server_list()
        valid_server_list = []
        for server_item in server_list_result:
            server = self.__init_server(server_item)
            if self.validate_server(server):
                valid_server_list.append(server)
            else:
                error_msg_instance = ErrorMsg(EngineCode().config_engine, ErrorLevel().record_and_continue,
                                              "validate server {} fail".format(server.get_hostname()))
                error_handle_instance = ErrorHandler(error_msg_instance)
                error_handle_instance.handle()
        self.send_signal.send(valid_server_list)
        return valid_server_list

    def stop(self):
        self.__configuration_process.terminate()
