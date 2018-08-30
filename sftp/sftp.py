from glob import glob

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

    def resv(self):
        for each in self.dest_list:
            if each not in self.local_list:
                try:
                    self.sftp.get(self.dest + "/" + each, self.local + "/" + each)
                except OSError:
                    pass

    def send(self):
        for each in self.local_list:
            if each not in self.dest_list:
                try:
                    self.sftp.put(each, self.dest + "/" + each)
                except OSError:
                    pass