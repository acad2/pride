# NOTE: the crypto package is included for convenience of development and should not 
# be taken to imply that the modules located in pride.crypto are suitable for
# use to protect data in the real world.

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
    
    def _get_key(self):
        return self._key
    def _set_key(self, value):
        self._key = bytearray(value)
    key = property(_get_key, _set_key)
    
    def __init__(self, key, mode):
        self.key = key
        self.mode = mode
        
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

    def encrypt(self, data, iv):   
        data = bytearray(data)
        encrypt(data, self.key, bytearray(iv), self.encrypt_block, self.mode)
        return bytes(data)
        
    def decrypt(self, data, iv):        
        data = bytearray(data)
        mode = self.mode
        decrypt(data, self.key, bytearray(iv), self.decrypt_block if mode == "cbc" else self.encrypt_block, mode)    
        return bytes(data)
        
def test_encrypt_decrypt():
    data = "TestData" * 4
    _data = data[:]
    key = bytearray("\x00" * 16)
    iv = "\x00" * 16
    from ciphertest import Test_Cipher
    
    for mode in ("ctr", "ofb", "cbc"):
        cipher = Test_Cipher(key, mode)
        ciphertext = cipher.encrypt(data, iv)
        print ciphertext
        plaintext = cipher.decrypt(ciphertext, iv)
        print plaintext
        assert plaintext == data, (plaintext, data)
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    