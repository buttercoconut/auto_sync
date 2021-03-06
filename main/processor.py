import os, sys
import configparser
from datetime import datetime

dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dir, '../'))

from connector import connector
from sftp.sftp import SFTP
import observer

if __name__ == "__main__":

    server = sys.argv[1]
    opt = sys.argv[2]

    config = configparser.ConfigParser()
    config.read(os.path.join(dir[:-5], "config/" + server + ".conf"))

    ssh, log = connector.connection(config)

    # log record
    log_f = open(os.path.join(dir[:-5], "log/" + str(datetime.now())[:-16] + ".log"), "a")
    log_f.write(log + "\n")
    log_f.close()

    # file sync
    if log[-4:] == "[00]":

        if opt == "recv":
            SFTP(ssh, config).recv()

        elif opt == "send":
            SFTP(ssh, config).send()

        ssh.close()