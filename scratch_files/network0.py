import uuid
import binascii
import struct
import ctypes

    
#
# Ethernet Frame:
# [
#   [ Destination address, 6 bytes ]
#   [ Source address, 6 bytes      ]
#   [ Ethertype, 2 bytes           ]
#   [ Payload, 40 to 1500 bytes    ]
#   [ 32 bit CRC chcksum, 4 bytes  ]
# ]
#

def get_mac_address():
    mac = uuid.getnode()
    if (mac >> 40) % 2:
        mac = None
    return hex(mac)
    
def ethernet_frame(destination_address, source_address, ethertype, 
                   payload):
    frame = struct.pack("!6s6s2s{}s".format(len(payload)), 
                        destination_address, source_address, ethertype,
                        payload)
    return frame + struct.pack('!i', binascii.crc32(frame))
    
def decode_ethernet_frame(frame):
    crc = struct.unpack('!i', frame[-4:])
    (destination_address, 
     source_address, 
     ethertype, 
     payload) = struct.unpack("!6s6s2s{}s".format(len(frame[14:-4])), frame)
    return {"destination_address" : destination_address,
            "source_address" : source_address,
            "ethertype" : ethertype,
            "payload" : payload,
            "crc" : crc}
            
def ip_header(version=0x04, internet_header_length=0x14, 
              differentiated_services_code_point=)