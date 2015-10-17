import random
import sys

import mpre
import mpre.vmlibrary
import mpre.utilities


class Ca_Test(mpre.vmlibrary.Process):
    defaults = mpre.vmlibrary.Process.defaults.copy()
    defaults.update({"priority" : .5,
                     "size" : 8,
                     "grid" : None})
    
    def __init__(self, **kwargs):
        self.recorded_grids = set()
        super(Ca_Test, self).__init__(**kwargs)       
        grid_range = range(self.size)
        self.grid = self.grid or [list((0 for cell in grid_range)) for cell in grid_range]
          
        midpoint, offset = divmod(self.size, 2)  
        midpoint -= 1 # zero based indexing
        if offset: # grid_size is odd, there is a single midpoint
            midpoint = (midpoint + offset) 
            self.grid[midpoint][midpoint] = 1
        else:
            for left_adjustment, right_adjustment in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                self.grid[midpoint + left_adjustment][midpoint + right_adjustment] = 1
                
    def run(self):
        mpre.utilities.shell("cls", True)    
        grid = self.grid
        
        grid_size = len(grid)
        row_size = len(grid[0])
        grid_range = range(grid_size)
        
        print '\n\n'.join(str(row) for row in grid)
        #raw_input("pause")
        new_grid = self.grid = [list((0 for cell in grid_range)) for row in grid_range]
                  
        state_character_dead = '0'
        state_character_alive = '1'
        
        side_range = range(-1, 2)
        for row_index, row in enumerate(grid):
            for cell_index, cell in enumerate(row):
                if cell:
                    state = 0
                else:
                    state = 0
                    for side in side_range:
                        for _side in side_range:
                            if not (side or _side):
                                continue
                            current_row = row_index + side
                            current_cell = cell_index + _side                            
                            try:                        
                                if grid[current_row][current_cell]:
                                    state = 1
                            except IndexError:
                                if grid[current_row % grid_size][current_cell % row_size]:
                                    state = 1
                            if state:
                                break
                        if state:
                            break
                new_grid[row_index][cell_index] = state


class Ca_Test2(mpre.vmlibrary.Process):
    defaults = mpre.vmlibrary.Process.defaults.copy()
    defaults.update({"priority" : .5,
                     "size" : 8,
                     "grid" : None,
                     "dead_symbol" : '0',
                     "alive_symbol" : '1'})
    
    def __init__(self, **kwargs):
        self.recorded_grids = set()
        super(Ca_Test2, self).__init__(**kwargs)       
        grid_range = range(self.size)
        self.grid = self.grid or [list((self.dead_symbol for cell in grid_range)) for 
                                  cell in grid_range]
        
        midpoint, offset = divmod(self.size, 2)  
        midpoint -= 1 # because of zero based indexing
        if offset: # grid_size is odd, there is a single midpoint
            midpoint = (midpoint + offset) 
            self.grid[midpoint][midpoint] = self.alive_symbol
        else:
            for left_adjustment, right_adjustment in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                self.grid[midpoint + left_adjustment][midpoint + right_adjustment] = self.alive_symbol
                
    def run(self):
        mpre.utilities.shell("cls", True)    
        grid = self.grid
        
        grid_size = len(grid)
        row_size = len(grid[0])
        grid_range = range(grid_size)
        
        print '\n\n'.join(str(row) for row in grid)
        if 'exit' in mpre.shell.get_user_input("type exit to quit ").lower():
            self.running = False
        dead, alive = self.dead_symbol, self.alive_symbol
        new_grid = self.grid = [list((dead for count in grid_range)) for row in grid_range]

        side_range = range(-1, 2)
        for row_index, row in enumerate(grid):
            for cell_index, cell in enumerate(row):
                if cell == alive:
                    state = dead
                else:
                    state = dead
                    # search around the neighbors for living cells
                    # [-1, -1][-1, 0][-1, 1]
                    # [ 0, -1][ 0, 0][ 0, 1]
                    # [ 1, -1][ 1, 0][ 1, 1]                    
                    for side in side_range:
                        for _side in side_range:
                            if not (side or _side):
                                continue # [0, 0] is the current cell
                            current_row = row_index + side
                            current_cell = cell_index + _side                            
                            try:                        
                                if grid[current_row][current_cell] == alive:
                                    state = alive
                                    break
                            except IndexError:
                                if (grid[current_row % grid_size]
                                        [current_cell % row_size]) == alive:
                                    state = alive
                                    break
                                    
                        if state == alive:
                            break
                new_grid[row_index][cell_index] = state


class Ca_Test3(mpre.vmlibrary.Process):
    defaults = mpre.vmlibrary.Process.defaults.copy()
    defaults.update({"priority" : .5,
                     "size" : 8,
                     "grid" : None})
    
    def __init__(self, **kwargs):
        self.recorded_grids = set()
        super(Ca_Test3, self).__init__(**kwargs)       
        grid_range = range(self.size)
        self.grid = self.grid or [list((0 for cell in grid_range)) for 
                                  cell in grid_range]
        
        midpoint, offset = divmod(self.size, 2)  
        midpoint -= 1 # because of zero based indexing
        if offset: # grid_size is odd, there is a single midpoint
            midpoint = (midpoint + offset) 
            self.grid[midpoint][midpoint] = 1
        else:
            for left_adjustment, right_adjustment in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                self.grid[midpoint + left_adjustment][midpoint + right_adjustment] = 1
                
    def run(self):
        mpre.utilities.shell("cls", True)    
        grid = self.grid
        
        grid_size = len(grid)
        row_size = len(grid[0])
        grid_range = range(grid_size)
        
        print '\n\n'.join(str(row) for row in grid)
        if 'exit' in mpre.shell.get_user_input("type exit to quit ").lower():
            self.running = False
        
        new_grid = self.grid = [list((dead for count in grid_range)) for row in grid_range]

        side_range = range(-1, 2)
        for row_index, row in enumerate(grid):
            for cell_index, cell in enumerate(row):
                if cell:
                    if cell > 0:
                        adjustment = -1
                    else:
                        adjustment = 1
                    state = cell + adjustment
                else:
                    state = dead
                # search around the neighbors for living cells
                # [-1, -1][-1, 0][-1, 1]
                # [ 0, -1][ 0, 0][ 0, 1]
                # [ 1, -1][ 1, 0][ 1, 1]                    
                for side in side_range:
                    for _side in side_range:
                        if not (side or _side):
                            continue # [0, 0] is the current cell
                        current_row = row_index + side
                        current_cell = cell_index + _side                            
                        try:                        
                            neighbor = grid[current_row][current_cell]
                        except IndexError:
                            neighbor = grid[current_row % grid_size][current_cell % row_size]
                              
                        if not neighbor:
                            
                    if state == alive:
                        break
                new_grid[row_index][cell_index] = state

                
if __name__ == "__main__":
    mpre.Instruction("Python", "create", Ca_Test2).execute()