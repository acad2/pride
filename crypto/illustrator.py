import pride.gui.gui
from utilities import cast

class Bit(pride.gui.gui.Button): 

    defaults = {"pack_mode" : "left"}
    

class Word(pride.gui.gui.Container):
    
    defaults = {"bits" : b'', "pack_mode" : "left"}
    required_attributes = ("bits", )
    
    def __init__(self, **kwargs):
        super(Word, self).__init__(**kwargs)
        for bit in self.bits:
            self.create(Bit, text=bit)
            

class P_Box(pride.gui.gui.Window):
    
    defaults = {"block_size" : 128, "word_size" : 8}
    
    def __init__(self, **kwargs):
        super(P_Box, self).__init__(**kwargs)        
        self.input_block = self.create("pride.gui.gui.Container")
        self.spacer = self.create("pride.gui.gui.Container")
        self.output_block = self.create("pride.gui.gui.Container")
        
    def permute(self, input_data, permutation):   
        output_data = bytearray(input_data)
        permutation(output_data)
        
        input_block, output_block = self.input_block, self.output_block
        for child in input_block.children:
            child.delete()
        for child in output_block.children:
            child.delete()
            
        for index, byte in enumerate(output_data):
            input_block.create(Word, bits=format(input_data[0], 'b').zfill(8))
            output_block.create(Word, bits=format(byte, 'b').zfill(8))                 
        
        
    def draw_texture(self):
        super(P_Box, self).draw_texture()
        
            