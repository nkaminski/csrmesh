# Simple bluepy wrapper
import os
from bluepy import btle
from binascii import hexlify

def connect(mac_list, debug=False):
    #Try to connect to each device in mac_list in order, returning after the first successful connection, or returning None after all attempts fail.
    device=None
    for mac in mac_list:
        try:
            if debug:
                print("[+] Connecting to device %s" % mac)
            device = btle.Peripheral(mac, addrType=btle.ADDR_TYPE_PUBLIC)
            return device
        except btle.BTLEException as err:
            if debug:
                print("[-] A connection error has occured: %s" % str(err))
    return None

def send_packet(dest, handle, p, debug=False):
    #Send the packet, dest may either be one or more MAC addresses represented as a comma separated string, or a btle.Peripheral object connected to the target
    #First 20 bytes to handle, if more than 20 bytes send the next bytes to handle+3

    #Make a connection if we were given an address, otherwise reuse the handle we were given
    if isinstance(dest, btle.Peripheral):
        if debug:
            print("[+] Reusing connection handle")
        device=dest
    else:
        device=connect(dest.split(','), debug)
        if not device:
            if debug:
                print("[-] Connection to mesh failed")
            return False

    #Write to the device
    try:
        gatt_write(device, handle, p[0:20], debug)
        if len(p) > 20:
            gatt_write(device, handle+3, p[20:], debug)

    except btle.BTLEException as err:
        if debug:
            print("[-] A communication error has occured: %s" % str(err))
        return False

    finally:
        #Disconnect from the device, but only if we made the connection
        if not isinstance(dest, btle.Peripheral):
            disconnect(device, debug)
        if debug:
            print("[+] Communication complete")

    return True

def disconnect(dev, debug=False):
    if dev:
        dev.disconnect()
        if debug:
            print("[+] BTLE disconnected")

def gatt_write(dev, handle, data, debug):
    if debug:
        print("[+] Writing 0x%s to BTLE handle 0x%X" % (hexlify(data).decode('ascii'), handle))
    dev.writeCharacteristic(handle, data, withResponse=True)
