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
        
        marker = random.randint(0x00, 0xff)
        packet = struct.pack("BBBB", marker, address, slot, index)
        
        print("Sending packet:", file=sys.stderr)
        util.dump_hex(packet)
        
        self.sock.send(packet)
        try:
            data = self.sock.recv(256)
        except socket.timeout:
            print("Timeout!", file=sys.stderr)
            return b""
        
        print("Received packet:", file=sys.stderr)
        util.dump_hex(data)
        
        if data[0] != marker:
            print("Received reply with wrong marker!", file=sys.stderr)
            return b""
        else:
            self.cache[key] = data[1:]
            return data[1:]