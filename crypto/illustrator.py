import pride.gui.gui
from utilities import cast

class Bit(pride.gui.gui.Button): 

    defaults = {"pack_mode" : "left"}
    

class Word(pride.gui.gui.Container):
    
    defaults = {"bits" : b'', "pack_mode" : "left"}
        
    def __init__(self, **kwargs):
        super(Word, self).__init__(**kwargs)
        for bit in self.bits:
            self.create(Bit, text=bit)
            

class P_Box(pride.gui.gui.Window):
    
    defaults = {"block_size" : 128, "word_size" : 8}
    
    def __init__(self, **kwargs):
        super(P_Box, self).__init__(**kwargs)        
        self.input_block = self.create("pride.gui.gui.Container", h_range=(0, 20))
        self.spacer = self.create("pride.gui.gui.Container", h_range=(0, 100))
        self.output_block = self.create("pride.gui.gui.Container", h_range=(0, 20))
        
    def permute(self, input_data, permutation):           
        input_block, output_block = self.input_block, self.output_block
        for child in input_block.children:
            child.delete()
        for child in output_block.children:
            child.delete()
        
        input_data, output_data = bytearray(input_data), bytearray(input_data)
        permutation(output_data)
        
        for index, byte in enumerate(input_data):
            input_block.create(Word, bits=format(input_data[index], 'b').zfill(8))
            output_block.create(Word, bits=format(output_data[index], 'b').zfill(8))
        
        output_words = output_block.objects["Word"]
        input_words = input_block.objects["Word"]
        
        for index in range(self.word_size):
            for word in input_words:
                output_words[index].add(word.objects["Bit"][index])
                              
        input_block.pack()
        output_block.pack()
        
    def draw_texture(self):
        super(P_Box, self).draw_texture()

            