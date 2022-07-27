function rm_dc = remove_dc(data)
    % remove the average in time
    % data size:(frame_cnt,bin_cnt)
    rm_dc = data - mean(data,1);
end