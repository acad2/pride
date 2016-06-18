# speed, strength, technique, endurance - how fast, how hard, how accurate, how long - physical
# wits, power, technique, charge - how fast, how hard, how accurate, how long - magical

# health

import pride.gui.boardgame

class Gameboard_Square(pride.gui.gui.Button):
    
    defaults = {"outline_width" : 2}
    flags = {"current_piece" : None}
        
    def left_click(self, mouse):
        chess_game = self.parent_application
        if chess_game._active_item:            
            piece = pride.objects[chess_game._active_item]
            available_moves = piece.get_potential_moves()
            if (self.grid_position + ("movement", ) in available_moves or
                self.grid_position + ("capture", ) in available_moves or
                self.grid_position + ("check", ) in available_moves):                 
                    
                piece.toggle_highlight_available_moves()  
                piece.color = getattr(chess_game, piece.team + "_color")                
                piece.pack_mode = None                
                piece.current_square.remove(piece)  
                if self.current_piece:                    
                    captured_piece = pride.objects[self.current_piece]
                    assert captured_piece.team == piece.other_team                    
                    captured_piece.delete()
                   # import objectfinder
                   # print objectfinder.find_locations(captured_piece)
                self.add(piece)            
                piece.pack_mode = "top"
                
                self.pack()                        
                
                chess_game._active_item = None
                chess_game._current_move = "black" if piece.team == "white" else "white"
                piece._moved = True 
                
                
class Turn_Based_Strategy(pride.gui.boardgame.Board_Game):
    
    def setup_game(self):
        game_board = self.game_board  
        white, black = self.white_color, self.black_color
        white_text, black_text = self.white_text_color, self.black_text_color
        white_background, black_background = self.white_background_color, self.black_background_color
        
       
class Gameboard_Square(pride.gui.boardgame.Gameboard_Square):
    
    defaults = {"outline_width" : 2}
    flags = {"current_piece" : None}
           
    def left_click(self, mouse):
        chess_game = self.parent_application
        if chess_game._active_item:            
            piece = pride.objects[chess_game._active_item]
            available_moves = piece.get_potential_moves()
            if (self.grid_position + ("movement", ) in available_moves or
                self.grid_position + ("capture", ) in available_moves or
                self.grid_position + ("check", ) in available_moves):                 
                    
                piece.toggle_highlight_available_moves()  
                piece.color = getattr(chess_game, piece.team + "_color")                
                piece.pack_mode = None                
                piece.current_square.remove(piece)  
                if self.current_piece:                                       
                    captured_piece = pride.objects[self.current_piece]
                    assert captured_piece.team == piece.other_team                    
                    captured_piece.delete()
                   # import objectfinder
                   # print objectfinder.find_locations(captured_piece)
                self.add(piece)            
                piece.pack_mode = "top"
                
                self.pack()                        
                
                chess_game._active_item = None
                chess_game._current_move = "black" if piece.team == "white" else "white"
                piece._moved = True 
                
    
def Game_Piece_Palette(pride.gui.gui.Window):
            
    mutable_defaults = {"unit_types" : list}
    
    def __init__(self, **kwargs):
        for classification_tier in self.unit_types:
            container = self.create("pride.gui.gui.Container", pack_mode="top")
            for unit_type in classification_tier:
                container.create(Placement_Button, unit_type=unit_type, pack_mode="left")
                                                       

