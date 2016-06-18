import pride.gui.gui
import pride.gui.boardgame
Game_Piece = pride.gui.boardgame.Game_Piece

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
          
class Pawn(Game_Piece):
    
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
        
        
class Rook(Game_Piece): 
    
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
        

class Knight(Game_Piece):
        
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
        
        
class Bishop(Game_Piece):
        
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
        
        
class Queen(Game_Piece):
        
    defaults = {"text" : "Queen"}
    
    diagonal_moves = Bishop.get_potential_moves
    straight_moves = Rook.get_potential_moves
    
    def get_potential_moves(self):
        return Bishop._get_potential_moves(self) + Rook._get_potential_moves(self)
        
    
class King(Game_Piece):
        
    defaults = {"text" : "King"}
    
    def get_potential_moves(self):
        game_board = self.parent_application.game_board
        row, column = self.current_square.grid_position
        moves = []
        
        for row_movement in range(-1, 2):
            for column_movement in range(-1, 2):
                next_row, next_column = (row + row_movement, column + column_movement)
                if next_row >= 0 and next_row <= 7 and next_column >= 0 and next_column <= 7:
                    move = determine_move_information(game_board, self, row + row_movement, column + column_movement)
                    if move:
                        moves.append(move)
        return moves
                    
        
class Chess(pride.gui.boardgame.Board_Game):
    
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
