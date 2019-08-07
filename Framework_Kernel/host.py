# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:00
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : test.py
# @Project : demo
import sys, os
from Framework_Kernel.log import assemble_log, execution_log
from Framework_Kernel import jenkins_class, QTPutils
from Framework_Kernel.analyzer import Analyzer
from Common_Library import file_operator, file_transfer


class Host:
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        self.__ip = ip
        self.__hostname = hostname
        self.__version = version
        self.__mac = mac
        self.__username = username
        self.__password = password
        self.__domain = domain
        self.status = status

    def start(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def reboot(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def shutdown(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def get_ip(self):
        return self.__ip

    def get_hostname(self):
        return self.__hostname

    def get_version(self):
        return self.__version

    def get_mac(self):
        return self.__mac

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_domain(self):
        return self.__domain

    # def get_status(self):
    #     return self.__status
    #
    # def set_status(self, status):
    #     if status == "on" or status == "off":
    #         self.__status = status
    #     else:
    #         print("status format input error, confirm your input is 'on' or 'off'")
    #     return False


class WindowsHost(Host):
    pass


class LinuxHost(Host):
    pass


class Build:
    def __init__(self):
        self.log = assemble_log

    def get_scripts(self, task):
        for script in task.get_script_list():
            pass
        self.log.info('get  {} scripts PASS'.format(task.get_name()))

    def jenkins_build(self,task,target_os,ip,user_name,password,py_entry="run.py",output_name = "run"):
        # my_url = "http://15.83.248.200:8080"
        my_url= "http://"+ip+":8080"
        # my_id = "bamboo"
        my_id=user_name
        # my_token = "1177eafe586b4459f7410f9abb393e15f2"
        my_token=password
        server1 = jenkins_class.Jenkins_Server(my_url, my_id, my_token)
        server1.connect()
        if target_os==jenkins_class.OS_type.win:
            """job info"""
            my_job_name = "job_test_win"
            my_job_os_type = jenkins_class.OS_type.win
            my_job_repository = task.get_repository()
            my_job_py_entry = py_entry
            my_job_output_name = output_name
            my_remote_folder_name = task.get_name()
            my_mail_list=task.get_email()
            job_win = jenkins_class.JOB(my_job_name, my_job_os_type, my_job_repository, my_job_py_entry, my_job_output_name, my_remote_folder_name ,server1,my_mail_list)
            job_win.creare_job()
            job_win.build_job()
            if job_win.build_result=='SUCCESS':
                task.insert_exe_file_list(r'/jenkins/windows/'+my_remote_folder_name+r'/'+my_job_output_name+'.exe')
                task.set_status(job_win.build_result)
            else:
                task.set_status(job_win.build_result)
            job_win.remove()
        elif target_os==jenkins_class.OS_type.linux:
            """job info"""
            my_job_name1 = "job_test_linux"
            my_job_os_type1 = jenkins_class.OS_type.linux
            my_job_repository1 = task.get_repository()
            my_job_py_entry1 = py_entry
            my_job_output_name1 = output_name
            my_remote_folder_name1=task.get_name()
            my_mail_list = task.get_email()
            job_linux = jenkins_class.JOB(my_job_name1, my_job_os_type1, my_job_repository1, my_job_py_entry1, my_job_output_name1,my_remote_folder_name1,server1,my_mail_list)
            job_linux.creare_job()
            job_linux.build_job()
            if job_linux.build_result=='SUCCESS':
                task.insert_exe_file_list(r'/jenkins/linux/'+my_remote_folder_name1+r'/'+my_job_output_name1)
                task.set_status(job_linux.build_result)
            else:
                task.set_status(job_linux.build_result)
            job_linux.remove()

    def get_os_type(self,task):
        for i in task.get_uut_list():
            if 'wes' in i._Host__version.lower():
                return jenkins_class.OS_type.win
            elif 'tp' in i._Host__version.lower():
                return jenkins_class.OS_type.linux

    def build_task(self, task):
        os_type=self.get_os_type(task)
        '''
        check scripts empty
        '''
        if not task.get_script_list():
            task.set_status("FAIL")
            return
        self.jenkins_build(task, os_type,self._Host__ip,self._Host__username,self._Host__password)
        self.log.info('build ' + task.get_name() + task.get_status())
        self.generate_scripts_config(task)


    def generate_scripts_config(self,task):
        self.log.info("generate script config file")
        scripts_config=os.path.join(os.getcwd(),'script.yml')
        scripts=[{i.get_name():i.get_status()} for i in task.get_script_list()]
        file.YamlFile.save(scripts,scripts_config)
        store_dir=os.path.join(os.path.dirname(task.get_exe_file_list()[0]),'test_data')
        self.log.info("upload script config file to {}".format(store_dir))
        remote_base_path=store_dir
        # Retrive FTP Settings from configuration file
        config_file = os.path.join(os.getcwd(), r'.\Configuration\config_framework_list.yml')
        analyze_hanlder = Analyzer()
        ftp_settings = analyze_hanlder.analyze_file(config_file)['ftp_settings']
        ftp_util = file_transfer.FTPUtils(ftp_settings['server_address'], ftp_settings['username'], ftp_settings['password'])
        ftp_util.change_dir(remote_base_path)
        ftp_util.upload_file(scripts_config, 'script.yml')
        ftp_util.close()


class Deploy:
    def __init__(self, host):
        self.log = execution_log
        self.host = host

    def deploy_task(self, task):
        QTPutils.QTP_HPDM().deploy_task(task, self.host)
        self.log.info('deploy package: ' + task.get_name() + ' Pass')


class Execute:
    def __init__(self, host):
        self.log = execution_log
        self.host = host

    def execute_task(self, task):
        QTPutils.QTP_HPDM().execute_task(self.host, task)
        self.log.info('execute {} on  {}'.format(
            task.get_name(),
            task.get_uut_list()[0].get_hostname()))

    def check_status(self, task):
        self.log.info('check {} status on {}'.format(
            task.get_name(),
            task.get_uut_list()[0].get_hostname()))

    def collect_result(self, task):
        QTPutils.QTP_HPDM().get_result(task)
        self.log.info('collect {} result from {}'.format(
            task.get_name(),
            task.get_uut_list()[0].get_hostname()))


class WindowsBuildHost(WindowsHost, Build):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        WindowsHost.__init__(self, ip, mac, hostname, version, username,
                             password, domain, status)
        Build.__init__(self)

    pass


class WindowsDeployHost(WindowsHost, Deploy):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        WindowsHost.__init__(self, ip, mac, hostname, version, username,
                             password, domain, status)
        Deploy.__init__(self, self)

    pass


class WindowsExecuteHost(WindowsHost, Execute):
    def __init__(self,
                 ip,
                 mac,
                 hostname='',
                 version='',
                 username='',
                 password='',
                 domain='',
                 status='off'):
        WindowsHost.__init__(self, ip, mac, hostname, version, username,
                             password, domain, status)
        Execute.__init__(self, self)

    pass


class LinuxBuild(LinuxHost, Build):
    pass


class LinuxExecute(LinuxHost, Execute):
    pass


if __name__ == "__main__":
    b = WindowsBuildHost("", "", "", "", "", "", "", "")
    b.build()
    d = WindowsDeployHost("", "", "", "", "", "", "", "")
    d.deploy_task()
    e = WindowsExecuteHost("", "", "", "", "", "", "", "")
    e.check_status()
    e.collect_result()
