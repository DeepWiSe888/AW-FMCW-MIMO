function range_data = struct_to_cube(framelist,param)
    num_tx = param.num_tx;
    num_rx = param.num_rx;
    range_fft_n = param.range_fft_n;
    
    frame_len = length(framelist);
    total_loop_size = floor(frame_len / (num_tx * num_rx));
    framelist = framelist(1:total_loop_size * num_tx*num_rx);

    bin_cnt = range_fft_n / 2;
    range_data = zeros(total_loop_size,num_tx,num_rx,bin_cnt);
    for i = 1:total_loop_size
        for j = 1:num_tx
            for k = 1:num_rx
                idx = (i-1)*num_tx*num_rx + (j - 1) * num_rx + k;
                tmp = framelist(idx).adc;
                %tmp = match_filter(tmp);
                tmp_fft = range_fft(tmp,range_fft_n);
                range_data(i,j,k,:) = tmp_fft(1:bin_cnt);
            end
        end
    end
    range_data = permute(range_data,[2,3,1,4]);
end