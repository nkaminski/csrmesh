import struct
from . import gatt
from . import crypto

def set_position(dest, pin, position, objid=0):
    cmd = generate_move_set_cmd(position, objid)

    key = crypto.network_key_from_pin(pin)
    packet = crypto.make_packet(key, crypto.random_seq(), cmd)

    gatt.send_packet(dest, 0x0021, packet)

def generate_move_set_cmd(position, objid=0):
    #Object ID specifies the bulb or group of bulbs that this command is to be applied to.
    # Assuming group vs device adressing works the same as with the bulbs
    if(objid > 0):
        flags = 0x80
    else:
        flags = 0x00
        objid = abs(objid)

    # Unknown, always seems to be 0x73 with original app (and that matches the value used by the lightbulb as well)
    magic = 0x73

    # Command to send, 0x22 is move to position, see: http://www.teptron.com/MOVE_UART_Commands_ver1.0.pdf
    cmd = 0x22

    p_cmd = struct.pack("<BBBBB",objid,flags,magic,cmd,position)
    return p_cmd
