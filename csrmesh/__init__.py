import hmac
import hashlib
import struct
import random
from binascii import hexlify
from . import gatt
from Crypto.Cipher import AES

def network_key(binary):
    h = hashlib.sha256()
    h.update(binary)
    dig = bytearray(h.digest())
    dig.reverse()
    return bytes(dig)[:16]

def network_key_feit(pin):
    #Derives the long term network key(128 bits) from the 4 digit setup PIN
    strpin = str(pin).zfill(4)
    pin2 = strpin.encode('ascii') + b'\x00MCP'
    return network_key(pin2)

def make_packet(key,seq,data):
    magic = b'\x80'
    eof = b'\xff'
    dlen = len(data)
    enc = AES.new(key, AES.MODE_ECB)
    #Compute "base" based on the sequence number and encrypt with net key
    base = struct.pack("<Ixc10x",seq,magic)
    ebase = enc.encrypt(base)[:dlen]
    #XOR the encrypted base with the data
    payload = bytearray([ chr(a ^ ord(b)) for (a,b) in zip(data, ebase) ])
    #Now pad, combine with header and compute HMAC
    prehmac = struct.pack("<8xIc"+str(dlen)+"s",seq,magic,str(payload))
    hm = bytearray(hmac.new(key, msg=prehmac, digestmod=hashlib.sha256).digest())
    #Reverse the order of the bytes and truncate
    hm.reverse()
    hm = bytes(hm)[:8]
    final = struct.pack("<Ic"+str(dlen)+"s8sc",seq,magic,str(payload),hm,eof)
    return final

def decrypt_packet(key, data):
    if(len(data)<14):
        return None
    od = {}
    dlen = len(data)-14
    (seq, magic, epayload, hmac_packet, eof) = struct.unpack("<Ic"+str(dlen)+"s8sc", data)
    #Pad, combine with header and compute HMAC
    prehmac = struct.pack("<8xIc"+str(len(epayload))+"s",seq,magic,epayload)
    hm = bytearray(hmac.new(key, msg=prehmac, digestmod=hashlib.sha256).digest())
    #Reverse the order of the bytes and truncate
    hm.reverse()
    hmac_computed = bytes(hm)[:8]
    #Begin decryption
    enc = AES.new(key, AES.MODE_ECB)
    #Compute "base" based on the sequence number and encrypt with net key
    base = struct.pack("<Ixc10x",seq,magic)
    ebase = enc.encrypt(base)[:dlen]
    #XOR the encrypted base with the data
    decpayload = str(bytearray([ chr(ord(a) ^ ord(b)) for (a,b) in zip(epayload, ebase) ]))
    od['seq']=seq
    od['magic']=magic
    od['encpayload']=epayload
    od['decpayload']=decpayload
    od['hmac_computed']=hmac_computed
    od['hmac_packet']=hmac_packet
    od['eof']=eof
    return od

def network_key_bruteforce(data):
    #Cracks the 4 digit pin given the contents of a packet in a few seconds.
    for x in range(0,10000):
        pinstr="{:04X}".format(x)
        ki = network_key(pinstr)
        trial = decrypt_packet(ki, data)
        if(trial['hmac_computed'] == trial['hmac_packet']):
            return (pinstr, trial)
    return None

def print_decrypted_packet(decpkt):
    for k in decpkt.keys():
        if(type(decpkt[k]) is bytes):
            print(k+": "+hexlify(decpkt[k]).decode('ascii'))
        else:
            print(k+": "+str(decpkt[k]))

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
