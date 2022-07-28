import time
import numpy as np
from scipy import interpolate
from scipy import signal

from pyqtgraph.Qt import QtGui, QtCore,QtWidgets
import pyqtgraph.opengl as gl
import pyqtgraph as pg

from libs.utils import *
from libs.conf import param
from libs.reader import RawDataReader
from libs.process import Process
from libs.plot import PlotData
from libs.mti import Mti


def main():
    file_name = './data/1658977383294.dat'
    reader = RawDataReader(file_name,param)
    framelist = []
    while True:
        frame = reader.get_next_frame()
        if frame is None:
            break
        framelist.append(frame)

    txs = np.unique([f['tx'] for f in framelist])
    rxs = np.unique([f['rx'] for f in framelist])

    param['txs'] = txs
    param['rxs'] = rxs
    framelist = align_data(framelist,param)
    range_data = struct_to_cube(framelist,param)
    (frame_cnt,num_tx,num_rx,bin_cnt) = range_data.shape
    # loop each tx * rx; 1/2 sec
    loop_size = round(param['fps'] / len(txs) /len(rxs) / 2)
    # step size 1/8 sec
    step_size = round(param['fps'] / len(txs) /len(rxs) / 8)

    p = Process(param)
    plot = PlotData()
    
    for i in range(0,frame_cnt - loop_size,step_size):
        frames = range_data[i:i+loop_size,:,:,:]
        # X,Y,Z,E = p.point_cloud(frames)
        range_time, range_doppler,range_azimuth,range_elevation = p.process_by_canpon(frames)
        plot_datas = [range_time.T, range_doppler.T,range_azimuth.T,range_elevation.T]
        plot.update(plot_datas)
        time.sleep(0.1)

    

    
        
        
if __name__ == '__main__':
    main()