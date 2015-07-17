from struct import unpack

from flask import Flask, request, render_template


from protocol import *
import directory


app = Flask(__name__)
conn = None


objects = {
    1: ("Physical Block", {
        1: ("Transmitter", {250:"Default"})
    }),
    2: ("Function Block", {
        1: ("Input", {1: "Analog Input"}),
        3: ("Control", {1: "PID"}),
        5: ("Calculation", {128: "Unknown"})
    }),
    3: ("Tranducer Block", {
        1: ("Pressure", {4: "Pressure + Level + Flow"}),
        2: ("Temperature", {2: "Resistance Thermometer"})
    }),
}

units = {
    1001: "°C",
    1138: "mbar",
    1342: "%"
}

man = {
    26: "ABB",
    42: "Siemens"
}


@app.route("/")
def index():
    return render_template("select_device.html")

@app.route("/device")
def device():
    addr = int(request.args.get('addr'))
    
    d = directory.Directory(conn, addr)
    d.read()
    
    return render_template("device.html", d=d, addr=addr)

@app.route("/block")
def block():
    addr = int(request.args.get('addr'))
    slot = int(request.args.get('slot'))
    idx = int(request.args.get('idx'))
    
    if idx in (14,):
        idx += 100
    
    d = directory.Directory(conn, addr)
    b = d.read_block(slot, idx)
    print(b)
    
    params = OrderedDict()
    
    # Physical block
    if b.block_obj == 1:
        params["Manufacturer"] = man[unpack(">H", conn.readparam(addr, slot, idx + 10))[0]]
        params["Device ID"] = conn.readparam(addr, slot, idx + 11).decode()
    
    # Function block
    if b.block_obj == 2:
        data = conn.readparam(addr, slot, idx + 10)
        params["Out"], params["Status"] = unpack(">fB", data)
        params["Unit"] = conn.readparam(addr, slot, idx + 35).decode()
    
    # Transducer block
    if b.block_obj == 3:
        if b.parent_class == 1:
            params["Out"], params["Status"] = unpack(">fB", conn.readparam(addr, slot, idx + TRIMMED_VALUE, cached=False))
            params["Unit"] = units[unpack(">H", conn.readparam(addr, slot, idx + SENSOR_UNIT))[0]]
        if b.parent_class == 2:
            params["Out"], params["Status"] = unpack(">fB", conn.readparam(addr, slot, idx + PRIMARY_VALUE, cached=False))
            params["Unit"] = units[unpack(">H", conn.readparam(addr, slot, idx + PRIMARY_VALUE_UNIT))[0]]
    
    return render_template("block.html", slot=slot, idx=idx, o=objects[b.block_obj], b=b, addr=addr, params=params)


@app.route("/read")
def read():
    addr = int(request.args.get('addr'))
    slot = int(request.args.get('slot'))
    idx = int(request.args.get('idx'))
    
    return to_hex(conn.readparam(addr, slot, idx, cached=False))

def run_server(c):
    global conn
    conn = c
    app.run(debug=True)
