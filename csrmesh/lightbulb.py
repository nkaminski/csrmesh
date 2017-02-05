import struct
from . import gatt
from . import crypto

def set_light(dest, pin, level, red, green, blue, objid=0):
    cmd = generate_light_set_cmd(level, red, green, blue, objid)

    key = crypto.network_key_from_pin(pin)
    packet = crypto.make_packet(key, crypto.random_seq(), cmd)

    gatt.send_packet(dest, 0x0011, packet)

def generate_light_set_cmd(level, red, green, blue, objid=0):
    #Object ID specifies the bulb or group of bulbs that this command is to be applied to. +ve values are interpreted as device IDs, -ve values will be interpreted as group IDs, and 0 is broadcast.
    cmd = b'\x73\x11'
    #for level only, -128 is full off and -1 is full on, RGB appears to be 0 to 255 so remap level to 0 to 255
    if(level < 0):
        level=0
    elif(level > 255):
        level=255
    level = (level//2)-128
    if(objid > 0):
        flags = 0x80
    else:
        flags = 0x00
        objid = abs(objid)
    p_cmd = struct.pack("<2x2sBBbBBB",cmd,objid,flags,level,red,green,blue)
    return p_cmd
