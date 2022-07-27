function framelist = align_data(framelist,param)
    frame_len = length(framelist);
    slice_idx = 1;
    txs = param.txs;
    rxs = param.rxs;
    num_tx = param.num_tx;
    num_rx = param.num_rx;
    for i = 1:frame_len
        txno = framelist(i).txno;
        rxno = framelist(i).rxno;
        if txno == txs(1) && rxno == rxs(1)
            slice_idx = i;
            break;
        end
    end
    framelist = framelist(slice_idx:end);
    frame_len = length(framelist);
    total_loop_size = floor(frame_len / (num_tx * num_rx));
    framelist = framelist(1:total_loop_size * num_tx*num_rx);
end