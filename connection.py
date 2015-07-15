import socket
import struct
import random
import sys

import util


class Connection:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)
        self.sock.connect((host, port))
        self.cache = {}

    def readparam(self, address, slot, index, cached=True):
        key = (address, slot, index)
        if cached and key in self.cache:
            return self.cache[key]
        
        for i in range(0, 3):
            marker = random.randint(0x00, 0xff)
            packet = struct.pack("BBBB", marker, address, slot, index)
            
            self.sock.send(packet)
            try:
                data = self.sock.recv(256)
            except socket.timeout:
                print("Timeout!", file=sys.stderr)
                return b""
            
            # check marker
            if data[0] != marker:
                return b""
            
            data = data[1:]
            if len(data) > 0:
                break
        
        self.cache[key] = data
        return data
