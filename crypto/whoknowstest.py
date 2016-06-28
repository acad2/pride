import os

class Ciphertext_Integer(int):
    
    def __init__(self, value, key, ciphertext=None, ciphertext_size=16):        
        if ciphertext is None:
            ciphertext = os.urandom(ciphertext_size)
        key[ciphertext] = int(value)        
        self.value = ciphertext
        
    #def __add__(self, other_operand):
        
        
        
def increment_ciphertext(ciphertext, integer2, key, new_ciphertext=None):    
    if new_ciphertext is None:
        new_ciphertext = os.urandom(16)
    integer1 = key[ciphertext]            
    key[new_ciphertext] = integer1 + integer2
    del key[ciphertext]
    return new_ciphertext
    
def modify_ciphertext(ciphertext, value, key, new_ciphertext=None, mode="__add__"):
    if new_ciphertext is None:
        new_ciphertext = os.urandom(16)
    old_value = key[ciphertext]
    key[new_ciphertext] = getattr(old_value, mode)(value)
    del key[ciphertext]
    return new_ciphertext        
               
def test_increment_ciphertext():
    integer1 = 10
    integer2 = 7
    ciphertext1 = os.urandom(16)    
    key = {ciphertext1 : integer1}
    print key[ciphertext1], ciphertext1  
    ciphertext3 = increment_ciphertext(ciphertext1, integer2, key)        
    print integer2
    print key[ciphertext3], ciphertext3
    
def test_modify_ciphertext():
    test_string = "Testing!"
    additional_value = " can be exciting sometimes!"
    ciphertext = os.urandom(16)
    key = {ciphertext : test_string}
    new_ciphertext = modify_ciphertext(ciphertext, additional_value, key)
    print new_ciphertext
    print key[new_ciphertext]
                   
if __name__ == "__main__":
    #test_increment_ciphertext()
    test_modify_ciphertext()
    