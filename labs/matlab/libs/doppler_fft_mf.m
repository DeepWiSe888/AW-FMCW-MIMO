function doppler_data = doppler_fft_mf(data,doppler_fft_n)
    %time-range data
    %data size:[frame_cnt,bin_cnt]
    [frame_cnt,bin_cnt] = size(data);
    mf_frame_cnt = frame_cnt*2-1;
    mf_data = zeros(mf_frame_cnt,bin_cnt);
    for i = 1:bin_cnt
        tmp = data(:,i);
        tmp = match_filter(tmp);
        mf_data(:,i) = tmp;
    end
    mf_data = mf_data .* hann(mf_frame_cnt);
    doppler_data = fftshift(fft(mf_data,doppler_fft_n),1);
end