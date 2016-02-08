import binascii

def to_bytes(input_string):        
    return binascii.unhexlify(input_string)
    
def xor(input1, input2):
    output = bytearray(input1)
    for index, byte in enumerate(bytearray(input2)):
        output[index] ^= byte
    return bytes(output)
    
def challenge_3():
    data = to_bytes("1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736")    
    a_k = data[0]
    b_k = data[1]
    ab = xor(a_k, b_k)
    
    print _byte, xor(data, len(data) * _byte)
    #for x in xrange(256):
    #    _byte = chr(x)
    #
    #    print x, xor(data, len(data) * _byte)
    
if __name__ == "__main__":
    challenge_3()