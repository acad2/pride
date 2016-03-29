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
                piece.pack_mode = None                
                piece.current_square.remove(piece)  
                if self.current_piece:                    
                    captured_piece = pride.objects[self.current_piece]
                    assert captured_piece.team == piece.other_team                    
                    captured_piece.delete()
                    
                self.add(piece)            
                piece.pack_mode = "top"
                
                self.pack()                        
                
                chess_game._active_item = None
                piece._moved = True                   
                              
                      
class Chess_Piece(pride.gui.gui.Button):
      
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
        super(Chess_Piece, self).__init__(**kwargs)
        self.text = self.__class__.__name__
        
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
        
          
class Pawn(Chess_Piece):
    
    defaults = {"_move_direction" : +1}    
    flags = {"_moved" : False}        
            
    def get_potential_moves(self):        
        game_board = self.parent_application.game_board
        column, row = self.current_square.grid_position
        movement_direction = self._move_direction
        
        moves = []
        next_row = row + movement_direction        
        if not game_board[column][next_row].current_piece:
            moves.append((column, next_row, "movement"))            
            if not self._moved and not game_board[column][next_row].current_piece:
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
        
def determine_move_information(game_board, piece, next_row, column):
    try:
        square = game_board[next_row][column]
    except (KeyError, IndexError):
        return None
        
    if square.current_piece:
        other_piece = pride.objects[square.current_piece]
        if other_piece.team == piece.other_team:
            if isinstance(other_piece, King):
  #              piece.alert("Checks King at {}".format((next_row, column)), 
  #                          level=piece.verbosity["check"])
                return (next_row, column, "check")
            else:
  #              piece.alert("Captures {} at {}".format(other_piece.__class__.__name__, (next_row, column)),
  #                          level=piece.verbosity["capture"])
                return (next_row, column, "capture")        
    else:                
        return (next_row, column, "movement")
                
class Rook(Chess_Piece): 
    
    def get_potential_moves(self):
        return self._get_potential_moves(self)
    
    @staticmethod
    def _get_potential_moves(self):
        game_board = self.parent_application.game_board
        moves = []
        row, column = self.current_square.grid_position
        
        next_row = row + 1
        while next_row <= 7:
            move = determine_move_information(game_board, self, next_row, column)
            if move:
                moves.append(move)
            else:
                break                
            if move[-1] == "capture":
                break
            next_row += 1

        next_row = row - 1
        while next_row >= 0:
            move = determine_move_information(game_board, self, next_row, column)
            if move:
                moves.append(move)
            else:
                break                
            if move[-1] == "capture":
                break
            next_row -= 1
            
        next_column = column + 1
        while next_column <= 7:
            move = determine_move_information(game_board, self, row, next_column)            
            if move:
                moves.append(move)
            else:
                break                
            if move[-1] == "capture":
                break            
            next_column += 1
            
        next_column = column - 1
        while next_column >= 0:
            move = determine_move_information(game_board, self, row, next_column)
            if move:                
                moves.append(move)
            else:
                break                
            if move[-1] == "capture":
                break
            next_column -= 1        
        return moves
        

class Knight(Chess_Piece):
        
    defaults = {"text" : "Knight"}
    
    def get_potential_moves(self):
        game_board = self.parent_application.game_board
        row, column = self.current_square.grid_position
        moves = []
        
        for row_movement, column_movement in ((2, -1), (2, 1), (1, -2), (1, 2),
                                              (-2, -1), (-2, 1), (-1, -2), (-1, 2)):
            move = determine_move_information(game_board, self, row + row_movement, column + column_movement)
            if move:
                moves.append(move)
        return moves
        
        
class Bishop(Chess_Piece):
        
    defaults = {"text" : "Bishop"}
    
    def get_potential_moves(self):
        return self._get_potential_moves(self)
        
    @staticmethod
    def _get_potential_moves(self):
        game_board = self.parent_application.game_board
        row, column = self.current_square.grid_position
        moves = []
        
        for movement in range(1, 8):
            next_row, next_column = (row + movement, column + movement)
            if next_row <= 7 and next_column <= 7:
                move = determine_move_information(game_board, self, next_row, next_column)            
                if not move:
                    break
                moves.append(move)
                if move[-1] == "capture":
                    break
            else:
                break
                
        for movement in range(1, 8):
            next_row, next_column = (row - movement, column - movement)
            if next_row >= 0 and next_column >= 0:
                move = determine_move_information(game_board, self, next_row, next_column)
                if not move:
                    break
                moves.append(move)
                if move[-1] == "capture":
                    break
            else:
                break
                
        for movement in range(1, 8):
            next_row, next_column = (row - movement, column + movement)
            if next_row >= 0 and next_column <= 7:
                move = determine_move_information(game_board, self, row - movement, column + movement)
                if not move:
                    break
                moves.append(move)
                if move[-1] == "capture":
                    break
            else:
                break
                
        for movement in range(1, 8):
            next_row, next_column = (row + movement, column - movement)
            if next_row <= 7 and next_column >= 0:
                move = determine_move_information(game_board, self, row + movement, column - movement)
                if not move:
                    break
                moves.append(move)    
                if move[-1] == "capture":
                    break            
            else:
                break
        return moves
        
        
class Queen(Chess_Piece):
        
    defaults = {"text" : "Queen"}
    
    diagonal_moves = Bishop.get_potential_moves
    straight_moves = Rook.get_potential_moves
    
    def get_potential_moves(self):
        return Bishop._get_potential_moves(self) + Rook._get_potential_moves(self)
        
    
class King(Chess_Piece):
        
    defaults = {"text" : "King"}
    
    def get_potential_moves(self):
        game_board = self.parent_application.game_board
        row, column = self.current_square.grid_position
        moves = []
        
        for row_movement in range(-1, 2):
            for column_movement in range(-1, 2):
                move = determine_move_information(game_board, self, row + row_movement, column + column_movement)
                if move:
                    moves.append(move)
        return moves
        
        
class Chess(pride.gui.gui.Application):
    
    defaults = {"square_outline_color" : (0, 0, 0, 255), "movable_square_outline_color" : (155, 155, 255, 255),
                "capture_outline_color" : (255, 175, 175, 255),
                "white_color" : (255, 255, 255, 255), "black_color" : (75, 75, 125, 255),
                "white_text_color" : (55, 55, 85, 255), "black_text_color" : (230, 230, 230, 255),
                "white_background_color" : (205, 205, 205, 155), "black_background_color" : (25, 25, 25, 155),
                "white_square_color" : (205, 205, 205, 255), "black_square_color" : (55, 55, 55, 255),
                "white_square_outline_color" : (0, 0, 0, 255), "black_square_outline_color" : (0, 0, 0, 255)}
    
    flags = {"_active_item" : None}
    
    def _get_game_board(self):
        return self.application_window.objects["Grid"][0]
    game_board = property(_get_game_board)
    
    def __init__(self, **kwargs):
        super(Chess, self).__init__(**kwargs)
        self.application_window.create("pride.gui.grid.Grid", rows=8, columns=8, 
                                       column_button_type=Gameboard_Square,
                                       square_colors=(self.white_square_color, self.black_square_color),
                                       square_outline_colors=(self.white_square_outline_color, self.black_square_outline_color))
        self.setup_game()
        
    def setup_game(self):
        game_board = self.game_board  
        white, black = self.white_color, self.black_color
        white_text, black_text = self.white_text_color, self.black_text_color
        white_background, black_background = self.white_background_color, self.black_background_color
        
        for piece_index in range(8):            
            game_board[piece_index][1].create("pride.gui.chess.Pawn", color=white, text="pawn", text_color=white_text,
                                              _move_direction=+1, team="white", background_color=white_background)
            game_board[piece_index][-2].create("pride.gui.chess.Pawn", color=black, text="pawn", text_color=black_text,
                                               _move_direction=-1, team="black", background_color=black_background)
        
        back_pieces = ("Rook", "Knight", "Bishop", "King", "Queen", "Bishop", "Knight", "Rook")
        for piece_index, piece_name in enumerate(back_pieces):
            game_board[piece_index][0].create("pride.gui.chess." + piece_name, text_color=white_text,
                                              color=white, text=piece_name, team="white",
                                              background_color=white_background)
       
        for piece_index, piece_name in enumerate(reversed(back_pieces)):
            game_board[piece_index][-1].create("pride.gui.chess." + piece_name, text_color=black_text,
                                               color=black, text=piece_name, team="black",
                                               background_color=black_background)
            
        
