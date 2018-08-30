import os, sys

dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dir, '../connector'))

import connector

if __name__ == "__main__":

    connector.connection()