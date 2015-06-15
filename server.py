import cherrypy

import directory

class Browser(object):
    def __init__(self, conn):
        self.conn = conn
    
    @cherrypy.expose
    def index(self):
        return """
<h1>Read Device Info</h1>
<form action="/device" method="get">
<label>Device ID:</label>
<br/>
<input name="addr" />
<br/>
<input type="submit" />
</form>"""
        
    @cherrypy.expose
    def device(self, addr):
        addr = int(addr)
        d = directory.Directory(self.conn, addr)
        d.read()
        resp = "<ul>"
        resp += "<li>Directory ID: %d</li>" % d.dir_id
        resp += "<li>Revision: %d</li>" % d.rev_num
        resp += "<li>Number of Directory Objects: %d</li>" % d.num_dir_obj
        resp += "<li>Number of Directory Entries: %d</li>" % d.num_dir_entry
        resp += "<li>First composition list directory entry: %d</li>" % d.first_comp_list_dir_entry
        resp += "<li>Number of composition list directory entries: %d</li>" % d.num_comp_list_dir_entry
        if d.pbs:
            resp += "<li>Physical Blocks:<ul>"
            for i, pb in enumerate(d.pbs):
                resp += "<li><a href=\"/pb?addr=%d&slot=%d&idx=%d&params=%d\">PB %d (Slot %d, Index %d, %d parameters)</a></li>" % (addr, pb[0], pb[1], pb[2], i, pb[0], pb[1], pb[2])
            resp += "</ul></li>"
        if d.tbs:
            resp += "<li>Transducer Blocks:<ul>"
            for i, tb in enumerate(d.tbs):
                resp += "<li><a href=\"/tb?addr=%d&slot=%d&idx=%d&params=%d\">TB %d (Slot %d, Index %d, %d parameters)</a></li>" % (addr, tb[0], tb[1], tb[2], i, tb[0], tb[1], tb[2])
            resp += "</ul></li>"
        if d.fbs:
            resp += "<li>Functional Blocks:<ul>"
            for i, fb in enumerate(d.fbs):
                resp += "<li><a href=\"/fb?addr=%d&slot=%d&idx=%d&params=%d\">FB %d (Slot %d, Index %d, %d parameters)</a></li>" % (addr, fb[0], fb[1], fb[2], i, fb[0], fb[1], fb[2])
            resp += "</ul></li>"
        resp += "</ul>"
        return resp

    @cherrypy.expose
    def pb(self, addr, slot, idx, params):
        addr = int(addr)
        slot = int(slot)
        idx = int(idx)
        
        d = directory.Directory(self.conn, addr)
        b = d.read_block(slot, idx)
        
        resp = "<h1>Physical Block</h1> on <a href=\"/device?addr=%d\">Device at Address %d</a>, Slot %d, Index %d" % (addr, addr, slot, idx)
        resp += "<ul>"
        resp += "<li>Block Object: %d</li>" % b.block_obj
        resp += "<li>Parent class: %d</li>" % b.parent_class
        resp += "<li>Class: %d</li>" % b.klass
        resp += "<li>Device Description Reference: %d</li>" % b.dd_ref
        resp += "<li>Device Description Revision: %d</li>" % b.dd_rev
        resp += "<li>Profile: %s</li>" % hex(b.profile)
        resp += "<li>Profile revision: %s</li>" % hex(b.profile_rev)
        resp += "<li>Execution time: %d</li>" % b.exec_time
        resp += "<li>Number of parameters: %d</li>" % b.num_param
        resp += "<li>Address of View 1: %d</li>" % b.address_of_view1
        resp += "<li>Number of Views: %d</li>" % b.num_of_views
        resp += "</ul>"
        
        return resp

def run_server(*args, **kwargs):
    cherrypy.quickstart(Browser(*args, **kwargs))