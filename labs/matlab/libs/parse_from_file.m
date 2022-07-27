function [timestamp,tx,rx,fn,adc] = parse_from_file(buf,cursor)
    timestamp = swapbytes(typecast(uint8(buf(cursor:cursor + 8 - 1)), 'uint64'));
    cursor = cursor + 8;

    tx = swapbytes(typecast(uint8(buf(cursor:cursor + 2 - 1)), 'uint16'));
    cursor = cursor + 2;

    rx = swapbytes(typecast(uint8(buf(cursor:cursor + 2 - 1)), 'uint16'));
    cursor = cursor + 2;

    fn = swapbytes(typecast(uint8(buf(cursor:cursor + 4 - 1)), 'uint32'));
    cursor = cursor + 4;

    adc = buf(cursor:end);
end