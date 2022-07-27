function result = point_clound(frames,param)
    % gen points clound
    %input data size:(n_tx,n_rx,n_frame,n_bin)
    doppler_fft_n = param.doppler_fft_n;
    angle_fft_n = param.angle_fft_n;
    [tx_cnt,rx_cnt,frame_cnt,bin_cnt] = size(frames);
    
    %remove dc
    remove_dc_data = frames - mean(frames,3);
    
    %range doppler
    range_doppler = zeros(tx_cnt,rx_cnt,doppler_fft_n,bin_cnt);
    for i = 1:tx_cnt
        for j = 1:rx_cnt
            tmp = squeeze(remove_dc_data(i,j,:,:));
            range_doppler(i,j,:,:) = doppler_fft(tmp,doppler_fft_n);
        end
    end
    
    %angle fft
    azimuth_fft = zeros(angle_fft_n,doppler_fft_n,bin_cnt);
    elevation_fft = zeros(angle_fft_n,doppler_fft_n,bin_cnt);
    for i = 1:frame_cnt
        for j = 1:bin_cnt
            azimuth_tmp = squeeze(mean(range_doppler(:,:,i,j),1));
            elevation_tmp = squeeze(mean(range_doppler(:,:,i,j),2));
            
            azimuth_fft(:,i,j) = fftshift(fft(azimuth_tmp,angle_fft_n));
            elevation_fft(:,i,j) = fftshift(fft(elevation_tmp,angle_fft_n));
        end
    end
    
    result.range_time = remove_dc_data(:,:,:,param.search_start:param.search_end);
    result.doppler = range_doppler(:,:,:,param.search_start:param.search_end);
    result.azimuth = azimuth_fft(:,:,param.search_start:param.search_end);
    result.elevation = elevation_fft(:,:,param.search_start:param.search_end);
end