import sys


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