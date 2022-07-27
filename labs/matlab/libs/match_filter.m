function mf_data = match_filter(data)
    h = conj(data(end:-1:1));
    mf_data = conv(data,h);
end