from libs.utils import *

class RawDataReader():
    def __init__(self,path,param):
        self.path = path
        self.raw_fid = open(self.path,'rb')
        self.pack_buffer = bytes()
        self.param = param
    def get_next_frame(self,buffer_size = 1024):
        while True:
            if len(self.pack_buffer)  < buffer_size * 2:
                pack = self.raw_fid.read(buffer_size)
                if not pack:
                    return None
                self.pack_buffer += pack
            start_index = self.pack_buffer.find(self.param['flag'])
            if(start_index == -1):
                continue
            end_index = self.pack_buffer.find(self.param['flag'],start_index + self.param['flag_size'])
            if(end_index == -1):
                continue
            else:
                pack = self.pack_buffer[start_index:end_index]
                pack_dict = parse_pack_from_file(self.param,pack)
                self.pack_buffer = self.pack_buffer[end_index:]
                break
        return pack_dict
        
    def close(self):
        self.raw_fid.close()