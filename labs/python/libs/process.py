from cgi import parse_multipart
from turtle import distance
import numpy as np
from scipy import signal
from scipy import ndimage
from libs.conf import *
from libs.utils import *

class Process(object):
    def __init__(self,param):
        self.last_peak = 0
        self.param = param

    def process_by_3dfft(self,raw_data):
        #range fft
        raw_data = raw_data[:,:,:,search_start:search_end]
        (frame_cnt_n,tx_cnt,rx_cnt,bin_cnt) = raw_data.shape
        data = np.zeros((frame_cnt_n,tx_cnt,12,bin_cnt),dtype=np.complex_)
        data[:,0,:,:] = raw_data[:,0,0:12,:]
        data[:,1,:,:] = raw_data[:,1,1:13,:]
        data[:,2,:,:] = raw_data[:,2,2:14,:]
        data[:,3,:,:] = raw_data[:,3,3:15,:]
        
        (frame_cnt_n,tx_cnt,rx_cnt,bin_cnt) = data.shape
        
        data = data - np.mean(data,0)
        # range time
        range_time = np.abs(np.mean(data,(1,2)))
        
        #doppler fft
        num_doppler_nfft = self.param['num_doppler_nfft']
        doppler_result = np.zeros((tx_cnt,rx_cnt,num_doppler_nfft,bin_cnt),dtype=np.complex_)
        for i in range(tx_cnt):
            for j in range(rx_cnt):
                for k in range(bin_cnt):
                    tmp = data[:,i,j,k]
                    tmp_fft = doppler_fft(tmp,num_doppler_nfft)
                    doppler_result[i,j,:,k] = tmp_fft
        range_doppler = np.abs(np.mean(doppler_result,(0,1)))
        
        # azimuth 
        num_angle_nfft = self.param['num_angle_nfft']
        azimuth_result = np.zeros((num_angle_nfft,num_doppler_nfft,bin_cnt),dtype=np.complex_)
        elevation_result = np.zeros((num_angle_nfft,num_doppler_nfft,bin_cnt),dtype=np.complex_)
        for i in range(num_doppler_nfft):
            for j in range(bin_cnt):
                azimuth_tmp = np.mean(doppler_result[:,:,i,j],0)
                azimuth_fft = angle_fft(azimuth_tmp,num_angle_nfft)
                azimuth_result[:,i,j] = azimuth_fft
                
                elevation_tmp = np.mean(doppler_result[:,:,i,j],1)
                elevatiom_fft = angle_fft(elevation_tmp,num_angle_nfft)
                elevation_result[:,i,j] = elevatiom_fft
                
        range_azimuth = np.abs(np.mean(azimuth_result,1))
        range_elevation = np.abs(np.mean(elevation_result,1))
        
        range_azimuth = smooth_matrix(range_azimuth)
        range_elevation = smooth_matrix(range_elevation)
                
        return range_time,range_doppler,range_azimuth,range_elevation
        
    def process_by_canpon(self,raw_data):
        #range fft
        raw_data = raw_data[:,:,:,search_start:search_end]
        (frame_cnt_n,tx_cnt,rx_cnt,bin_cnt) = raw_data.shape
        data = np.zeros((frame_cnt_n,tx_cnt,12,bin_cnt),dtype=np.complex_)
        data[:,0,:,:] = raw_data[:,0,0:12,:]
        data[:,1,:,:] = raw_data[:,1,1:13,:]
        data[:,2,:,:] = raw_data[:,2,2:14,:]
        data[:,3,:,:] = raw_data[:,3,3:15,:]
        
        (frame_cnt_n,tx_cnt,rx_cnt,bin_cnt) = data.shape

        data = data - np.mean(data,0)
        # range time
        range_time = np.mean(data,(1,2))
        
        # rang doppler
        range_doppler = np.fft.fftshift(np.fft.fft(range_time,64,0),0)
        

        # range azimuth
        azimuth_data = np.mean(data[:,:,0:6,:],1)
        range_azimuth = capon(azimuth_data)
        
        # range elevation
        elevation_data = np.mean(data[:,0:4,0:6,:],2)
        range_elevation = capon(elevation_data)

        # azimuth and elevation
        azimuth_elevation = range_azimuth @ range_elevation.T
        
        return np.abs(range_time), np.abs(range_doppler),np.abs(range_azimuth),np.abs(range_elevation)
    
    def point_cloud(self,raw_data):
        range_time, range_doppler,range_azimuth,range_elevation = self.process_by_canpon(raw_data)
        
        # find the target
        range_doppler_std = np.std(range_doppler,0)
        max_target_idx = np.argmax(range_doppler_std)
        range_res = self.param['range_res']
        dist = range_res * max_target_idx
        
        # point cloud
        azimuth_elevation = np.dot(range_azimuth,range_elevation.T)
        azimuth_bin,elevation_bin = azimuth_elevation.shape
        cfar_thre = np.max(azimuth_elevation) * 0.85
        azimuth_idxs,elevation_idxs = np.where(azimuth_elevation > cfar_thre)
        E = azimuth_elevation[azimuth_idxs,elevation_idxs]
        
        azimuth_angle = (azimuth_idxs - (azimuth_bin / 2)) * (np.pi / 180)
        elevation_angle = (elevation_idxs - (elevation_bin / 2)) * (np.pi / 180)
        
        X = dist * np.cos(elevation_angle) * np.sin(azimuth_angle)
        Y = dist * np.cos(elevation_angle) * np.sin(azimuth_angle)
        Z = dist * np.sin(elevation_angle)
        return X,Y,Z,E
