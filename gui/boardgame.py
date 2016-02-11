import pride.gui.gui
import pride.gui.widgetlibrary

class Board_Game(pride.gui.gui.Application):
    
    defaults = {"size" : (16, 16), "grid_type" : "pride.gui.grid.Grid",
                "row_container_type" : "pride.gui.gui.Container",
                "column_button_type" : "pride.gui.gui.Button"}
    
    def __init__(self, **kwargs):
        super(Board_Game, self).__init__(**kwargs)
        self.create("pride.gui.grid.Grid", rows=self.size[0], columns=self.size[1],
                    row_container_type=self.row_container_type,
                    column_button_type=self.column_button_type)
        
        
#class Game_Piece(pride.gui.gui.Button):    

#    def draw_texture(self):
        
        
class Checkers(Board_Game):
     
    defaults = {"size" : (8, 8)}
    
    def __init__(self, **kwargs):
        super(Checkers, self).__init__(**kwargs)
        