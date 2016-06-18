import pride.gui.gui
        
class Gameboard_Square(pride.gui.gui.Button):
    
    defaults = {"outline_width" : 2}
    flags = {"current_piece" : None}
    
    def add(self, piece):        
        self_reference = self.reference

        piece.current_square = self_reference
        self.current_piece = piece.reference
        
        if piece.parent is not self:            
            piece.parent_name = self_reference                
        super(Gameboard_Square, self).add(piece)
    
    def remove(self, piece):
        piece.current_square = None
        self.current_piece = None
        super(Gameboard_Square, self).remove(piece)
        
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
                              
                      
class Game_Piece(pride.gui.gui.Button):
      
    defaults = {"team" : '', "outline_width" : 2}
    flags = {"_highlight_on" : False, "_backup_color" : None}
    verbosity = {"check" : 0, "capture" : 'v'}
    
    def _get_current_square(self):
        return pride.objects[self._current_square]
    def _set_current_square(self, reference):
        self._current_square = reference
    current_square = property(_get_current_square, _set_current_square)
        
    def _get_other_team(self):
        return "black" if self.team == "white" else "white"
    other_team = property(_get_other_team)        
    
    def __init__(self, **kwargs):
        super(Game_Piece, self).__init__(**kwargs)
        self.text = self.__class__.__name__
        
    def left_click(self, mouse):
        chess_game = self.parent_application
            
        current_position = row, column = self.parent.grid_position
        game_board = self.parent_application.game_board
                
        if not chess_game._active_item and chess_game._current_move == self.team:
            # this piece has been selected
            self.color = chess_game.selected_piece_outline_color
            chess_game._active_item = self.reference
            self.toggle_highlight_available_moves()
                            
        elif self.reference == chess_game._active_item and chess_game._current_move == self.team:
            # this piece has been deselected
            self.color = getattr(chess_game, self.team + "_color")
            chess_game._active_item = None
            self.toggle_highlight_available_moves()
        else:
            # this piece may have been captured 
            self.current_square.left_click(mouse)             

    def toggle_highlight_available_moves(self):
        chess_game = self.parent_application
        capture_color = chess_game.capture_outline_color
        
        if not self._highlight_on:                   
            movement_color = chess_game.movable_square_outline_color            
            self._highlight_on = True            
        else:
            movement_color = chess_game.square_outline_color            
            self._highlight_on = False
        
        game_board = chess_game.game_board
        for row, column, move_type in self.get_potential_moves():
            if move_type == "movement":                
                game_board[row][column].color = movement_color                
            else:                
                piece = game_board[row][column].current_piece
                pride.objects[piece].toggle_outline_highlight(capture_color)                            

    def toggle_outline_highlight(self, color):
        if self._backup_color:            
            self.color = self._backup_color
            self._backup_color = None            
        else:
            backup_color = self.color
            self._backup_color = (backup_color.r, backup_color.g, backup_color.b, backup_color.a)
            self.color = color            
            
    def get_potential_moves(self):
        return []        
        
               
class Board_Game(pride.gui.gui.Application):
    
    defaults = {"square_outline_color" : (0, 0, 0, 255), "movable_square_outline_color" : (155, 155, 255, 255),
                "capture_outline_color" : (255, 75, 125, 255), "selected_piece_outline_color" : (255, 175, 125, 255),
                "white_color" : (255, 255, 255, 255), "black_color" : (75, 75, 125, 255),
                "white_text_color" : (55, 55, 85, 255), "black_text_color" : (230, 230, 230, 255),
                "white_background_color" : (205, 205, 205, 155), "black_background_color" : (25, 25, 25, 155),
                "white_square_color" : (205, 205, 205, 255), "black_square_color" : (55, 55, 55, 255),
                "white_square_outline_color" : (0, 0, 0, 255), "black_square_outline_color" : (0, 0, 0, 255),
                "row_count" : 8, "column_count" : 8}
    
    flags = {"_active_item" : None, "_current_move" : "white"}
    
    def _get_game_board(self):
        return self.application_window.objects["Grid"][0]
    game_board = property(_get_game_board)
    
    def __init__(self, **kwargs):
        super(Board_Game, self).__init__(**kwargs)
        self.application_window.create("pride.gui.grid.Grid", rows=self.row_count, columns=self.column_count, 
                                       column_button_type=Gameboard_Square, pack_mode="main",
                                       square_colors=(self.white_square_color, self.black_square_color),
                                       square_outline_colors=(self.white_square_outline_color, self.black_square_outline_color))
        self.setup_game()        
        
    def setup_game(self):
        raise NotImplementedError()
        