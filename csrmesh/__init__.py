import hmac
import hashlib
import struct
import random
from . import gatt
from Crypto.Cipher import AES

def network_key(pin):
    #Derives the long term network key(128 bits) from the 4 digit setup PIN
    h = hashlib.sha256()
    pin = str(pin)
    pin2 = pin.encode('ascii') + b'\x00MCP'
    h.update(pin2)
    dig = bytearray(h.digest())
    dig.reverse()
    return bytes(dig)[:16]

def make_packet(key,seq,data):
    magic = b'\x80'
    eof = b'\xff'
    enc = AES.new(key, AES.MODE_ECB)
    #Compute "base" based on the sequence number and encrypt with net key
    base = struct.pack("<Ixc10x",seq,magic)
    ebase = enc.encrypt(base)[:10]
    #XOR the encrypted base with the data
    payload = bytes([ a ^ b for (a,b) in zip(data, ebase) ])
    #Now pad, combine with header and compute HMAC
    prehmac = struct.pack("<8xIc10s",seq,magic,payload)
    hm = bytearray(hmac.new(key, msg=prehmac, digestmod=hashlib.sha256).digest())
    #Reverse the order of the bytes and truncate
    hm.reverse()
    hm = bytes(hm)[:8]
    final = struct.pack("<Ic10s8sc",seq,magic,payload,hm,eof)
    return final

def light_set_cmd(level, red, green, blue):
    cmd = b'\x73\x11'
    #for level only, -128 is full off and -1 is full on, RGB appears to be 0 to 255 so remap level to 0 to 255
    if(level < 0):
        level=0
    elif(level > 255):
        level=255
    level = (level//2)-128
    p_cmd = struct.pack("<2x2s2xbBBB",cmd,level,red,green,blue)
    return p_cmd

def random_seq():
    #Sequence number must just be different, not necessarily sequential
    return random.randint(1,16777215)

def send_packet(dest,p):
    #Send the packet, first 20 bytes to handle 0x0011 and remainder to 0x0014
    gatt.gatt_write(dest,b'\x00\x11',p[0:20])
    gatt.gatt_write(dest,b'\x00\x14',p[20:24])
    return True
