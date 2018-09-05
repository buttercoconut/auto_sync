import os, sys
import subprocess
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


    def dest_list(self, ssh, destpath):
        dest_dict = {}
        stdin, stdout, stderr = ssh.exec_command("ls -l " + destpath)
        dest_file_path = stdout.read().decode('utf-8').split("\n")
        for each in dest_file_path:
            spl = each.split()
            if len(spl) == 9:
                dest_dict[spl[8]] = {"format": spl[0], "size": spl[4]}

        return dest_dict


    def local_list(self, localpath):
        local_dict = {}
        local_file_path = list(subprocess_open_when_shell_true("ls -l " + localpath))[0].decode('utf-8').split("\n")
        for each in local_file_path:
            spl = each.split()
            if len(spl) == 9:
                local_dict[spl[8]] = {"format": spl[0], "size": spl[4]}

        return local_dict


    def dir_proc(self, opt, localpath, destpath, filename):

        add_list = []

        if opt[:4] == "recv":

            if opt == "recv_c":
                subprocess_open_when_shell_true("mkdir " + localpath + "/" + filename)

            dest_dict = self.dest_list(self.ssh, destpath + "/" + filename)
            local_dict = self.local_list(localpath + "/" + filename)

            for each in list(dest_dict.keys()):
                dest_format = dest_dict[each]['format'][0]
                dest_size = dest_dict[each]['size']
                if each not in list(local_dict.keys()):
                    if dest_format is 'd':
                        add_list += self.dir_proc("recv_c", localpath, destpath, each)
                    else:
                        add_list.append([destpath + "/" + filename + "/" + each, localpath + "/" + filename + "/" + each])
                else:
                    if dest_format is 'd':
                        add_list += self.dir_proc("recv_r", localpath, destpath, each)
                    else:
                        if dest_size != local_dict[each]['size']:
                            add_list.append([destpath + "/" + filename + "/" + each, localpath + "/" + filename + "/" + each + "_" + str(datetime.now())[:10]])

            return add_list


        elif opt[:4] == "send":

            if opt == "send_c":
                self.ssh.exec_command("mkdir " + destpath + "/" + filename)

            dest_dict = self.dest_list(self.ssh, destpath + "/" + filename)
            local_dict = self.local_list(localpath + "/" + filename)

            for each in list(local_dict.keys()):
                local_format = local_dict[each]['format'][0]
                local_size = local_dict[each]['size']
                if each not in list(dest_dict.keys()):
                    if local_format is 'd':
                        add_list += self.dir_proc("send_c", localpath, destpath, each)
                    else:
                        add_list.append([localpath + "/" + filename + "/" + each, destpath + "/" + filename + "/" + each])
                else:
                    if local_format is 'd':
                        add_list += self.dir_proc("send_r", localpath, destpath, each)
                    else:
                        if local_size != local_dict[each]['size']:
                            add_list.append([localpath + "/" + filename + "/" + each, destpath + "/" + filename + "/" + each + "_" + str(datetime.now())[:13]])

            return add_list



    def recv(self):
        dest_dict = self.dest_list(self.ssh, self.dest)
        local_dict = self.local_list(self.local)
        get_list = []
        for each in list(dest_dict.keys()):
            dest_format = dest_dict[each]['format'][0]
            dest_size = dest_dict[each]['size']
            if each not in list(local_dict.keys()):
                if dest_format is 'd':
                    get_list += self.dir_proc("recv_c", self.local, self.dest, each)
                else:
                    get_list.append([self.dest + "/" + each, self.local + "/" + each])
            else:
                if dest_format is 'd':
                    get_list += self.dir_proc("recv_r", self.local, self.dest, each)
                else:
                    if dest_size != local_dict[each]['size']:
                        get_list.append([self.dest + "/" + each, self.local + "/" + each + "_" + str(datetime.now())[:13]])


        for each in get_list:
            self.sftp.get(each[0], each[1])
            # log record
            log_f = open(os.path.join(dir[:-5], "log/" + str(datetime.now())[:-16] + "_recv.log"), "a")
            log_f.write(str(datetime.now()) + " : " + each[0] + "\n")
            log_f.close()


    def send(self):
        dest_dict = self.dest_list(self.ssh, self.dest)
        local_dict = self.local_list(self.local)
        put_list = []
        for each in list(local_dict.keys()):
            local_format = local_dict[each]['format'][0]
            local_size = local_dict[each]['size']
            if each not in list(dest_dict.keys()):
                if local_format is 'd':
                    put_list += self.dir_proc("send_c", self.local, self.dest, each)
                else:
                    put_list.append([self.local + "/" + each, self.dest + "/" + each])
            else:
                if local_format is 'd':
                    put_list += self.dir_proc("send_r", self.local, self.dest, each)
                else:
                    if local_size != local_dict[each]['size']:
                        put_list.append([self.local + "/" + each, self.dest + "/" + each + "_" + str(datetime.now())[:10]])


        for each in put_list:
            self.sftp.put(each[0], each[1])
            # log record
            log_f = open(os.path.join(dir[:-5], "log/" + str(datetime.now())[:-16] + "_send.log"), "a")
            log_f.write(str(datetime.now()) + " : " + each[0] + "\n")
            log_f.close()
