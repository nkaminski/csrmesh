# csrmesh
Reverse engineered bearer implementation of the CSRMesh BTLE protocol including all necessary cryptographic and packing routines required to send packages over a CSRMesh BTLE network. This particular implementation currently only supports the CSRMesh lighting API and has been suucssfully tested with Fiet HomeBrite smart LED bulbs. However, the implemtation of other CSRMesh APIs should be quite straightformard if needed.

# Requirements
 * Python 3.x
 * Recent version of bluez
 * pycrypto

# Usage
    csrmesh.py [-h] --pin (4 digit pin) --dest (destination BT address) 
    [--level LEVEL] [--red RED] [--green GREEN] [--blue BLUE]
All levels are represented using numbers from 0 (off) to 255 (maximum)

# Protocol Documentation
## Network Key Derivation
The 128 bit network key used in CSRMesh networks is derived by concatenating the ASCII representation of the PIN with a null byte and the string 'MCP', computing the SHA256 hash of the string, reversing the order of the bytes in the hash, and taking the first 16 bytes of the resulting character array as the key.

## Forming Authenticated Packets
Packets sent to CSRMesh devices require authentication as well as encryption. All multibyte types are represented in little endian format. To form a valid packet, the sequence number, the constant 0x0080, and N null bytes where N is equal to the size of the payload to be sent are concatenated together and encrypted using the network key using AES-128 in ECB mode. The result of such encryption is then truncated to the length of the payload to be sent. The payload is XOR'ed with the result of the previous encryption to form the encrypted payload. Next, the message authentication code is computed using HMAC-SHA256 using the network key as the secret of the following data concatenated together: 8 null bytes, sequence number, constant 0x80 and encrypted payload. The order of the bytes in the resulting hash are then reversed and the has truncated to 8 bytes. Finally, the packet is formed by contatenating the sequence number, constant 0x80, encrypted payload, truncated HMAC, and the constant 0xff.

## Sending packets
Packets are then sent via the Bluetooth LE GATT protocol. To send a packet, the data must be written to two write only handles, 0x0011 and 0x0014. The first 20 bytes of the packed are first written to handle 0x0011 and then the remainder of the packet is written to handle 0x0014.
