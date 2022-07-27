import os
import time
import struct
import socket
import threading
import numpy as np
from queue import Queue

from libs.recv import Receive,Cache
from libs.conf import *
from libs.utils import *

           
def main():
    filename = './data/{}.dat'.format(int(round(time.time() * 1000)))
    fid = open(filename,'ab+')

    local_udp_ip = "192.168.0.3"
    local_udp_port = 6000
    fpga_udp_ip = "192.168.0.2"
    fpga_udp_port = 5000
    
    r = Receive(local_udp_ip,local_udp_port,fpga_udp_ip,fpga_udp_port)
    msg,result = r.setting(txs,rxs)
    if result < 0:
        print(msg)
        exit(0)

    recv_thd = threading.Thread(target=r.recv_data)
    recv_thd.setDaemon(True)
    recv_thd.start()
    try:
        while True:
            if Cache.empty():
                time.sleep(0.001)
                continue
            else:
                print(Cache.qsize())
                pack = Cache.get()
                save_pack = pack['byte']
                fid.write(save_pack)
    except KeyboardInterrupt:
        fid.flush()
        fid.close()
            

if __name__ == '__main__':
    main()