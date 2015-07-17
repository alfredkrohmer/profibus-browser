from util import *


DirectoryObjectHeader = make_packet("DirectoryObjectHeader", (
    ("dir_id",                    "H"),
    ("rev_num",                   "H"),
    ("num_dir_obj",               "H"),
    ("num_dir_entry",             "H"),
    ("first_comp_list_dir_entry", "H"),
    ("num_comp_list_dir_entry",   "H")
), payload=False)

CompositeListDirectoryEntries = make_packet("CompositeListDirectoryEntries", (
    ("idx", "B"),
    ("off", "B"),
    ("num", "H")
), payload=False)

CompositeDirectoryEntries = make_packet("CompositeDirectoryEntries", (
    ("slot",       "B"),
    ("idx",        "B"),
    ("num_params", "H")
), payload=False)

BlockInfo = make_packet("BlockInfo", (
    ("reserved",        "B"),
    ("block_obj",       "B"),
    ("parent_class",    "B"),
    ("klass",           "B"),
    ("dd_ref",          "I"),
    ("dd_rev",          "H"),
    ("profile",         "H"),
    ("profile_rev",     "H"),
    ("exec_time",       "B"),
    ("num_param",       "H"),
    ("address_of_view1","H"),
    ("num_of_views",    "B")
), payload=False)

PRIMARY_VALUE = 8
PRIMARY_VALUE_UNIT = 9

TRIMMED_VALUE = 15
SENSOR_UNIT = 14
