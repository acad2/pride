import itertools

import pride.gui.gui

class Grid(pride.gui.gui.Window):
    
    defaults = {"rows" : 2, "columns" : 2,
                "row_container_type" : "pride.gui.gui.Container",
                "column_button_type" : "pride.gui.gui.Button",
                "square_colors" : ((0, 0, 0), (255, 255, 255))}
    
    def _get_size(self):
        return self.rows, self.columns
    def _set_size(self, value):
        self.rows, self.columns = value
    size = property(_get_size, _set_size)
    
    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)
        background_colors = itertools.cycle(self.square_colors)
        background_color = next(background_colors)
        for row in range(self.rows):
            container = self.create(self.row_container_type)
            for column in range(self.columns):
                button = container.create(self.column_button_type, pack_mode="left",
                                          background_color=background_color)
                background_color = next(background_colors)
                
        self._container_type = type(container).__name__
        self._button_type = type(button).__name__
        
    def __getitem__(self, item):
        return self.objects[self._container_type][item].objects[self._button_type]
        