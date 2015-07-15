import sys

from socket import *
from fcntl import ioctl
from sys import argv, exit, stdout, stderr
from struct import pack, unpack, calcsize
from collections import namedtuple, OrderedDict


def to_hex(s):
    return ":".join("{:02x}".format(c) for c in s)

def dump_hex(s):
    print(to_hex(s), file=sys.stderr)

def set_fields(obj, s, args):
    for i, name in enumerate(args):
        setattr(obj, name, s[i])

def collect_fields(obj, args):
    fields = []
    for name in args:
        fields.append(getattr(obj, name))
    return fields

def get_fields_info(obj, args):
    fields = collect_fields(obj, args)
    info = ""
    for i, name in enumerate(args):
        info += name + ": " + str(fields[i]) + "\n"
    return info

def make_packet(name, fields, statics={}, payload=True, payload_size_field=None, payload_offset=0, vlf=None, vlf_size_field=None):
    fields = OrderedDict(fields)
    fmt = ">" + "".join([(f[0] if isinstance(f, tuple) else f) for f in fields.values()])
    size = calcsize(fmt)
    
    f = list(fields.keys())
    if payload:
        f.append("payload")
    if vlf is not None:
        f.append(vlf)
    
    t = namedtuple(name, f)
    class _class(t):
    
        def __new__(cls, *args, **kwargs):
        
            # unpack (parse packet)
            if len(args) == 1:
                data = args[0]
                
                # unpack known-size fields
                unpacked = unpack(fmt, data[0:size])
                
                kw = {}
                
                # handle variable length fields
                if vlf is not None:
                    vlf_size = unpacked[list(fields.keys()).index(vlf_size_field)]
                    kw[vlf] = data[size:size+vlf_size]
                else:
                    vlf_size = 0
                
                # handle payload
                if payload:
                    if payload_size_field is not None:
                        pl_size = unpacked[list(fields.keys()).index(payload_size_field)] + payload_offset
                        kw["payload"] = data[size+vlf_size:size+vlf_size+pl_size]
                    else:
                        kw["payload"] = data[size+vlf_size:]
                
                # finally create instance
                self = t.__new__(cls, *unpacked, **kw)

            # pack (create packet)
            else:
                self = t.__new__(cls, *args, **kwargs)

            return self

        def __str__(self):
            ret = "%s packet (%d bytes)\n" % (name, len(self))
            for k, v in fields.items():
                ret += k + ": "
                value = getattr(self, k)
                if isinstance(v, tuple):
                    if isinstance(v[1], str):
                        ret += v[1] % value
                    else:
                        ret += v[1](value)
                else:
                    ret += str(value)
                ret += "\n"
            return ret
        
        def __bytes__(self):
            packed = pack(fmt, *(getattr(self, key) for key in fields.keys()))
            if vlf is not None:
                packed += bytes(getattr(self, vlf))
            if payload:
                packed += bytes(self.payload)
            return packed

        def __len__(self):
            s = size
            if vlf is not None:
                s += len(bytes(getattr(self, vlf)))
            if payload:
                s += len(self.payload)
            return s

    _class.fmt = fmt
    _class.fmt_size = size

    for k, v in statics.items():
        setattr(_class, k, v)

    return _class
