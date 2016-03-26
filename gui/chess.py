import pride.gui.gui

class Gameboard_Square(pride.gui.gui.Button):
    
    pass
    
    
class Pawn(pride.gui.gui.Button):

    pass
    
    
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
    
    def _get_game_board(self):
        return self.application_window.objects["Grid"][0]
    game_board = property(_get_game_board)
    
    def __init__(self, **kwargs):
        super(Chess, self).__init__(**kwargs)
        self.application_window.create("pride.gui.grid.Grid", rows=8, columns=8, row_button_type=Gameboard_Square)
        self.setup_game()
        
    def setup_game(self):
        game_board = self.game_board  
        white, black = (255, 255, 255, 255), (0, 0, 0, 255)
        for piece_count in range(8):            
            game_board[1][piece_count].create("pride.gui.chess.Pawn", color=white, text="pawn")
            game_board[-2][piece_count].create("pride.gui.chess.Pawn", color=black, text="pawn")
        
        back_pieces = ("Rook", "Knight", "Bishop", "King", "Queen", "Bishop", "Knight", "Rook")
        for piece_index, piece_name in enumerate(back_pieces):
            game_board[0][piece_index].create("pride.gui.chess." + piece_name, color=white, text=piece_name)
       
        for piece_index, piece_name in enumerate(reversed(back_pieces)):
            game_board[-1][piece_index].create("pride.gui.chess." + piece_name, color=black, text=piece_name)
            
        
