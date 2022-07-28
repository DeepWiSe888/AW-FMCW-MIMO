import os
import sys
import time
import struct
import numpy as np
from scipy import signal,ndimage

def parse_pack_from_file(param,pack):
    """
    parse save file packet

    Parameters
    ----------
    pack : bytes
        stream packet

    Returns
    -------
    pack_dict : dict
        packet dict after parse
    
    """
    cursor = 0
    # flag
    flag_pack_tmp = pack[0:cursor + param['flag_size']]
    cursor = cursor + param['flag_size']

    # timestamp
    timestamp_pack_tmp = pack[cursor:cursor + 8]
    timestamp = list(struct.unpack('>Q',timestamp_pack_tmp))[0]
    cursor = cursor + 8

    # antenna no
    tx_pack_tmp = pack[cursor:cursor + 2]
    tx_antenna_no = list(struct.unpack('>H',tx_pack_tmp))[0]
    cursor = cursor + 2

    rx_pack_tmp = pack[cursor:cursor + 2]
    rx_antenna_no = list(struct.unpack('>H',rx_pack_tmp))[0]
    cursor = cursor + 2

    # frame no
    fn_pack_tmp = pack[cursor:cursor + 4]
    frame_no = list(struct.unpack('>L',fn_pack_tmp))[0]
    cursor = cursor + 4

    # adc data
    adc_pack_tmp = pack[cursor:]
    adc = list(struct.unpack('{}B'.format(len(adc_pack_tmp)),adc_pack_tmp))

    pack_dict = {'tx':tx_antenna_no,'rx':rx_antenna_no,'fn':frame_no,'t':timestamp,'adc':adc}
    return pack_dict

def parse_pack_from_stream(pack,param):
    """
    parse stream packet

    Parameters
    ----------
    pack : bytes
        stream packet

    Returns
    -------
    save_pack : bytes
        stream which add the timestamp
    
    pack_dict : dict
        packet dict after parse
    
    """
    cursor = 0
    # flag
    flag_pack_tmp = pack[0:cursor + param['flag_size']]
    cursor = cursor + param['flag_size']

    # antenna no
    tx_pack_tmp = pack[cursor:cursor + 2]
    tx_antenna_no = list(struct.unpack('>H',tx_pack_tmp))[0]
    cursor = cursor + 2

    rx_pack_tmp = pack[cursor:cursor + 2]
    rx_antenna_no = list(struct.unpack('>H',rx_pack_tmp))[0]
    cursor = cursor + 2

    # frame no
    fn_pack_tmp = pack[cursor:cursor + 4]
    frame_no = list(struct.unpack('>L',fn_pack_tmp))[0]
    cursor = cursor + 4

    # adc data
    adc_pack_tmp = pack[cursor:]
    adc = list(struct.unpack('{}B'.format(len(adc_pack_tmp)),adc_pack_tmp))

    # timestamp
    timestamp = int(round(time.time() * 1000))
    timestamp_pack_tmp = struct.pack('>Q',timestamp)

    save_pack = flag_pack_tmp + timestamp_pack_tmp + tx_pack_tmp + rx_pack_tmp + fn_pack_tmp + adc_pack_tmp
    pack_dict = {'tx':tx_antenna_no,'rx':rx_antenna_no,'fn':frame_no,'t':timestamp,'adc':adc}
    
    return save_pack,pack_dict

def align_data(framelist,param):
    txs = param['txs']
    rxs = param['rxs']

    num_tx = len(txs)
    num_rx = len(rxs)

    slice_idx = 0
    for i,frame in enumerate(framelist):
        tx = frame['tx']
        rx = frame['rx']
        if tx == txs[0] and rx == rxs[0]:
            slice_idx = i
            break
    framelist = framelist[slice_idx:]
    frame_len = len(framelist)
    total_loop_size = int(np.floor(frame_len / (num_tx * num_rx)))
    framelist = framelist[:total_loop_size * num_tx * num_rx]
    return framelist

def match_filter(data):
    h = np.conj(data[::-1])
    data = np.convolve(data,h)
    return data

def range_fft(data,range_fft_n):
    data =  data * np.hanning(len(data))
    data_fft = np.fft.fft(data,range_fft_n)
    return data_fft

def doppler_fft(data,doppler_fft_n = 64):
    data =  data * np.hanning(len(data))
    data_fft = np.fft.fftshift(np.fft.fft(data,doppler_fft_n))
    return data_fft

def angle_fft(data,angle_fft_n = 180):
    data_fft = np.fft.fftshift(np.fft.fft(data,angle_fft_n))
    return data_fft

def struct_to_cube(framelist,param):
    txs = param['txs']
    rxs = param['rxs']
    num_range_nfft = param["num_range_nfft"]

    num_tx = len(txs)
    num_rx = len(rxs)

    frame_len = len(framelist)
    total_loop_size = int(np.floor(frame_len / (num_tx * num_rx)))
    bin_cnt = num_range_nfft // 2
    range_data = np.zeros((total_loop_size,num_tx,num_rx,bin_cnt),dtype=np.complex_)
    for i in range(total_loop_size):
        for j in range(num_tx):
            for k in range(num_rx):
                idx = i*num_tx*num_rx + j* num_rx + k
                frame = framelist[idx]
                tmp = frame['adc']
                tmp_fft = range_fft(tmp,num_range_nfft)
                range_data[i,j,k,:] = tmp_fft[:bin_cnt]
    return range_data

def cfar(x, num_train, num_guard, rate_fa):
    num_cells = x.size
    num_train_cell = num_train // 2
    num_guard_cell = num_guard // 2
    num_side = num_train_cell + num_guard_cell
    alpha = num_train * (rate_fa ** (-1 / num_train) - 1)
    peaks= []
    for i in range(num_side, num_cells - num_side):
        if i != i-num_side + np.argmax(x[i-num_side : i+num_side+1]): 
            continue
        all_sum = np.sum(x[i-num_side : i+num_side+1])
        guard_sum = np.sum(x[i-num_guard_cell : i+num_guard_cell+1]) 
        p_noise = (all_sum - guard_sum) / num_train 
        thre = alpha * p_noise
        if x[i] > thre: 
            peaks.append(i)
    peaks = np.array(peaks)
    return peaks

def gen_steering_vec(angle_one_sided,ant_cnt):
    angle_res = 1
    angle_points = round(2 * angle_one_sided / angle_res + 1)
    steering_vector = np.zeros((angle_points, ant_cnt), dtype=np.complex_)
    for ii in range(angle_points):
        for jj in range(ant_cnt):
            mag = -1 * np.pi * jj * np.sin((-angle_one_sided + ii * angle_res) * np.pi / 180)
            real = np.cos(mag)
            imag = np.sin(mag)
            steering_vector[ii, jj] = real + 1j * imag
    return steering_vector

def forward_backward_avg(Rxx):
    assert np.size(Rxx, 0) == np.size(Rxx, 1)

    M = np.size(Rxx, 0)
    Rxx = np.matrix(Rxx)

    J = np.eye(M)
    J = np.fliplr(J) 
    J = np.matrix(J)
    
    Rxx_FB = (Rxx + J * np.conj(Rxx) * J) / 2
    return np.array(Rxx_FB)

def smooth_matrix(data):
    conv_k = np.ones((5,5)) / 25
    conv_data = signal.convolve2d(data,conv_k,'same')
    conv_data = ndimage.gaussian_filter(conv_data,sigma=7)
    return conv_data
    
def capon(data):
    (frame_cnt_n,ant_cnt,bin_cnt) = data.shape
    steering_vector = gen_steering_vec(90,ant_cnt)
    capon_map = np.zeros((181,bin_cnt),dtype=np.complex_)
    for i in range(bin_cnt):
        X = data[:,:,i]
        X = X.T
        R = X @ np.conj(X.T)
        R = forward_backward_avg(R)
        R = np.divide(R, frame_cnt_n)
        R_INV = np.linalg.inv(R)
        tmp = R_INV @ steering_vector.T
        mvdr_result = np.reciprocal(np.einsum('ij,ij->i', steering_vector.conj(), tmp.T))
        capon_map[:,i] = np.array(abs(mvdr_result))
    capon_map = np.real(capon_map)
    capon_map_conv = smooth_matrix(capon_map)
    return capon_map_conv

    
    

