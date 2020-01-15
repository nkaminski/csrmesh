import hmac
import hashlib
import struct
import random
from Cryptodome.Cipher import AES

def network_key_from_pin(pin):
    #Derives the long term network key(128 bits) from the 4 digit setup PIN
    strpin = str(pin).zfill(4)
    pin2 = strpin.encode('ascii') + b'\x00MCP'
    return generate_key(pin2)

def generate_key(binary):
    h = hashlib.sha256()
    h.update(binary)
    dig = bytearray(h.digest())
    dig.reverse()
    return bytes(dig)[:16]

def make_packet(key,seq,data):
    #Message source is always 0x0080 (32768) when sending
    #packets from a device without a network ID
    source = 32768
    eof = b'\xff'
    dlen = len(data)
    seq_arr = int.to_bytes(seq, 3, byteorder="little")
    #Compute 128 bit IV based on the sequence number/nonce
    #|   SEQ   |  0x00  | Source  | 0x00 x10 |
    #| 3 bytes | 1 byte | 2 bytes | 10 bytes |
    iv = struct.pack("<3sxH10x",seq_arr,source)
    #Initialize AES in OFB mode with the IV we just computed
    enc = AES.new(key, AES.MODE_OFB, iv)
    payload = bytearray(enc.encrypt(data))
    #Now pad, combine with header and compute HMAC
    #HMAC Input
    #| 0x00 x8 |   SEQ   | Source  | payload |
    #| 8 bytes | 3 bytes | 2 bytes |   var   |
    prehmac = struct.pack("<8x3sH"+str(dlen)+"s",seq_arr,source,bytes(payload))
    hm = bytearray(hmac.new(key, msg=prehmac, digestmod=hashlib.sha256).digest())
    #Reverse the order of the bytes and truncate
    hm.reverse()
    hm = bytes(hm)[:8]
    #CSR Message Format
    #|   SEQ   | Source  | payload |  HMAC   |  EOF   |
    #| 3 bytes | 2 bytes |   var   | 8 bytes | 1 byte |
    final = struct.pack("<3sH"+str(dlen)+"s8sc",seq_arr,source,bytes(payload),hm,eof)
    return final

def decrypt_packet(key, data):
    if(len(data)<14):
        return None
    od = {}
    dlen = len(data)-14
    (seq_arr, source, epayload, hmac_packet, eof) = struct.unpack("<3sH"+str(dlen)+"s8sc", data)
    #Pad, combine with header and compute HMAC
    prehmac = struct.pack("<8x3sH"+str(len(epayload))+"s",seq_arr,source,epayload)
    hm = bytearray(hmac.new(key, msg=prehmac, digestmod=hashlib.sha256).digest())
    #Reverse the order of the bytes and truncate
    hm.reverse()
    hmac_computed = bytes(hm)[:8]
    #Compute the IV and initialize AES context
    iv = struct.pack("<3sxH10x",seq_arr,source)
    enc = AES.new(key, AES.MODE_OFB, iv)
    #Decrypt the payload
    decpayload = enc.decrypt(bytes(epayload))
    seq = int.from_bytes(seq_arr, byteorder='little')
    od['seq']=seq
    od['source']=source
    od['encpayload']=epayload
    od['decpayload']=decpayload
    od['hmac_computed']=hmac_computed
    od['hmac_packet']=hmac_packet
    od['eof']=eof
    return od

def bruteforce_pin(data):
    #Cracks the 4 digit pin given the contents of a packet in a few seconds.
    for x in range(0,10000):
        ki = network_key_from_pin(x)
        trial = decrypt_packet(ki, data)
        if(trial['hmac_computed'] == trial['hmac_packet']):
            return x
    return None

def random_seq():
    #Sequence number must just be different, not necessarily sequential
    return random.randint(1,16777215)
