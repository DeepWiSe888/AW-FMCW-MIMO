import os
import sys
import time
import threading
import numpy as np
from scipy import interpolate
from scipy import signal

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import matplotlib.pyplot as plt

from libs.recv import Receive,Cache
from libs.utils import *
from libs.conf import param
from libs.process import Process
from libs.plot import PlotData


def process_data(param):
    print("start process data")
    start_save = False
    t1 = t2 = time.time()

    # config
    adc_len = param["adc_len"]
    txs = param['txs']
    rxs = param['rxs']
    num_tx = param['num_tx']
    num_rx = param['num_rx']
    loop_size = param['num_loop_per_frame']
    step_size = param['step_size']
    
    p = Process(param)
    plot = PlotData()
    pack_list = []

    last_fn = 0
    recv_buffer = bytes()
    try:
        while True:
            if Cache.empty():
                time.sleep(0.001)
                continue
            else:
                cache_pack = Cache.get()
                data = cache_pack['byte']
                recv_buffer = recv_buffer + data
                while True:
                    start_index = recv_buffer.find(param['flag'])
                    if(start_index == -1):
                        break
                    end_index = recv_buffer.find(param['flag'],start_index + param['flag_size'])
                    if(end_index == -1):
                        break
                    pack = recv_buffer[start_index:end_index]
                    save_pack,pack_dict = parse_pack_from_stream(pack,param)
                    timestamp = pack_dict['t']
                    frame_no = pack_dict['fn']
                    tx = pack_dict['tx']
                    rx = pack_dict['rx']
                    if frame_no - last_fn != 1:
                        print(timestamp,tx,rx,frame_no,last_fn,frame_no - last_fn)
                    last_fn = frame_no
                    recv_buffer = recv_buffer[end_index:]
                    # 对齐tx、rx
                    # print("tx:{},rx:{}".format(tx,rx))
                    if tx == txs[0] and rx == rxs[0]:
                        start_save = True
                    if start_save:
                        adc_data = pack_dict['adc']
                        adc_data = adc_data[:adc_len]
                        win_data = adc_data * np.hanning(len(adc_data))
                        range_fft_n = param['num_range_nfft']
                        range_fft = np.fft.fft(win_data,range_fft_n)
                        iq = range_fft[0:int(range_fft_n/2)]
                        pack_list.append(iq)
                        if len(pack_list) >= param['frame_size']:
                            t1 = time.time()
                            loop_pack_list = pack_list
                            frames = np.array(loop_pack_list)
                            # print(frames.shape)
                            frames = frames.reshape(loop_size,num_tx,num_rx,-1)
                            range_time, range_doppler,range_azimuth,range_elevation = p.process_by_canpon(frames)
                            plot_datas = [range_time.T, range_doppler.T,range_azimuth.T,range_elevation.T]
                            plot.update(plot_datas)
                            cost_t = time.time() - t2
                            t2 = time.time()
                            print("cost time:{:.2f}s,process time:{:.2f}".format(cost_t,t2 - t1))
                            pack_list = pack_list[(loop_size - step_size) * num_tx * num_rx:]  
    except KeyboardInterrupt:
        pass

def main():
    local_udp_ip = "192.168.0.3"
    local_udp_port = 6000
    fpga_udp_ip = "192.168.0.2"
    fpga_udp_port = 5000
    txs = param['txs']
    rxs = param['rxs']
    r = Receive(local_udp_ip,local_udp_port,fpga_udp_ip,fpga_udp_port)
    msg,result = r.setting(txs,rxs)
    if result < 0:
        print(msg)
        exit(0)

    recv_thd = threading.Thread(target=r.recv_data)
    recv_thd.setDaemon(True)
    recv_thd.start()    
    process_data(param)

if __name__ == '__main__':
    main()