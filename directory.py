import struct

import util


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
        return self.conn.readparam(self.address, slot, idx)
    
    def read(self):
        # Directory Object Header von Gerät holen
        directory_object_header = struct.unpack(">HHHHHH", self._r(1, 0))
        util.set_fields(self, directory_object_header, Directory.DIR_INFO_FIELDS)
        
        # Directory Objects holen
        composite_list_directory = self._r(1, 1)
        
        pb_idx = pb_off = num_pb = 0
        tb_idx = tb_off = num_tb = 0
        fb_idx = fb_off = num_fb = 0
        lo_idx = lo_off = num_lo = 0
        
        if self.num_comp_list_dir_entry > 0:
            pb_idx, pb_off, num_pb = struct.unpack(">BBH", composite_list_directory[0:4])

        if self.num_comp_list_dir_entry > 1:
            tb_idx, tb_off, num_tb = struct.unpack(">BBH", composite_list_directory[4:8])
            
        if self.num_comp_list_dir_entry > 2:
            fb_idx, fb_off, num_fb = struct.unpack(">BBH", composite_list_directory[8:12])
            
        if self.num_comp_list_dir_entry > 3:
            lo_idx, lo_off, num_lo = struct.unpack(">BBH", composite_list_directory[12:16])
        
        self.pbs = self._read_blocks(pb_idx, pb_off, num_pb)
        self.tbs = self._read_blocks(tb_idx, tb_off, num_tb)
        self.fbs = self._read_blocks(fb_idx, fb_off, num_fb)
        self.los = self._read_blocks(lo_idx, lo_off, num_lo)
        
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
    
    def _read_blocks(self, idx, off, num):
        off = (off - self.num_comp_list_dir_entry - 1)*4
        blocks = self._r(1, idx)[off:off+num*4]
        ret = []
        for i in range(0, num):
            ret.append(struct.unpack(">BBH", blocks[i*4:(i+1)*4]))
        return ret

    
    def dir_info(self):
        return util.get_fields_info(self, Directory.DIR_INFO_FIELDS)
