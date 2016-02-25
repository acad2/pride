from pride.crypto.ciphertest import S_BOX

def permute(data):    
    xor_sum = data[0] ^ data[1]
    for index, byte in enumerate(data):
        data[index] ^= S_BOX[xor_sum ^ byte ^(2 ** (index % 8))]
    data[0], data[1] = data[1], data[0]
    
def test():
    data = bytearray("\x00" * 2)
    outputs = []
    while True:
        permute(data)
        output = bytes(data)
        if output in outputs:
            break
        else:
            outputs.append(output)
    print len(outputs)
    
if __name__ == "__main__":
    test()