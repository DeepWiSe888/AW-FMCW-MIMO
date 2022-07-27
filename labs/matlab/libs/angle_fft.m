function data_fft = angle_fft(data,angle_fft_n)
    data = data .* hann(length(data));
    data_fft = fftshift(fft(data,angle_fft_n));
end