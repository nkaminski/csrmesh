# Simple gatttool wrapper
import os
from binascii import hexlify

def send_packet(dest, handle, p):
    #Send the packet, first 20 bytes to handle, if more than 20 bytes send the next bytes to handle+3
    gatt_write(dest, handle, p[0:20])

    if(len(p) > 20):
        gatt_write(dest, handle+3, p[20:])

    return True

def gatt_write(dest, handle, data):
    strdata = hexlify(data).decode('ascii')
    p_handle = "0x" + format(handle, '04x')
    cmd = "gatttool -b %s --char-write-req -a %s -n %s" % (dest, p_handle, strdata)
    print("Running: " + cmd)
    os.system(cmd)
