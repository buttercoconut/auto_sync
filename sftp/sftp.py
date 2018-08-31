import os, sys
from glob import glob
from datetime import datetime

dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dir, '../'))

class SFTP(object):

    def __init__(self, ssh, config):
        self.ssh = ssh
        self.sftp = ssh.open_sftp()
        self.local = config['local']['dir']
        self.dest = config['dest']['dir']
        self.dest_list = []
        self.local_list = []

        # dest and local file check
        stdin, stdout, stderr = self.ssh.exec_command("ls " + self.dest)
        dest_file_path = stdout.read().split()
        for each in dest_file_path:
            self.dest_list.append(each.decode('ascii'))
        local_file_path = glob(self.local + "/*")
        for each in local_file_path:
            self.local_list.append(each.replace(self.local + "/", ""))

    def recv(self):
        for each in self.dest_list:
            log_f = open(os.path.join(dir[:-5], "log/" + str(datetime.now())[:-16] + "_send.log"), "a")
            if each not in self.local_list:
                try:
                    self.sftp.get(self.dest + "/" + each, self.local + "/" + each)
                    # log record
                    log_f.write(str(datetime.now()) + " : " + self.dest + "/" + each + "\n")
                except OSError:
                    pass

            log_f.close()

    def send(self):
        for each in self.local_list:
            log_f = open(os.path.join(dir[:-5], "log/" + str(datetime.now())[:-16] + "_send.log"), "a")
            if each not in self.dest_list:
                try:
                    self.sftp.put(self.local + "/" + each, self.dest + "/" + each)
                    # log record
                    log_f.write(str(datetime.now()) + " : " + self.local + "/" + each + "\n")
                except OSError:
                    pass

            log_f.close()