import hmac
import hashlib
import struct
from Crypto.Cipher import AES
from binascii import hexlify,unhexlify

def network_key(pin):
    #Derives the long term network key(128 bits) from the 4 digit setup PIN
    h = hashlib.sha256()
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

def light_set_cmd(power, red, green, blue):
    cmd = b'\x73\x11'
    p_cmd = struct.pack("<2x2s2xBBBB",cmd,power,red,green,blue)
    return p_cmd
    
print(hexlify(light_set_cmd(228,255,255,255)))
p = make_packet(network_key('1337'),4000008,light_set_cmd(0,0,0,0))
#p = make_packet(network_key('1337'),4000005,unhexlify('000073110000e4ffffff'))
#p = make_packet(network_key('1337'),4000006,unhexlify('00007311000000000000'))

print(hexlify(p))
print(hexlify(p[0:20]))
print(hexlify(p[20:24]))
