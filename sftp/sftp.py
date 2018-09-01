import os, sys
import subprocess
from glob import glob
from datetime import datetime

dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dir, '../'))

def subprocess_open_when_shell_true(command):
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (stdoutdata, stderrdata) = popen.communicate()
    return stdoutdata, stderrdata

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
            self.dest_list.append(each.decode('utf-8'))
        local_file_path = glob(self.local + "/*")
        for each in local_file_path:
            self.local_list.append(each.replace(self.local + "/", ""))

    def dir_transfer(self, opt, dir_path, dir_name, filelist):

        if opt == "recv":

            try:
                self.sftp.get(self.dest + "/" + each, self.local + "/" + each)
                # log record
                log_f = open(os.path.join(dir[:-5], "log/" + str(datetime.now())[:-16] + "_recv.log"), "a")
                log_f.write(str(datetime.now()) + " : " + self.dest + "/" + each + "\n")
                log_f.close()
            except OSError:
                subprocess_open_when_shell_true("mkdir " + dir_path + "/" + dir_name)
                self.dir_transfer()

            return filelist

        elif opt == "send":
            try:
                self.sftp.put(self.local + "/" + each, self.dest + "/" + each)
                # log record
                log_f = open(os.path.join(dir[:-5], "log/" + str(datetime.now())[:-16] + "_send.log"), "a")
                log_f.write(str(datetime.now()) + " : " + self.local + "/" + each + "\n")
                log_f.close()
            except OSError:
                self.ssh.exec_command("mkdir " + dir_path + "/" + dir_name)
                self.dir_transfer()

            return filelist

    def recv(self):
        get_list = []
        for each in self.dest_list:
            if each not in self.local_list:
                if os.path.isdir(self.dest + "/" + each):
                    subprocess_open_when_shell_true("mkdir " + each[1])
                    self.dir_transfer("recv", self.local, each, get_list)
                else:
                    get_list.append([self.dest + "/" + each, self.local + "/" + each])

        for each in get_list:
            self.sftp.get(each[0], each[1])
            # log record
            log_f = open(os.path.join(dir[:-5], "log/" + str(datetime.now())[:-16] + "_recv.log"), "a")
            log_f.write(str(datetime.now()) + " : " + each[0] + "\n")
            log_f.close()

    def send(self):
        put_list = []
        for each in self.local_list:
            if each not in self.dest_list:
                if os.path.isdir(self.local + "/" + each):
                    self.ssh.exec_command("mkdir " + each[1])
                    self.dir_transfer("send", self.dest, each, put_list)
                else:
                    put_list.append([self.local + "/" + each, self.dest + "/" + each])

        for each in put_list:
            self.sftp.put(each[0], each[1])
            # log record
            log_f = open(os.path.join(dir[:-5], "log/" + str(datetime.now())[:-16] + "_send.log"), "a")
            log_f.write(str(datetime.now()) + " : " + each[0] + "\n")
            log_f.close()
