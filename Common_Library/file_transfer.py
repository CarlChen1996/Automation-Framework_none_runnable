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
