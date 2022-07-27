# configuration
'''
1. The radar switches between the transmitting and receiving antennas with each scan cycle. 
2. The end of the loop is considered a frame.
'''


'''
The radar basic characteristic
'''

radar_band = "C"

if radar_band == "C":
    # the radar sweep time
    sweep_time = 0.5e-3

    # start scan frequency
    start_freq = 5.2e9

    # end scan frequency
    end_freq = 8.2e9

    # bandwidth
    B = end_freq - start_freq

    # speed of light
    c = 3e8

    # IF adc sample 1MHz
    if_fs = 1e6

    # offeset IF = 140 KHz
    offset_if = 140e3

    # antenna fps
    fps = 2000

elif radar_band == "S":
    # the radar sweep time
    sweep_time = 0.5e-3

    # start scan frequency
    start_freq = 2e9

    # end scan frequency
    end_freq = 4e9

    # bandwidth
    B = end_freq - start_freq

    # IF adc sample 1MHz
    if_fs = 2e6

    # offeset IF = 140 KHz
    offset_if = 210e3

    # antenna fps
    fps = 2000

# speed of light
c = 3e8

# slope
S = B / sweep_time


# an object at a distance d produces an IF frequence of:
# f_if = (2 * S) * d / c
# maximum range 
d_max = if_fs * c / (2 * S)


'''
The radar data acquisition parameters
'''

# pack flag
flag = b'\x77\x69\x72\x75\x73\x68\x2d\x76\x70\x61\x73\x3a'
flag_size = 12

# FPGA use antenna no
txs = [1,2,3,4]
rxs = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] #

# the number of tx
num_tx = len(txs)

# the number of rx
num_rx = len(rxs)


'''
The Process Parameters
'''
# data size after traversing each antenna
loop_size = num_tx * num_rx

# the number of loops each  frame
num_loop_per_frame = round(fps / num_tx / num_rx / 2)

step_size = round(fps / num_tx / num_rx / 8)

# frame size,the data length of each processing window
frame_size = num_loop_per_frame * loop_size

# remove dc
remove_dc = True

# the number of points of range fft
num_range_nfft = 512

# the number of points of range bin
num_range_bins = num_range_nfft // 2

# the number of points of doppler fft
num_doppler_nfft = 64

# the number of points of angle fft
num_angle_nfft = 180

# range resolution
range_res = d_max / num_range_nfft

# interpolation points
interp_points = 4

# the range searched on the distance dimension
search_start = round(offset_if / if_fs * num_range_nfft)

# scann area,unit:m
scann_area = 3
# search_end = round(search_start + scann_area / range_res)
search_end = 150

# azimuth range
azimuth_x_min = -(search_end - search_start)
azimuth_x_max = search_end - search_start
azimuth_y_min = 0
azimuth_y_max = search_end - search_start

# elevation range
elevation_x_min = -(search_end - search_start)
elevation_x_max = search_end - search_start
elevation_y_min = elevation_x_min
elevation_y_max = elevation_x_max

# target bin cnt 
target_range_bin = 3

# each target select doppler points
target_speed_cnt = 20

param = {}
param['txs'] = txs
param['rxs'] = rxs
param['num_tx'] = num_tx
param['num_rx'] = num_rx
param['fps'] = fps
param["flag"] = flag
param["flag_size"] = flag_size
param["loop_size"]= loop_size
param["num_loop_per_frame"] = num_loop_per_frame
param["step_size"] = step_size
param["frame_size"] = frame_size
param["remove_dc"] = remove_dc
param["num_range_nfft"] = num_range_nfft
param["num_range_bins"] = num_range_bins
param["num_doppler_nfft"] = num_doppler_nfft
param["num_angle_nfft"] = num_angle_nfft
param["range_res"] = range_res





