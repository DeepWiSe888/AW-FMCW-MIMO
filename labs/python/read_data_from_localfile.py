import os
import time
import struct
import socket
import threading
import numpy as np
from queue import Queue

from sqlalchemy import true

from libs.recv import Receive,Cache
from libs.conf import *
from libs.utils import *

           
def main():
    filename = './data/{}.dat'.format("1653646783394")
    fid = open(filename,'rb')
    last_fn = 0
    recv_buffer = bytes()
    total_fn = 0
    while True:
        data = fid.read(1024)
        if len(data) < 1024:
            break
        recv_buffer += data
        start_index = recv_buffer.find(flag)
        if(start_index == -1):
            continue
        end_index = recv_buffer.find(flag,start_index+flag_size)
        if(end_index == -1):
            continue
        else:
            pack = recv_buffer[start_index:end_index]
            save_pack,pack_dict = parse_pack_from_stream(pack)
            timestamp = pack_dict['t']
            frame_no = pack_dict['fn']
            tx_antenna_no = pack_dict['tx']
            rx_antenna_no = pack_dict['rx']
            total_fn += 1
            # print("fn:{},total fn:{}".format(frame_no,total_fn))
            if frame_no - last_fn != 1:
                print(timestamp,tx_antenna_no,rx_antenna_no,frame_no,last_fn,frame_no - last_fn)
            last_fn = frame_no
            recv_buffer = recv_buffer[end_index:]
    fid.close()
    
            

if __name__ == '__main__':
    main()