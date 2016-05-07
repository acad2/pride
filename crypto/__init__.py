# NOTE: the crypto package is included for convenience of development and should not 
# be taken to imply that the modules located in pride.crypto are suitable for
# use to protect data in the real world.

from utilities import slide, xor_subroutine, replacement_subroutine, cast
from metrics import test_block_cipher
from pride.errors import InvalidTag
                
def cbc_encrypt(block, iv, key, cipher, tag=None): 
    xor_subroutine(block, iv)        
    cipher(block, key, tag)        
    replacement_subroutine(iv, block)        
    
def cbc_decrypt(block, iv, key, cipher, tag=None):    
    next_iv = block[:]        
    cipher(block, key, tag)
    xor_subroutine(block, iv)        
    replacement_subroutine(iv, next_iv)    
    
def ofb_mode(block, iv, key, cipher, tag=None):
    cipher(iv, key, tag)        
    xor_subroutine(block, iv)
        
def ctr_mode(block, iv, key, cipher, tag=None):
    cipher(iv, key, tag)
    xor_subroutine(block, iv)    
    replacement_subroutine(iv, bytearray(cast(cast(cast(bytes(iv), "binary"), "integer") + 1, "bytes")))
    
def ella_mode(block, iv, key, cipher, tag):         
    datablock = tag + block
    cipher(datablock, key)
    replacement_subroutine(block, datablock[8:])
    replacement_subroutine(tag, datablock[:8])#tag[:8] = datablock[:8]        
    
def ecb_mode(block, iv, key, cipher, tag=None):
    cipher(block, key, tag)
    
def crypt(data, key, iv, cipher, mode_of_operation, blocksize, tag):    
    output = bytearray()    
    for block in slide(data, blocksize):      
        mode_of_operation(block, iv, key, cipher, tag)        
        output.extend(block)
    replacement_subroutine(data, output)                       
        
ENCRYPTION_MODES = {"cbc" : cbc_encrypt, "ofb" : ofb_mode, "ctr" : ctr_mode, "ella" : ella_mode, "ecb" : ecb_mode}
DECRYPTION_MODES = {"cbc" : cbc_decrypt, "ofb" : ofb_mode, "ctr" : ctr_mode, "ella" : ella_mode, "ecb" : ecb_mode}
    
def cbc_padding(datasize, blocksize):
    padding_amount = (blocksize - (datasize % blocksize))         
    if not padding_amount:
        padding_characters = chr(0) * blocksize
    elif padding_amount == blocksize:
        padding_characters = chr(0) * blocksize
    else:                        
        padding_characters = chr(padding_amount) * padding_amount
    return padding_characters
    
def encrypt(data, cipher, iv, tag=None):
    #data = bytearray(data)
    mode = cipher.mode    
    blocksize = cipher.blocksize
    datasize = len(data)
    if mode == "ella" and tag is None:
        raise ValueError("Tag not supplied")
    if mode == "cbc":
        data.extend(cbc_padding(datasize, blocksize))
        
    crypt(data, cipher.key, iv, cipher.encrypt_block, 
          ENCRYPTION_MODES[cipher.mode], blocksize, tag)                
    #if tag is not None:
    #    return tag + bytes(data)
    #else:
    return bytes(data)
    
def decrypt(data, cipher, iv, tag=None):#key, iv, cipher, mode_of_operation, tweak=None):    
    mode = cipher.mode    
    #if mode != "ella":
    #    assert not tag, (mode, data, cipher, iv, tag)
    if mode in ("cbc", "ella", "ecb"):
        crypt_block = cipher.decrypt_block
        if mode == "ella":                    
            data = ''.join(reversed([block for block in slide(bytes(data), cipher.blocksize)]))
    else:
        crypt_block = cipher.encrypt_block  
    
    #data = bytearray(data)        
    crypt(data, cipher.key, iv, crypt_block, DECRYPTION_MODES[mode], cipher.blocksize, tag)  
    if mode == "ella":
        if tag != cipher.mac_key:
            raise InvalidTag()
        return ''.join(reversed([block for block in slide(bytes(data), cipher.blocksize)]))
    elif mode == "cbc":
        padding_amount = data[-1]            
        return bytes(data)[:-(padding_amount or cipher.blocksize)]
    else:
        return bytes(data)
    
class Cipher(object):
    
    def _get_key(self):
        return self._key[:]
    def _set_key(self, value):
        self._key = bytearray(value)
    key = property(_get_key, _set_key)
    
    MODE_ECB = "ecb"
    MODE_CBC = "cbc"
    MODE_OFB = "ofb"
    MODE_CTR = "ctr"
    MODE_ELLA = "ella"
    
    def __init__(self, key, mode):
        self.key = key
        self.mode = mode
        self.blocksize = 0
        self.iv = None
        
    def encrypt_block(self, plaintext, key, tag=None):
        raise NotImplementedError()
    
    def decrypt_block(self, ciphertext, key, tag=None):
        raise NotImplementedError()

    def encrypt(self, data, iv=None, tag=None): 
        if self.iv:
            assert iv is None
            iv = self.iv           
        self.tag = tag
        data = bytearray(data)
        iv = bytearray(iv or '')
        return encrypt(data, self, iv, tag)
                
    def decrypt(self, data, iv=None, tag=None): 
        if self.iv:
            assert iv is None
            iv = self.iv    
        data = bytearray(data)        
        iv = bytearray(iv)
        return decrypt(data, self, iv, tag)    
                
    @classmethod
    def new(cls, key, mode, iv=None):
        cipher = cls(key, mode)
        cipher.iv = iv
        return cipher
    
    @classmethod
    def test_metrics(cls, *args, **kwargs):        
        mode = kwargs.pop("mode", "ctr")
        tag = bytearray(kwargs.pop("tag", "\x00" * 16))
        test_block_cipher(lambda data, key, iv: cls(key, mode).encrypt(data, iv, tag), *args, **kwargs)    
    
    @classmethod
    def test_encrypt_decrypt(cls, *args, **kwargs):
        cipher = cls(*args, **kwargs)
        message = "\x00" * 16
        iv = "\x00" * 16
        tag = [0 for byte in range(16)]
        ciphertext = cipher.encrypt(message, iv, tag)
        plaintext = cipher.decrypt(ciphertext, iv, tag)
        assert message == plaintext, (message, plaintext)
        
#class Test_Cipher(Cipher):
#    
#    def __init__(self, encrypt_block_method, *args):
#        super(Test_Cipher, self).__init__(*args)
#        self.blocksize = 16
#        self.encrypt_block = encrypt_block_method
#        
#    def encrypt_block(self, data, key):
#        pass  
        
def test_encrypt_decrypt():
    data = "TestData" * 4
    _data = data[:]
    key = bytearray("\x00" * 16)
    iv = "\x00" * 16
    from blockcipher import Test_Cipher
    #print data
    for mode in ("ctr", "ofb", "cbc", "ecb"):    
        print "Testing: ", mode
        cipher = Test_Cipher(key, mode)
        ciphertext = cipher.encrypt(data, iv)
        plaintext = cipher.decrypt(ciphertext, iv)    
        #print ciphertext                    
        assert plaintext == data, (mode, plaintext, data)
        
        ciphertext2 = encrypt(data, cipher, iv)             
        assert ciphertext2 == ciphertext
        plaintext2 = decrypt(ciphertext2, cipher, iv)   
        assert plaintext2 == plaintext, (mode, plaintext2, plaintext)
    
    print "Beginning mac test..."
    cipher = Test_Cipher(key, "ella")
    tag = cipher.mac_key[:]
    ciphertext = cipher.encrypt(data, iv, tag)
    try:
        plaintext = cipher.decrypt(ciphertext, iv, tag)
    except InvalidTag:        
        raise
        
    ciphertext = cipher.encrypt(data, iv, tag)[:-2]
    for x in xrange(256):
        for y in xrange(256):
            try:
                plaintext = cipher.decrypt(ciphertext + chr(x) + chr(y), iv, tag)
            except InvalidTag:
                continue
            else:        
                print x, y#assert plaintext == data, (plaintext, data)
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    