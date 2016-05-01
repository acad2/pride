import struct

def MurmurOAAT(data):
  h = int(0)

  # Hash the Content
  for i in range(len(data)):
    h ^= ord(data[i])
    h  = (h * 0x5bd1e995) & 0xffffffff
    h ^= h >> 15

  return struct.pack('I', h)
  
from metrics import test_hash_function

test_hash_function(MurmurOAAT)