# Simple gatttool wrapper
import os
from binascii import hexlify

def gatt_write(dest, handle, data):
	strdata = hexlify(data).decode('ascii')
	p_handle = "0x" + hexlify(handle).decode('ascii')
	cmd = "gatttool -b %s --char-write-req -a %s -n %s" % (dest, p_handle, strdata)
	print("Running " + cmd)
	os.system(cmd)
