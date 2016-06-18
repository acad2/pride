import pride.gui.gui
import pride.gui.grid

import pride.gui._interpretertest

class Visualized_Stack(pride.gui._interpretertest.Stack):
    
    
    




class Quadword(pride.gui.grid.Square):
    
    defaults = {"base_size" : 8, "square_colors" : ((55, 55, 65, 255), (55, 55, 65, 255)),
                "square_outline_colors" : ((125, 125, 125, 255), (125, 125, 125, 255)),
                "h_range" : (0, 320), "w_range" : (0, 320),
                "pack_mode" : "left"}
                
    def setup_grid(self):
        super(Quadword, self).setup_grid()
        for index in range(8):
            for index2 in range(8):
                self[index][index2].text = str((index * 8) + index2)
                
                
class PyObject(pride.gui.gui.Button): pass

class Integer(PyObject): pass

class Instruction_Viewer(pride.gui.gui.application):
    
    def __init__(self, **kwargs):
        super(Instruction_Viewer, self).__init__(**kwargs)
        self.stack = self.create("pride.gui.gui.Container")
        
    def 
                