from utilities import slide, xor_subroutine, replacement_subroutine, cast
                
def cbc_encrypt(block, iv, key, cipher, output):        
    xor_subroutine(block, iv)
    cipher(block, key)          
    output.extend(block)
    replacement_subroutine(iv, block)    

def cbc_decrypt(block, iv, key, cipher, output):    
    next_iv = block[:]        
    cipher(block, key)
    xor_subroutine(block, iv)        
    output.extend(block)
    replacement_subroutine(iv, next_iv)    
    
def ofb_mode(block, iv, key, cipher, output):
    cipher(iv, key)        
    xor_subroutine(block, iv)
    output.extend(block)
    
def ctr_mode(block, iv, key, cipher, output):
    cipher(iv, key)
    xor_subroutine(block, iv)
    output.extend(block)
    replacement_subroutine(iv, bytearray(cast(cast(cast(bytes(iv), "binary"), "integer") + 1, "bytes")))
    
def crypt(data, key, iv, cipher, mode_of_operation):    
    output = bytearray()
    blocksize = len(key)    
    iv = bytearray(iv)
    for block in slide(data, blocksize):  
        mode_of_operation(block, iv, key, cipher, output)
    
    replacement_subroutine(data, output)    
    
ENCRYPTION_MODES = {"cbc" : cbc_encrypt, "ofb" : ofb_mode, "ctr" : ctr_mode}
DECRYPTION_MODES = {"cbc" : cbc_decrypt, "ofb" : ofb_mode, "ctr" : ctr_mode}
    
def encrypt(data, key, iv, cipher, mode_of_operation):
    crypt(data, key, iv, cipher, ENCRYPTION_MODES[mode_of_operation])
    
def decrypt(data, key, iv, cipher, mode_of_operation):
    crypt(data, key, iv, cipher, DECRYPTION_MODES[mode_of_operation])    

class Cipher(object):
                
    def encrypt_block(self, plaintext, key):
        raise NotImplementedError()
    
    def decrypt_block(self, ciphertext, key):
        raise NotImplementedError()
        
    def generate_round_key(self, key):
        raise NotImplementedError()
        
    def extract_round_key(self, key):
        raise NotImplementedError()
        
    def p_box(self, data):
        raise NotImplementedError()
        
    def substitution_round(self, data, key):
        raise NotImplementedError()

    def encrypt(self, data, key, iv, mode):        
        return encrypt(data, key, iv, self.encrypt_block, mode)
        
    def decrypt(self, data, key, iv, mode):
        cipher = self.decrypt_block if mode == "cbc" else self.encrypt_block
        return decrypt(data, key, iv, cipher, mode)    
        
def test_encrypt_decrypt():
    data = bytearray("TestData" * 4)
    _data = data[:]
    key = bytearray("\x00" * 16)
    iv = key[:]
    from ciphertest import encrypt_block, decrypt_block
    for mode in ("ctr", "ofb", "cbc"):
        encrypt(data, key, iv, encrypt_block, mode)
        print data
        decrypt(data, key, iv, encrypt_block, mode)
        print data
        assert _data == data, (_data, data)
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    