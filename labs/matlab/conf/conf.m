%% radar basic characteristic
radar_band  = "S";
if radar_band == "C"
    % the radar sweep time
    sweep_time = 0.5e-3;

    % start scan frequency
    start_freq = 5.2e9;

    % end scan frequency
    end_freq = 8.2e9;

    % bandwidth
    B = end_freq - start_freq;

    % IF adc sample 1MHz
    if_fs = 1e6;

    % offeset IF = 140 KHz
    offset_if = 140e3;

    % antenna fps
    fps = 2000;
    
    % the number of points of range fft
    num_range_nfft = 512;
elseif radar_band == "S"
    % the radar sweep time
    sweep_time = 0.5e-3;

    % start scan frequency
    start_freq = 2e9;

    % end scan frequency
    end_freq = 4e9;

    % bandwidth
    B = end_freq - start_freq;

    % IF adc sample 1MHz
    if_fs = 1e6;

    % offeset IF = 140 KHz
    offset_if = 100e3;

    % antenna fps
    fps = 2000;
    
    % the number of points of range fft
    num_range_nfft = 2048;
end
% speed of light
c = 3e8;

% slope
S = B / sweep_time;

% an object at a distance d produces an IF frequence of:
% f_if = (2 * S) * d / c
% maximum range 
d_max = if_fs * c / (2 * S);

%%
% pack flag
flag = 'wirush-vpas:';
flag_size = length(flag);

% FPGA use antenna no
txs = [1,2,3,4];
rxs = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16];

% the number of tx
num_tx = length(txs);

% the number of rx
num_rx = length(rxs);


%% The Process Parameters
% data size after traversing each antenna
loop_size = num_tx * num_rx;

% the number of loops each  frame
num_loop_per_frame = round(fps / num_tx / num_rx) * 4;
step_size = round(fps / num_tx / num_rx) * 2;

% frame size,the data length of each processing window
frame_size = num_loop_per_frame * loop_size;

% remove dc
remove_dc = 1;

% the number of points of range bin
num_range_bins = num_range_nfft / 2;

% the number of points of doppler fft
num_doppler_nfft = 64;

% the number of points of angle fft
num_angle_nfft = 180;

% range resolution
range_res = d_max / num_range_nfft;

% the range searched on the distance dimension
search_start = round(offset_if / if_fs * num_range_nfft);

% scann area,unit:m
scann_area = 3;

search_end = round(search_start + scann_area / range_res);
% search_end = 150;

