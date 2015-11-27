import sys
import random

import pride.vmlibrary
import pride.utilities

#next_state = {(0, 1, 0) : 1, (0, 0, 0) : 0, (1, 0, 0) : 1,
#              (0, 0, 1) : 1, (1, 0, 1) : 0, (1, 1, 0) : 0,
#              (0, 1, 1) : 0, (1, 1, 1) : 1}

next_state = {(1, 1, 1) : 1, (1, 1, 0) : 0, (1, 0, 1) : 0, (1, 0, 0) : 1,
              (0, 1, 1) : 0, (0, 1, 0) : 1, (0, 0, 1) : 1, (0, 0, 0) : 0}
 
rule_30 = {(1, 1, 1) : 0, (1, 1, 0) : 0, (1, 0, 1) : 0, (1, 0, 0) : 1,
           (0, 1, 1) : 1, (0, 1, 0) : 1, (0, 0, 1) : 1, (0, 0, 0) : 0}
              
class CA_Test(pride.vmlibrary.Process):
                
    defaults = {"storage_size" : 1024}
    
    def __init__(self, **kwargs):
        super(CA_Test, self).__init__(**kwargs)
        self.bytearray = bytearray(1024)
        self.bytearray[sum(ord(random._urandom(1)) for x in xrange(4))] = 1
        
    def run(self):
        _bytearray = self.bytearray
        size = self.storage_size
        new_bytearray = bytearray(size)
        for index, byte in enumerate(_bytearray):
            current_state = (_bytearray[index - 1], byte, _bytearray[(index + 1) % size])
            new_bytearray[index] = next_state[current_state]
        self.bytearray = new_bytearray
        pride.utilities.shell("cls", True)
        sys.stdout.write(new_bytearray)
            