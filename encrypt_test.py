import getpass
import hashlib
import os
import utilities
from itertools import izip_longest
convert = utilities.convert
asciikey = ''.join(chr(x) for x in xrange(256))

PADS = set()
def grouper(n, iterable, padvalue=None):
    """grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"""
    return izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)
    
def convert(bytes, message_key, public_key):
    old_base_size = len(message_key)
    new_base_size = len(public_key)
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(message_key))
    decimal_value = 0    
    new_value = ''
    print "\nBeginning conversion of: ", len(bytes), bytes, [ord(byte) for byte in bytes]
    print "from key: ", len(message_key), [ord(char) for char in message_key]
    print "to key: ", len(public_key), [ord(char) for char in public_key]
    for power, value_representation in enumerate(reversed(bytes)):
     #   value = old_base_mapping[value_representation]*(old_base_size**power)
      #  if not_significant and not value:
            
        
        decimal_value += old_base_mapping[value_representation]*(old_base_size**power)
                            
    if decimal_value == 0:
        new_value = public_key[0]
    else:
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            print "Calculated the digit: ", digit, public_key[digit]
            new_value += public_key[digit]
        print "done calculating: ", digit, public_key[digit]
    result = ''.join(reversed(new_value))
    print "conversion result: ", len(result), result, [ord(char) for char in result]
    return result
    
def derive_public_key(key_size=192, random_selection_size=128):
    key = []
    while len(key) < key_size:
        key.extend(set(os.urandom(random_selection_size)).difference(key))
    return ''.join(key)[:key_size]
    
def derive_public_key512(key_size=512, random_selection_size=512):
    key = []
    while len(key) < key_size:
        bytes = os.urandom(random_selection_size)
        _key = set()
        for index in range(1, key_size-1, 2):
            _key.add(bytes[index - 1:index + 1])
        key.extend(_key)                
    return ''.join(key[:key_size])
   
def derive_password_key(public_key, password=None, hash_function=hashlib.sha512, key_size=256):
    password = password if password else getpass.getpass("Please provide the password: ")
    public_key_size = len(public_key)
    password_key = public_key
    while len(password_key) < key_size:
        password = hash_function(password).digest()
        for symbol in password:
            if symbol not in password_key and len(password_key) < key_size:
                password_key += symbol
    return password_key
    
def derive_message_key(message):
    _key = list(set(message))
    key = []
    while _key:
        random_number = os.urandom(1)
        try:
            key.append(_key.pop(ord(random_number)))
        except IndexError:
            pass
    assert ''.join(key) not in PADS
    PADS.add(''.join(key))
    return key
    
def encrypt(message, public_key=None):
    message_key = derive_message_key(message)
    password_key = derive_password_key(public_key)
    return convert(message, message_key, password_key), message_key
    
def decrypt(encrypted_message, public_key, message_key):
    password_key = derive_password_key(public_key)
    return convert(encrypted_message, password_key, message_key)
    
PUBLIC_KEY = derive_public_key()

def test_convert(): 
    e = convert(message, asciikey, PUBLIC_KEY)
    d = convert(e, PUBLIC_KEY, asciikey)
    print d
    print message
    assert d == message
     
def test_message_key():     
    message_key = derive_message_key(message)
    _message_key = derive_message_key(message)
    assert message_key != _message_key    
    
    e = convert(message, message_key, PUBLIC_KEY)
    d = convert(e, PUBLIC_KEY, message_key)
    print d
    print message
    print message_key
    assert d == message
    
def test_password_key():
    message_key = derive_message_key(message)    
    _key = derive_password_key(PUBLIC_KEY)
    _key2 = derive_password_key(PUBLIC_KEY)
    assert _key == _key2
    assert len(_key) == 256    
    assert len(set(_key)) == 256
    e2 = convert(message, message_key, _key)
    d2 = convert(e2, _key, message_key)
    print d2
    print message
    assert d2 == message
 
    
def test_encrypt():    
    encrypted, key = encrypt(message, PUBLIC_KEY)
    decrypted = decrypt(encrypted, PUBLIC_KEY, key)
    assert decrypted == message
            
if __name__ == "__main__":
    message = "test_data " 
    getpass.getpass = lambda prompt: "testpassword"

    while True:
     #   test_convert()
        test_message_key()
    #    test_password_key()
      #  test_encrypt()
