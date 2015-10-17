import pride.gui.gui

class Cell(pride.gui.gui.Window_Object):
    
    defaults = pride.gui.gui.Window_Object.defaults.copy()
    defaults.update({"dead_color" : (0, 0, 0),
                     "alive_color" : (255, 255, 255),
                     "texture_size" : (4, 4)})
                     
    def _get_alive(self):
        return self._alive
    def _set_alive(self, value):
        if value:
            self.color = self.dead_color
        else:
            self.color = self.alive_color
        self._alive = value
    alive = property(_get_alive, _set_alive)
        
    def __init__(self, alive=False, born=(3, ), stays_alive=(2, 3),
                 minimum_neighbors=2, maximum_neighbors=3, **kwargs):
        super(Cell, self).__init__(**kwargs)
        self.born = born
        self.stays_alive = stays_alive
        self.minimum_neighbors = minimum_neighbors
        self.maximum_neighbors = maximum_neighbors
        self.alive = alive
        self.size = self.texture_size
        
            
class Game_Of_Life(pride.vmlibrary.Process):
             
    defaults = pride.vmlibrary.Process.defaults.copy()
    defaults.update({"cell_count_width" : 10,
                     "cell_count_height" : 10,
                     "priority" : 1})
                     
    def __init__(self, **kwargs):
        super(Game_Of_Life, self).__init__(**kwargs)
        
        grid = self.grid = []
        for width_index in xrange(self.cell_count_width):
            self.alert("Creating row {}/{}".format(width_index, 
                                                   self.cell_count_width))
            new_row = []
            grid.append(new_row)
            for height_index in xrange(self.cell_count_height):
                new_row.append(self.create(Cell, 
                                           poisition=(width_index, height_index)))
                
    def run(self):
        grid = self.grid
        grid_size = len(grid)
        row_size = len(grid[0])
        for grid_index, row in enumerate(grid):
            for cell_index, cell in enumerate(row):
                living_neighbors = 0
                for side in xrange(-1, 2):
                    for _side in xrange(-1, 2):
                        try:
                            if grid[grid_index + side][cell_index + _side].alive:
                                living_neighbors += 1
                        except IndexError:
    
                            if grid_index + side == grid_size:
                                side = -grid_size
                            if cell_index + _side == row_size:
                                _side = -row_size
         
                            if grid[grid_index + side][cell_index + _side].alive:
                                living_neighbors += 1
                                
                if cell.alive:
                    living_neighbors -= 1
                              
                if living_neighbors < cell.minimum_neighbors:
                    cell.alive = False
                elif living_neighbors > cell.maximum_neighbors:
                    cell.alive = False
                elif not cell.alive and living_neighbors in cell.born:
                    cell.alive = True
                    
                    