# -*- coding: utf-8 -*-
# @Time   : 2019/5/29 16:48
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : jenkins_class.py
# @Project : jenkins


import jenkins
import time
import os
from lxml import etree as et
import datetime
import logging
from Framework_Kernel.log import assemble_log

class OS_type:
    win="windows"
    linux="linux"

def timer(func):
    def calculate(*args,**kwargs):
        start_time=datetime.datetime.now()
        func(*args,**kwargs)
        stop_time=datetime.datetime.now()
        with open("log.txt","a") as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" execute: "
                    +func.__name__+" :cost time: {} \n".format(stop_time-start_time))
    return calculate

class Jenkins_Server():
    def __init__(self,url,id,token):
        self.url=url
        self.id=id
        self.token=token
        self.connection:jenkins.Jenkins=None
        self.config_module_win=os.path.join(os.getcwd(),'Configuration',"config_win.xml")
        self.config_module_linux=os.path.join(os.getcwd(),'Configuration',"config_linux.xml")

    def connect(self):
        try:
            self.connection=jenkins.Jenkins(self.url, username=self.id, password=self.token)
        except Exception as e:
            assemble_log.info(str(e))
            # logging.info(str(e))
            # print(e)
            self.connection=None

    def build_job(self,job_name):
        try:
            self.connection.build_job(job_name)
        except Exception as e:
            assemble_log.info(str(e))
            # logging.info(str(e))
            # print(e)

    def get_job_list(self):
        job_list=[]
        for job in self.connection.get_all_jobs():
            job_list.append(job.get("name"))
        return job_list

    def get_last_build_number(self,job_name):
        try:
            return self.connection.get_job_info(job_name).get("lastBuild").get("number")
        except Exception as e:
            assemble_log.info(str(e))
            # logging.info(str(e))
            # print(e)
            return None

    def get_build_result(self,job_name,last_build_number):
        try:
            while True:
                t=self.connection.get_build_info(job_name,last_build_number).get('result')
                if t:
                    return t
                else:
                    assemble_log.info("wait {} build {} result".format(job_name,last_build_number))
                    # logging.info("wait {} build {} result".format(job_name,last_build_number))
                    # print("wait {} build {} result".format(job_name,last_build_number))
                    time.sleep(1)

        except Exception as e :
            assemble_log.info(str(e))
            # logging.info(str(e))
            # print(e)
            return None

    def create_job(self,new_job_name,new_job_config):
        try:
            config=""
            with open(new_job_config) as f:
                config=f.read()
            self.connection.create_job(new_job_name,config)
        except Exception as e:
            assemble_log.info(str(e))
            # logging.info(str(e))
            # print(e)

    def process_config(self,config_file,repository,py_entry,output_name,remote_folder_name,build_node,job_os_type,mail_list):
        try:
            with open(config_file) as f:
                ele_tree:et._ElementTree=et.parse(f)

                ele_repository=ele_tree.xpath(r"./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
                if ele_repository:
                    ele_repository[0].text=repository
                else:
                    assemble_log.info("not found repository in module")
                    # logging.info("not found repository in module")
                    # print("not found repository in module")
                    return None
                if job_os_type =="windows":
                    ele_builder=ele_tree.xpath(r"./builders/hudson.tasks.BatchFile/command")
                else:
                    ele_builder = ele_tree.xpath(r"./builders/hudson.tasks.Shell/command")
                if ele_builder:
                    ele_builder[0].text=ele_builder[0].text.replace("hello.py",py_entry)
                    ele_builder[0].text = ele_builder[0].text.replace("output_name", output_name)
                else:
                    assemble_log.info("not found builder in module")
                    # logging.info("not found builder in module")
                    # print("not found builder in module")
                    return None
                ele_build_node=ele_tree.xpath(r"./assignedNode")
                if ele_build_node:
                    ele_build_node[0].text=build_node
                else:
                    assemble_log.info("not found builder node in module")
                    # logging.info("not found builder node in module")
                    # print("not found builder node in module")
                    return None
                ele_publisher_node=ele_tree.xpath(r"//jenkins.plugins.publish__over__ftp.BapFtpTransfer/remoteDirectory")
                if ele_publisher_node:
                    ele_publisher_node[0].text=ele_publisher_node[0].text.replace('${JOB_NAME}', remote_folder_name)

                ele_mail_list = ele_tree.xpath(r'./publishers/hudson.tasks.Mailer/recipients')
                if ele_mail_list:
                    ele_mail_list[0].text=",".join(mail_list)
                return et.tostring(ele_tree.getroot(),encoding="UTF-8").decode("utf-8")

        except Exception as e:
            assemble_log.info(str(e))
            # logging.info(str(e))
            # print(e)

    def create_job_params(self,job_name,job_os_type,repository,py_entry,output_name,remote_folder_name,mail_list):
        if job_os_type =="windows":
            config_file=self.config_module_win
            build_node="Build_Node_W_1"
        elif job_os_type =="linux":
            config_file=self.config_module_linux
            build_node ="Build-Node-TP-1"
        else:
            raise Exception("please specify job_os_type ")

        try:
            config=self.process_config(config_file,repository,py_entry,output_name,remote_folder_name,build_node,job_os_type,mail_list)
            self.connection.create_job(job_name, config)
        except Exception as e:
            assemble_log.info(str(e))
            # logging.info(str(e))
            # print(e)

    def remove_job(self,job_name):
        try:
            self.connection.delete_job(job_name)
        except Exception as e:
            assemble_log.info(str(e))
            # logging.info(str(e))
            # print(e)

    def check_job_exists(self,job_name):
        return self.connection.job_exists(job_name)


class JOB:
    def __init__(self,job_name,job_os_type,repository,py_entry,output_name,remote_folder_name,server,mail_list):
        self.job_name=job_name
        self.job_os_type=job_os_type
        self.repository=repository
        self.py_entry=py_entry
        self.output_name=output_name
        self.build_result=None
        self.remote_folder_name=remote_folder_name
        self.server=server
        self.mail_list=mail_list


    def creare_job(self):
        """test create win job"""
        if not self.server.check_job_exists(self.job_name):
            self.server.create_job_params(self.job_name, self.job_os_type,self.repository, self.py_entry,
                                     self.output_name,self.remote_folder_name,self.mail_list)
        else:
            self.server.remove_job(self.job_name)
            self.server.create_job_params(self.job_name, self.job_os_type, self.repository, self.py_entry,
                                     self.output_name,self.remote_folder_name,self.mail_list)

    def build_job(self):
        start_last_build = self.server.get_last_build_number(self.job_name)
        # logging.info("start build job {}".format(self.job_name))
        assemble_log.info("start build job {}".format(self.job_name))
        # print("start build job {}".format(self.job_name))
        self.server.build_job(self.job_name)
        while True:
            current_last_build = self.server.get_last_build_number(self.job_name)
            if start_last_build == current_last_build:
                assemble_log.info(
                    "start_last_build_number is {} ,cureent_last_build_number is {}".format(start_last_build,
                                                                                             current_last_build)
                )
                # logging.info("start_last_build_number is {} ,cureent_last_build_number is {}".format(start_last_build,
                #                                                                                      current_last_build))
                # print("start_last_build_number is {} ,cureent_last_build_number is {}".format(start_last_build,
                #                                                                               current_last_build))
                assemble_log.info("wait {} build finish,delay 1s".format(self.job_name))
                # logging.info("wait {} build finish,delay 1s".format(self.job_name))
                # print("wait {} build finish,delay 1s".format(self.job_name))
                time.sleep(1)
            else:
                result=self.server.get_build_result(self.job_name, current_last_build)
                assemble_log.info("start_last_build_number is {} ,cureent_last_build_number is {}".format(start_last_build,
                                                                                                     current_last_build))
                # logging.info("start_last_build_number is {} ,cureent_last_build_number is {}".format(start_last_build,
                #                                                                                      current_last_build))
                # print("start_last_build_number is {} ,cureent_last_build_number is {}".format(start_last_build,
                #                                                                               current_last_build))
                assemble_log.info("{} build finish,result is {}".format(self.job_name, result))
                # logging.info("{} build finish,result is {}".format(self.job_name, result))
                # print("{} build finish,result is {}".format(self.job_name,result))
                self.build_result=result
                break

    def remove(self):
        self.server.remove_job(self.job_name)


if __name__ == '__main__':

    logging.basicConfig(filename="test.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        datefmt="%d-%M-%Y %H:%M:%S",level=logging.INFO)

    """15.36.179.19"""
    # my_url="http://15.36.179.19:8080"
    # my_id="bamboo"
    # my_token="11cd395aeecd61ae8b50b402d28780b63b"
    # my_job="task_test"
    # my_new_job_name="test_job1"
    # my_new_job_config="empty_config.xml"
    # server=Jenkins_Server(my_url,my_id,my_token)
    # server.connect()

    """15.83.248.200"""

    my_url="http://15.83.248.200:8080"
    my_id="bamboo"
    my_token="1177eafe586b4459f7410f9abb393e15f2"
    server1=Jenkins_Server(my_url,my_id,my_token)
    server1.connect()


    """job info"""
    my_job_name="job_test_win"
    my_job_os_type=OS_type.win
    my_job_repository="https://github.azc.ext.hp.com/HPI-ThinClientQA/bamboo_test1.git"
    my_job_py_entry="run.py"
    my_job_output_name="run"
    my_job_remote_folder_name='task1'


    job_win=JOB(my_job_name,my_job_os_type,my_job_repository,my_job_py_entry,my_job_output_name,my_job_remote_folder_name,server1)

    input("press key to start create win job")
    job_win.creare_job()

    input("press any key to build win job and get result")
    job_win.build_job()

    input("press key to remove win job")
    job_win.remove()


    input("press key to continue linux")

    """job info"""
    my_job_name1="job_test_linux"
    my_job_os_type1=OS_type.linux
    my_job_repository1="https://github.azc.ext.hp.com/HPI-ThinClientQA/bamboo_test1.git"
    my_job_py_entry1="run.py"
    my_job_output_name1="run"
    my_job_remote_folder_name1 = 'task1'
    job_linux=JOB(my_job_name1,my_job_os_type1,my_job_repository1,my_job_py_entry1,my_job_output_name1,my_job_remote_folder_name,server1)

    input("press key to start create linux job")

    job_linux.creare_job()

    input("press any key to build linux job and get result")

    job_linux.build_job()

    input("press key to remove linux job")

    job_linux.remove()







