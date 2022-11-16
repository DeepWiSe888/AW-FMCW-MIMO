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
filename = '../python/data/1658742915340.dat';
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

%move target indicate
mti = Mti(param.doppler_fft_n,param.range_fft_n/2);

%find target peak
ftp = FindTargetPeak(15);

figure(1)
set(gcf,'position',[18.6,270.6,1086.4,477.6])
colormap jet
last_tmp_sum = [];
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
    
    result = point_clound(range_data_tmp,param);
    
    %time range
    time_range = squeeze(sum(abs(result.range_time),[1,2]));
    
    %non-coherent
    non_coherent = squeeze(sum(abs(result.doppler),[1,2]));
    
    %azimuth
    azimuth = squeeze(sum(abs(result.azimuth),2));
    
    %elevation
    elevation = squeeze(sum(abs(result.elevation),2));
    
    doppler_sum = sum(non_coherent,1);
    %find peak
    peak = ftp.get_tartget_peak(doppler_sum);
    
    %ranges
    ranges = [];
    if peak >2 && peak < length(doppler_sum) - 2
        ranges = (peak-2:peak+2);
    elseif peak <=2
        ranges = (1:5);
    else
        ranges = (length(doppler_sum) - 4:length(doppler_sum));
    end
    
    %doppler points
    doppler_max = max(max(non_coherent(:,ranges)));
    [doppler_idxs,~] = find(non_coherent(:,ranges) > doppler_max * 0.95);
    range_idxs = [];
    for j = 1:length(ranges)
        range_idxs = [range_idxs,repmat(ranges(j),[1,length(doppler_idxs)])];
    end
    
    %azimuth index
    azimuth_result = result.azimuth;
    azimuth_result = azimuth_result(:,doppler_idxs,ranges);
    azimuth_result = reshape(azimuth_result,num_angle_nfft,[]);
    [~,azimuth_idxs] = max(azimuth_result);
    azimuth_idxs = (azimuth_idxs - (num_angle_nfft / 2)) * (pi / num_angle_nfft);
    
    %elevation index
    elevation_result = result.elevation;
    elevation_result = elevation_result(:,doppler_idxs,ranges);
    elevation_result = reshape(elevation_result,num_angle_nfft,[]);
    [~,elevation_idxs] = max(elevation_result);
    elevation_idxs = (elevation_idxs - (num_angle_nfft / 2)) * (pi / num_angle_nfft);
    
    x_pos = range_idxs * range_res .* sin(azimuth_idxs);
    y_pos = range_idxs * range_res .* cos(azimuth_idxs);
    z_pos = range_idxs * range_res .* sin(elevation_idxs);
    
    
    cla
    subplot(221)
    imagesc(non_coherent)
    %view(1,1)    
    
    subplot(222)
    %imagesc(non_coherent)
    plot(doppler_sum)
    title(peak)
    
    subplot(223)
    imagesc(azimuth)
    %view(1,1) 
    
    subplot(224)
    imagesc(elevation)
    %imagesc(angle_result)
    %view(90,0)  
    
    %rectangle('Position',[-0.20,1.0,1.00,1.90],'Linewidth',1,'EdgeColor','r');
    %axis([-1.30,1.30,0.0,3.00])
    %hold on
    %plot(x_pos,y_pos,'LineStyle','none','Marker','o','MarkerSize',10,'MarkerFace','b') %,'MarkerEdge',[1,0,0],'LineWidth',2
    
    %plot3(x_pos,y_pos,z_pos,'LineStyle','none','Marker','o','MarkerSize',10,'MarkerFace','y','MarkerEdge',[1,0,0],'LineWidth',2)
    %xlabel("X(m)")
    %ylabel("Y(m)")
    
    pause(0.01)
end












