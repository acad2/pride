from utilities import xor_sum, rotate_left, xor_subroutine

def shuffle_bytes(_state, section, temp=list(range(16))):          
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
            
    _state[section] = temp[:]
           
def prp(data, key, mask=255, rotation_amount=5, bit_width=8, key_slice=slice(16, 32), data_slice=slice(0, 16)):     
    shuffle_bytes(data, key_slice)
    shuffle_bytes(data, data_slice)       
            
    for index in reversed(range(len(data))):       
        left, right = data[index], data[(index + 1) % 16]
        
        key ^= right
        right = rotate_left((right + key + index) & mask, rotation_amount, bit_width)
        key ^= right
        
        key ^= left
        left = (left + (right >> (bit_width / 2))) & mask
        left ^= rotate_left(right, rotation_amount)
        key ^= left

        data[index], data[(index + 1) % 16] = left, right                 

    key ^= data[0]
    data[0] = (data[0] + key) & mask
    key ^= data[0]
    
    return key
        
def prf(data, key, mask=255, rotations=5, bit_width=8):      
    for index in range(len(data)):         
        new_byte = rotate_left((data[index] + key + index) & mask, rotations, bit_width)
        key ^= new_byte        
        data[index] = new_byte             
    
def stream_cipher(data, seed, key, size=(8, 255, 5)):     
    key = list(key)
    seed = list(seed)
    state = seed + key
    key_material = list()       
    
    bit_width, mask, rotation_amount = size    
        
    block_count, extra = divmod(len(data), 16) 
    prf_state_xor = 0
    state_xor = xor_sum(state)
    for block in range(block_count + 1 if extra else block_count):       
        state_xor = prp(state, state_xor, mask, rotation_amount, bit_width)
        prf_state_xor ^= state_xor
        key_material.extend(state[0:16])    
    
    prf(key_material, prf_state_xor, mask, rotation_amount, bit_width)        
    
    xor_subroutine(data, key_material)    
        
def test_prp():
    data = bytearray(16)
    prp(data, 0)
    print [byte for byte in data[:16]]
    
if __name__ == "__main__":
    test_prp()
    