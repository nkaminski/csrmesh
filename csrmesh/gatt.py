# Simple bluepy wrapper
import os
from bluepy import btle
from binascii import hexlify

def send_packet(dest, handle, p):
    #Send the packet, first 20 bytes to handle, if more than 20 bytes send the next bytes to handle+3
    device=None
    try:
        print("[+] Connecting to device %s" % dest)
        device = btle.Peripheral(dest, addrType=btle.ADDR_TYPE_PUBLIC)
        gatt_write(device, handle, p[0:20])

        if(len(p) > 20):
            gatt_write(device, handle+3, p[20:])

    except btle.BTLEException as err:
        print("[-] A communication error has occured: %s" % str(err))
        return False

    finally:
        if device:
            print("[+] Communication complete")
            device.disconnect()

    return True

def gatt_write(dev, handle, data):
    print("[+] Writing 0x%s to BTLE handle 0x%X" % (hexlify(data).decode('ascii'), handle))
    dev.writeCharacteristic(handle, data, withResponse=True)
