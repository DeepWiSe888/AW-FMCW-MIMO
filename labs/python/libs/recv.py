import queue
import socket

from libs.conf import *
from libs.utils import *

Cache = queue.Queue()

class Receive(object):
    def __init__(self,
                local_udp_ip = "192.168.0.3",local_udp_port = 6000,
                fpga_udp_ip = "192.168.0.2",fpga_udp_port = 5000):
        
        # udp 
        self.local_udp_ip = local_udp_ip
        self.local_udp_port = local_udp_port
        self.fpga_udp_ip = fpga_udp_ip,
        self.fpga_udp_port = fpga_udp_port
        # receive data buffer
        self.recv_buffer = bytes()
        # last frame no
        self.last_fn = 0

    def antenna_cmd(self,antenna_idxs,type):
        """
        antenna cmd

        Parameters
        ----------
        antenna_idxs : list
            antenna index to use

        type : int
            tx or rx

        Returns
        -------
        cmd : bytes
            the cmd packet 
        
        Examples
        -------
        tx no [4 3 2 1]

        rx no [16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1]

        use_tx = int('1000',2).to_bytes(1,'big')

        use_rx = int('0000000000011111',2).to_bytes(2,'big')
        """
        cmd = []
        byte_len = 1
        # tx
        if type == 1:
            cmd = ['0' for i in range(4)]
            byte_len = 1
        else:
            cmd = ['0' for i in range(16)]
            byte_len = 2
        if max(antenna_idxs) > len(cmd) or min(antenna_idxs) < 1:
            pass
        else:
            for idx in antenna_idxs:
                cmd[idx - 1] = '1'
            cmd = cmd[::-1]
        cmd_str = ''.join(cmd)
        antenna_cmd = int(cmd_str,2).to_bytes(byte_len,'big')
        return antenna_cmd

    def select_use_antenna(self,txs,rxs):
        """
        select tx and rx to use

        Parameters
        ----------
        txs : list
            txs list to use

        rxs : list
            rxs list to use

        Returns
        -------
        cmd : bytes
            the cmd packet 
        
        """
        use_tx = self.antenna_cmd(txs,1)
        use_rx = self.antenna_cmd(rxs,2)
        cmd = b'\xef\xfe\x0e\x00' + use_tx + use_rx + b'\xee'
        return cmd

    def setting(self,select_txs,select_rxs):
        msg = ""
        result = 0
        self.local_upd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.local_upd_socket.bind((self.local_udp_ip, self.local_udp_port))
        except:
            self.local_upd_socket.close()
            msg = "upd binding error"
            result = -1
        # select the antenna number to use
        cmd = self.select_use_antenna(select_txs,select_rxs)
        try:
            # fpga udp address,send setting to fpga
            self.local_upd_socket.sendto(cmd,("192.168.0.2", 5000))
            pass
        except:
            self.local_upd_socket.close()
            msg = "send setting to fpga error"
            result = -1
        return msg,result
             
    def recv_data(self):
        while True:
            try:
                data, remote_address = self.local_upd_socket.recvfrom(4096)
                if not data:
                    print('disconnect')
                    self.local_upd_socket.close()
                    self.recv_buffer = bytes()
                    break
                Cache.put({'data':{},'byte':data})
            except Exception as e:
                print(e)

    def __exit__(self):
        self.local_upd_socket.close()