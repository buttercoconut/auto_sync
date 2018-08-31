import paramiko
from datetime import datetime
from traceback import format_exc

def connection(config):

    log = ""

    ipaddress = config['connect']['ipaddress']
    try:
        port = config['connect']['port']
    except:
        port = 22
    try:
        username = config['connect']['username']
    except:
        log += "Null username "
    try:
        passwd = config['connect']['passwd']
    except:
        log += "Null password "

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ipaddress, port=port, username=username, password=passwd, timeout=10)
        log += str(datetime.now()) + " : connect success to " + ipaddress + ":" + port + "[00]"
    except:
        if"socket.timeout" in str(format_exc()):
            log += str(datetime.now()) + " : connection timeout![01]"
        elif "socket.gaierror" in str(format_exc()):
            log += str(datetime.now()) + " : nodename nor servname provided, or not known![02]"
        else:
            log += str(datetime.now()) + " : unknown error![03]"

    return ssh, log