import pride.gui.gui

class Gameboard_Square(pride.gui.gui.Button):
    
    flags = {"current_piece" : None}
    
    def add(self, piece):        
        self_reference = self.reference
        piece.current_square = self_reference
        self.current_piece = piece.reference
        
        piece.parent_name = self_reference        
        super(Gameboard_Square, self).add(piece)
    
    def left_click(self, mouse):
        chess_game = self.parent_application
        if chess_game._active_item:                        
            piece = pride.objects[chess_game._active_item]
            piece._moved = True                       
            piece.toggle_highlight_available_moves()                        
            piece.pack_mode = None
            
            piece.current_square.remove(piece)            
            self.add(piece)            
            piece.pack_mode = "top"
            self.pack()                        
            
            chess_game._active_item = None
        
class Pawn(pride.gui.gui.Button):
    
    defaults = {"_move_direction" : +1}
    flags = {"_moved" : False, "_highlight_on" : False}
     
    def _get_current_square(self):
        return pride.objects[self._current_square]
    def _set_current_square(self, reference):
        self._current_square = reference
    current_square = property(_get_current_square, _set_current_square)
    
    def left_click(self, mouse):
        chess_game = self.parent_application
        current_position = row, column = self.parent.grid_position
        game_board = self.parent_application.game_board
                
        if not chess_game._active_item:
            # this piece has been selected
            chess_game._active_item = self.reference
            self.toggle_highlight_available_moves()
                            
        elif self.reference == chess_game._active_item:
            # this piece has been deselected
            chess_game._active_item = None
            self.toggle_highlight_available_moves()
        else:
            # this piece has been captured
            raise NotImplementedError()

    def toggle_highlight_available_moves(self):
        chess_game = self.parent_application
        
        if not self._highlight_on:                   
            movement_color = chess_game.movable_square_outline_color
            capture_color = chess_game.capture_square_outline_color
            self._highlight_on = True            
        else:
            capture_color = movement_color = chess_game.square_outline_color            
            self._highlight_on = False
        
        game_board = chess_game.game_board
        for row, column, move_type in self.get_potential_moves():
            if move_type == "movement":
                color = movement_color                
            else:
                color = capture_color
            game_board[row][column].color = color
            
    def get_potential_moves(self):        
        game_board = self.parent_application.game_board
        column, row = self.current_square.grid_position
        movement_direction = self._move_direction
        
        moves = []
        next_row = row + movement_direction        
        if not game_board[column][next_row].current_piece:
            moves.append((column, next_row, "movement"))
            if not self._moved:
                moves.append((column, row + (movement_direction * 2), "movement"))            
        
        if column:
            left_column = column - 1
            left_square = game_board[left_column][next_row]
            if left_square.current_piece:
                moves.append((left_column, next_row, "capture"))
        if column < 7:
            right_column = column + 1
            right_square = game_board[right_column][next_row]
            if right_square.current_piece:
                moves.append((right_column, next_row, "capture"))
                              
        return moves
        
        
class Rook(pride.gui.gui.Button): pass


class Knight(pride.gui.gui.Button):
        
    defaults = {"text" : "Knight"}
    

class Bishop(pride.gui.gui.Button):
        
    defaults = {"text" : "Bishop"}
    
    
class Queen(pride.gui.gui.Button):
        
    defaults = {"text" : "Queen"}
    
    
class King(pride.gui.gui.Button):
        
    defaults = {"text" : "King"}
    
    
class Chess(pride.gui.gui.Application):
    
    defaults = {"square_outline_color" : (0, 0, 0, 255), "movable_square_outline_color" : (200, 200, 255, 255),
                "capture_square_outline_color" : (235, 200, 175, 255),
                "white_color" : (255, 255, 255, 255), "black_color" : (15, 25, 45, 255),
                "white_square_color" : (225, 225, 225, 255), "black_square_color" : (25, 25, 25, 255)}
    
    flags = {"_active_item" : None}
    
    def _get_game_board(self):
        return self.application_window.objects["Grid"][0]
    game_board = property(_get_game_board)
    
    def __init__(self, **kwargs):
        super(Chess, self).__init__(**kwargs)
        self.application_window.create("pride.gui.grid.Grid", rows=8, columns=8, 
                                       column_button_type=Gameboard_Square,
                                       square_colors=(self.white_square_color, self.black_square_color))
        self.setup_game()
        
    def setup_game(self):
        game_board = self.game_board  
        white, black = self.white_color, self.black_color
        
        for piece_index in range(8):            
            game_board[piece_index][1].create("pride.gui.chess.Pawn", color=white, text="pawn", _move_direction=+1)
            game_board[piece_index][-2].create("pride.gui.chess.Pawn", color=black, text="pawn", _move_direction=-1)
        
        back_pieces = ("Rook", "Knight", "Bishop", "King", "Queen", "Bishop", "Knight", "Rook")
        for piece_index, piece_name in enumerate(back_pieces):
            game_board[piece_index][0].create("pride.gui.chess." + piece_name, color=white, text=piece_name)
       
        for piece_index, piece_name in enumerate(reversed(back_pieces)):
            game_board[piece_index][-1].create("pride.gui.chess." + piece_name, color=black, text=piece_name)
            
        
