import configparser
import paramiko

def connection():

    config = configparser.ConfigParser()
    config.read('../config/local.conf')

    ipaddress = config['connect']['ipaddress']
    port = config['connect']['port']
    username = config['connect']['username']
    passwd = config['connect']['passwd']

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ipaddress, port=port, username=username, password=passwd)

    sftp = ssh.open_sftp()

    sftp.get('/home/yutw/data/uptime.log', 'temp.log')

    ssh.close()