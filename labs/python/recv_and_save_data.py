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

    last_fn = 0
    recv_buffer = bytes()
    try:
        while True:
            if Cache.empty():
                time.sleep(0.001)
                continue
            else:
                print(Cache.qsize())
                cache_pack = Cache.get()
                data = cache_pack['byte']
                recv_buffer = recv_buffer + data
                while True:
                    start_index = recv_buffer.find(flag)
                    if(start_index == -1):
                        break
                    end_index = recv_buffer.find(flag,start_index+flag_size)
                    if(end_index == -1):
                        break
                    pack = recv_buffer[start_index:end_index]
                    save_pack,pack_dict = parse_pack_from_stream(pack)
                    timestamp = pack_dict['t']
                    frame_no = pack_dict['fn']
                    tx_antenna_no = pack_dict['tx']
                    rx_antenna_no = pack_dict['rx']
                    if frame_no - last_fn != 1:
                        print(timestamp,tx_antenna_no,rx_antenna_no,frame_no,last_fn,frame_no - last_fn)
                    last_fn = frame_no
                    recv_buffer = recv_buffer[end_index:]

                    fid.write(save_pack)
    except KeyboardInterrupt:
        fid.flush()
        fid.close()
            

if __name__ == '__main__':
    main()