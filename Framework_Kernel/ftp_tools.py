# from multiprocessing import Pipe
# from Framework_Kernel.log import controller_log
# from Framework_Kernel import configuration_engine
# from Framework_Kernel import assemble_engine
# from Framework_Kernel import execution_engine
# from Common_Library.functions import get_keyboard_input
# from multiprocessing import Process
# import threading
# import time
# from Framework_Kernel.task import Task
# from Framework_Kernel.host import WindowsExecuteHost
# from Framework_Kernel.host import WindowsDeployHost
# from Framework_Kernel.QTPutils import QTP_HPDM
# import ruamel.yaml as yaml
#
#
#
# if __name__ == '__main__':
#
#     task = Task('precheck')
#     uut1 = WindowsExecuteHost('15.83.248.208', '7C:D3:0A:05:01:97', '', 'WES10', '', '', '', '')
#     # uut2 = WindowsExecuteHost('15.83.250.20', '48:0F:CF:BC:DD:3C', '', 'WES10', 'Admin', 'Admin', '', 'on')
#     uut3 = WindowsExecuteHost('15.83.250.205', '48:0F:CF:BB:7C:65', '', 'WES7E', 'Administrator', 'Administrator', '', 'on')
#     # uut4 = WindowsExecuteHost('15.83.250.210', '48:0F:CF:BB:7F:65', '', 'WES7E', 'Administrator', 'Administrator', '', 'on')
#     deploy_host = WindowsDeployHost("15.83.248.251","","")
#     execute_host = WindowsExecuteHost("15.83.248.251", "", "")
#     task.insert_uut_list(uut1)
#     # task.insert_uut_list(uut2)
#     task.insert_uut_list(uut3)
#     # task.insert_uut_list(uut4)
#     task.insert_exe_file_list(r'/jenkins/windows/task_2/run.exe')
#     # task.deploy(deploy_host)
#     # print('deploying')
#     task.execute()
#     print('executing')
#     task.collect_result(execute_host)
import ftplib
import os


class FTPUtils:
    def __init__(self, server='15.83.248.251', username='automation', password='Shanghai2010', base_Path='/Repository/Files/Captured'):
        self.ftp = ftplib.FTP(server)
        self.ftp.login(username, password)
        self.base_path = base_Path
        self.ftp.cwd(self.base_path)

    def get_list(self):
        self.ftp.cwd(self.base_path)
        return self.ftp.nlst()

    def is_ftp_file(self,name):
        try:
            self.ftp.cwd(name)
            self.ftp.cwd('..')
            return False
        except:
            return True

    def download(self, localfile, remotefile):
        file_handler = open(localfile, 'wb')
        self.ftp.retrbinary("RETR " + remotefile, file_handler.write)
        file_handler.close()
        self.ftp.delete(remotefile)

    def download_dir(self, local, remote):
            if self.is_ftp_file(remote):
                self.download(local, remote)
            else:
                if not os.path.exists(local):
                    os.mkdir(local)
                self.ftp.cwd(remote)
                for i in self.ftp.nlst():
                    self.download_dir(os.path.join(local, i), i)
                self.ftp.cwd("..")
                self.ftp.rmd(remote)

    def upload(self, localfile, remotefile):
        self.ftp.storbinary('STOR '+ remotefile, open(localfile, 'rb'), 1024)


    def close(self):
        self.ftp.close()



if __name__ == '__main__':
    ftp_util = FTPUtils()
    task_list = ftp_util.get_list()
    for folder in task_list:
        ftp_util.download_dir(os.path.join('.\\Report', folder), folder)
    ftp_util.close()
