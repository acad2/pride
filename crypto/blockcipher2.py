from utilities import xor_sum, rotate_left, rotate_right, slide, xor_subroutine
    
def diffusion_transformation(data, diffuser):    
    for index in range(len(data)):
        byte = data[index]
        diffuser ^= byte        
        data[index] = rotate_left((byte + diffuser + index) % 256, 5)
        diffuser ^= data[index]            
    return diffuser
    
def bit_transposition(state):
    output = bytearray(16)
    for index in range(8):
        output[index] = 0
        for index2 in range(8):            
            byte = state[index2]
            output[index] |= ((byte & 1) << index2) & 255
            state[index2] = rotate_right(byte, 1)        
        
        output[index + 8] = rotate_left(state[index + 8], 1)
    
    state[:] = output[:]  

def byte_transposition(_state):   
    temp = bytearray(16)
    
    temp[7] = _state[0] 
    temp[12] = _state[1]
    temp[14] = _state[2]
    temp[9] = _state[3]
    temp[2] = _state[4]
    temp[1] = _state[5]
    temp[5] = _state[6]
    temp[15] = _state[7]
    temp[11] = _state[8]
    temp[6] = _state[9]
    temp[13] = _state[10]
    temp[0] = _state[11]
    temp[4] = _state[12]
    temp[8] = _state[13]
    temp[10] = _state[14]
    temp[3] = _state[15]
            
    _state[:] = temp[:]
             
def decorrelation_layer(data):
    bit_transposition(data)
    byte_transposition(data)
                
def invert_byte_transposition(state):
    temp = bytearray(16)
    
    temp[11] = state[0]
    temp[5] = state[1]
    temp[4] = state[2]
    temp[15] = state[3]
    temp[12] = state[4]
    temp[6] = state[5]
    temp[9] = state[6]
    temp[0] = state[7]
    temp[13] = state[8]
    temp[3] = state[9]
    temp[14] = state[10]
    temp[8] = state[11]
    temp[1] = state[12]
    temp[10] = state[13]
    temp[2] = state[14]
    temp[7] = state[15]
    
    state[:] = temp[:]
    
def xor_subroutine2(data, key):
    key_xor = 0
    data_xor = 0
    for index, byte in enumerate(key):
        data_xor ^= data[index]
        data[index] ^= byte
        key_xor ^= byte
    return key_xor, data_xor
    
def encrypt(data, key, rounds=1):
    key_xor, data_xor = xor_subroutine2(data, key)
    for round in range(rounds):
        key_xor = diffusion_transformation(key, key_xor)
        data_xor = diffusion_transformation(data, data_xor)
        decorrelation_layer(data)
        key_xor, data_xor = xor_subroutine2(data, key)
        
def invert_diffusion_transformation(data, diffuser):    
    for index in reversed(range(len(data))):
        byte = data[index]
        diffuser ^= byte        
        data[index] = (256 + (rotate_right(byte, 5) - diffuser - index)) % 256
        diffuser ^= data[index]
    return diffuser
    
def test_invert_diffusion_transformation():
    data = bytearray("Testing!")
    data_xor = diffusion_transformation(data, xor_sum(data))
    invert_diffusion_transformation(data, data_xor)
    assert data == "Testing!", data
    
def test_diffusion_cycle_length():
    from utilities import find_cycle_length_subroutine
    print len(find_cycle_length_subroutine(diffusion_transformation, bytearray("\x00\x01\x00"), 3))
    
def test_diffusion_metrics():
    from utilities import slide, xor_subroutine
    def test_hash(data):
        output = bytearray(16)
        for block in slide(bytearray(data), 16):            
            diffusion_transformation(block)
            xor_subroutine(output, block)
        return bytes(output)
        
    from metrics import test_hash_function
    test_hash_function(test_hash)
    
def test_bit_byte_transposition_diffusion():
    def test_hash(data):
        output = bytearray(16)
        for block in slide(bytearray(data), 16):
            block.extend("\x00" * (16 - len(block)))
            assert len(block) == 16
            for round in range(4):
                bit_transposition(block)
                byte_transposition(block)
                for index in range(16):
                    block[index] = (block[index] + block[(index + 2) % 16] + index) % 256
            xor_subroutine(output, block)        
        return bytes(output)
    from metrics import test_hash_function
    test_hash_function(test_hash)
    
if __name__ == "__main__":
    test_invert_diffusion_transformation()
    #test_diffusion_cycle_length()
    #test_diffusion_metrics()
    #test_bit_byte_transposition_diffusion()
    