import struct


from protocol import *
import util

class Block:
    BLOCK_INFO_FIELDS = [
        "reserved",
        "block_obj",
        "parent_class",
        "klass",
        "dd_ref",
        "dd_rev",
        "profile",
        "profile_rev",
        "exec_time",
        "num_param",
        "address_of_view1",
        "num_of_views"
    ]

class Directory:
    DIR_INFO_FIELDS = [
        "dir_id",
        "rev_num",
        "num_dir_obj",
        "num_dir_entry",
        "first_comp_list_dir_entry",
        "num_comp_list_dir_entry"
    ]
    
    def __init__(self, conn, address):
        self.conn = conn
        self.address = address
        
        self.pbs = []
        self.tbs = []
        self.fbs = []
        self.los = []
    
    def _r(self, slot, idx):
        d = self.conn.readparam(self.address, slot, idx)
        print(d)
        return d
    
    def read(self):
        # Directory Object Header von Gerät holen
        self.doh = DirectoryObjectHeader(self._r(1, 0))
        
        # Directory Objects holen
        cld = self._r(1, 1)
        
        pb_idx = pb_off = num_pb = 0
        tb_idx = tb_off = num_tb = 0
        fb_idx = fb_off = num_fb = 0
        lo_idx = lo_off = num_lo = 0
        
        if self.doh.num_comp_list_dir_entry > 0:
            pb = CompositeListDirectoryEntries(cld[0:4])
            self.pbs = self._read_blocks(pb)

        if self.doh.num_comp_list_dir_entry > 1:
            tb = CompositeListDirectoryEntries(cld[4:8])
            self.tbs = self._read_blocks(tb)
            
        if self.doh.num_comp_list_dir_entry > 2:
            fb = CompositeListDirectoryEntries(cld[8:12])
            self.fbs = self._read_blocks(fb)
            
        if self.doh.num_comp_list_dir_entry > 3:
            lo = CompositeListDirectoryEntries(cld[12:16])
            self.los = self._read_blocks(lo)
        
        """
        for b in self.pbs:
            print("PB at %d/%d with %d params" % (b[0], b[1], b[2]))
            b = (b[0], b[1]+100, b[2])
            ds32 = self._r(b[0], b[1])
            _, block_obj, parent_class, klass, dd_ref, dd_rev, profile, profile_rev, exec_time, num_param, address_of_view1, num_of_views = struct.unpack(">BBBBIHHHBHHB", ds32)
            for i in range(1, b[2]):
                print(self._r(b[0], b[1] + i))
            print(block_obj, parent_class, klass, dd_ref, dd_rev, profile, profile_rev, exec_time, num_param, address_of_view1, num_of_views)
        for b in self.tbs:
            print("TB at %d/%d with %d params" % (b[0], b[1], b[2]))
        for b in self.fbs:
            print("FB at %d/%d with %d params" % (b[0], b[1], b[2]))
        for b in self.los:
            print("LO at %d/%d with %d params" % (b[0], b[1], b[2]))
        """
    def _read_blocks(self, cld_entry):
        idx, off, num = cld_entry.idx, cld_entry.off, cld_entry.num
        off = (off - 1)*4
        blocks = self._r(1, idx)[off:off+num*4]
        ret = []
        for i in range(0, num):
            ret.append(CompositeDirectoryEntries(blocks[i*4:(i+1)*4]))
        return ret
    
    def read_block(self, slot, idx):
        if self.address == 7 and slot == 1 and idx == 14:
            idx = 114
        block = BlockInfo(self._r(slot, idx))
        return block
    

