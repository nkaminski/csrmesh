#!/usr/bin/env python

from . import crypto
from binascii import hexlify, unhexlify

class CSRVirtualDevice(object):
    def __init__(self, pin):
        self.lhandle = 0x1c
        self.hhandle = 0x1f
        self.lregister = b'\x00'
        self.hregister = b'\x00'
        self.netkey = crypto.network_key_from_pin(pin)
        self.callback = self.print_callback
        self.payloads = []
        self.debug = True

    def _registerChanged(self):
        data = self.lregister + self.hregister
        return self.process_packet(data)

    def _debugprint(self, s):
        if self.debug:
            print(s)

    def print_callback(self, data):
        print("[+] CSRVirtualDevice received valid packet")
        for k,v in data.items():
            if isinstance(v, bytes):
                v = hexlify(v)
            print('{}: {}'.format(k,v))
        print("[+] End of packet")

    # Set the value of a virtual device register by BTLE handle 
    def set_handle(self, handle, data):
        if handle == self.lhandle:
            self.lregister = data
            return self._registerChanged()
        elif handle == self.hhandle:
            self.hregister = data
            return self._registerChanged()
        else:
            self._debugprint('[-] Handle 0x{:x} does not map to a vaild register'.format(handle))

    # Set the value of a virtual device register directly
    def set_l_register(self, data):
        self.lregister = data
        return self._registerChanged()

    def set_h_register(self, data):
        self.hregister = data
        return self._registerChanged()

    # Process the byte string of a CSRMesh packet directly
    def process_packet(self, data, allow_invalid=False):
        res = crypto.decrypt_packet(self.netkey, data)
        if res:
            if allow_invalid or (res['hmac_computed'] == res['hmac_packet']):
                self.payloads.append(res['decpayload'])
                return self.callback(res)
        return False

    # Return a list of all decrypted payloads processed
    def get_all_payloads(self):
        return self.payloads
 
def hex2int(h):
    #Strip 0x
    if h[1] == 'x':
        h = h[2:]
    bdata = unhexlify(h)
    return int.from_bytes(bdata, byteorder='big', signed=False)
