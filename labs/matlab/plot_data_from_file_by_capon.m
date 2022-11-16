close all
clc;clear;

addpath libs;
addpath conf;

%load param
conf;
%fft
param.range_fft_n = num_range_nfft;
param.doppler_fft_n = num_doppler_nfft;
param.angle_fft_n = num_angle_nfft;

%target range
param.search_start = search_start;
param.search_end = search_end;
range_resolution = range_res;
angle_bin = num_angle_nfft + 1;
range_bin = search_end - search_start + 1;

%read file
filename = '../python/data/1660450221752.dat';
%read from file
framelist = read_frame(filename);

% data param
txs = unique([framelist.txno]);
rxs = unique([framelist.rxno]);

param.txs = txs;
param.rxs = rxs;
param.num_tx = length(txs);
param.num_rx = length(rxs);
% loop related
win_size = round(fps / param.num_tx / param.num_rx / 2);
step = round(fps / param.num_tx / param.num_rx / 8);

%Slice the start and end
framelist = align_data(framelist,param);

%range fft,size(frame_cnt,num_tx,num_rx,bin_cnt)
range_data = struct_to_cube(framelist,param);

figure(1)
%set(gcf,'position',[18.6,41.8,1086.4,741.6])
set(gcf,'position',[9,279.4,1072.8,469.6])
colormap jet
last_tmp_sum = [];
range_azimuth = zeros(angle_bin,range_bin);
range_elevation = zeros(angle_bin,range_bin);

F = [];
F_CNT = 1;

mti = Mti(angle_bin,range_bin);
%for i = 233:step: length(range_data) - win_size
for i = 1:step: length(range_data) - win_size
    clf;
    %get data
    range_data_tmp = range_data(:,:,i:i+ win_size - 1,:);
    
    % effective virtual antenna array
    range_data_tmp = squeeze([range_data_tmp(1,1:12,:,:);...
        range_data_tmp(2,2:13,:,:);...
        range_data_tmp(3,3:14,:,:);...
        range_data_tmp(4,4:15,:,:);...
        ]);
    range_data_tmp = range_data_tmp - mean(range_data_tmp,3);
    azimuth_doa_data = squeeze(mean(range_data_tmp(:,1:6,:,param.search_start:param.search_end),1));
    
    elevation_doa_data = squeeze(mean(range_data_tmp(1:4,1:6,:,param.search_start:param.search_end),2));
    
    %8*5*256
    
    range_azimuth_conv = capon(azimuth_doa_data);
    range_elevation_conv = capon(elevation_doa_data);


    %range
    plot_range = mean(range_azimuth_conv,1);
    [~,range_index] = max(plot_range);
    
    %xy
    azimuth_max = max(max(range_azimuth_conv));
    [azimuths_idx,ranges_idx] = find(range_azimuth_conv > azimuth_max * 0.60);
    azimuths = (azimuths_idx - (angle_bin / 2)) * (pi / 180);
    ranges = ones(size(azimuths)) * range_index * range_resolution;
    x_pos1 = ranges .* sin(azimuths);
    y_pos1 = ranges .* cos(azimuths);
    
    %2d aoa
    aoa_2d = range_azimuth_conv * range_elevation_conv';
    aoa_max = max(max(aoa_2d));
    [azimuths_idx,elevations_idx] = find(aoa_2d > aoa_max * 0.60);
    
    
    %Pow = aoa_2d(azimuths,elevations);
    
    azimuths = (azimuths_idx - (angle_bin / 2)) * (pi / 180);
    elevations = (elevations_idx - (angle_bin / 2)) * (pi / 180);
    
    ranges = ones(size(azimuths)) * range_index * range_resolution;
    x_pos = ranges .* cos(elevations) .* sin(azimuths);
    y_pos = ranges .* cos(elevations) .* cos(azimuths);
    z_pos = ranges .* sin(elevations);
    %[mean(x_pos),mean(y_pos),mean(z_pos)]
    
    x_mim = min(x_pos);x_max = max(x_pos);
    z_min = min(z_pos);z_max = max(z_pos);
    
    x_idx = -150:1:150;
    y_idx = 0:1:300;
    x_points = round(x_pos1 * 100);
    y_points = round(y_pos1 * 100);
    XY_MAP = zeros(length(x_idx),length(y_idx));
    for j = 1:181
        theta = (j - (angle_bin / 2)) * (pi / 180);
        for k = 1:range_bin
            distance = k * range_resolution * 100;
            x_idx_tmp = round(distance * sin(theta)) + 150;
            y_idx_tmp = round(distance * cos(theta)) + 1;
            if y_idx_tmp >= 1 && y_idx_tmp <= 301 && x_idx_tmp >= 1 && x_idx_tmp <= 301
                XY_MAP(x_idx_tmp,y_idx_tmp) = XY_MAP(x_idx_tmp,y_idx_tmp) + range_azimuth_conv(j,k);
            end
        end
    end
    conv_k = ones(5,5) / 25;
    XY_MAP = conv2(XY_MAP,conv_k,'same');
    [X,Y] =meshgrid(x_idx,y_idx);Z=peaks(X,Y);     %间隔为0.25
    p_xi = -150:0.1:150;
    p_zi = 0:0.1:300;
    [XI,YI]=meshgrid(p_xi,p_zi);          %XI间隔为0.33，YI间隔为0.05
    XY_MAP=interp2(X,Y,XY_MAP,XI,YI,'cubic');
    
    
    
    %处理能量数据  XZ
    p_x = mean(x_pos) - 1:0.1:mean(x_pos) + 1;
    p_z = mean(z_pos) - 2:0.1:mean(z_pos) + 2;
    XZ_MAP = zeros(length(p_x),length(p_z));
    for j = 1:length(x_pos)
        x_tmp = x_pos(j);
        z_tmp = z_pos(j);
        p_tmp = aoa_2d(azimuths_idx(j),elevations_idx(j));

        [x_min, x_idx] = min(abs(x_tmp - p_x));
        [z_min, z_idx] = min(abs(z_tmp - p_z));
        if x_min < 0.5 && z_min < 0.5
            XZ_MAP(x_idx,z_idx) = XZ_MAP(x_idx,z_idx) + p_tmp;
        end
    end
    
    [X,Y] =meshgrid(p_x,p_z);Z=peaks(X,Y);     %间隔为0.25
    p_xi = mean(x_pos) - 1:0.01:mean(x_pos) + 1;
    p_zi = mean(z_pos) - 2:0.01:mean(z_pos) + 2;
    [XI,YI]=meshgrid(p_xi,p_zi);          %XI间隔为0.33，YI间隔为0.05
    XZ_MAP=interp2(X,Y,XZ_MAP',XI,YI,'cubic');
    
    subplot(121)
    imagesc(range_azimuth_conv)
    xlabel("Range(m)")
    ylabel("Azimuth(rad)")
    yt = str2double(string(yticklabels)) - 90;
    yticklabels(yt)
    xt = str2double(string(xticklabels)) * range_resolution;
    xticklabels(xt)

    subplot(122)
    imagesc(range_elevation_conv)
    xlabel("Range(m)")
    ylabel("Elevation(rad)")
    yt = str2double(string(yticklabels)) - 90;
    yticklabels(yt)
    xt = str2double(string(xticklabels)) * range_resolution;
    xticklabels(xt)
    
    %     subplot(121)
    %     imagesc(XY_MAP')
    %     yticks([])
    %     xticks([])
    %     ylabel("Y(m)")
    %     xlabel("X(m)")
    %     set(gca,'YDir','normal')
    % 
    %     subplot(122)
    %     imagesc(XZ_MAP)
    %     yticks([])
    %     xticks([])
    %     ylabel("Z(m)")
    %     xlabel("X(m)")

    
    cdata(1,:,:,:) = getframe(gcf).cdata;
    F = [F;cdata];
    pause(0.01)
end

% save images as video
write2video('C_BAND_10',F,8);










