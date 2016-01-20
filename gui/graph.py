import pride.gui.gui

class Graph(pride.gui.gui.Window):
    
    defaults = {"background_color" : (255, 255, 255), "color" : (0, 0, 0),
                "x_axis_range" : (0, 100), "y_axis_range" : (0, 100)}
    mutable_defaults = {"points" : list}
    
    def __init__(self, **kwargs):
        super(Graph, self).__init__(**kwargs)
        self.x_spacing = self.w / self.x_axis_range[1]
        self.y_spacing = self.h / self.y_axis_range[1]        
        self.points = self.points or [0 for counter in range(self.x_axis_range[1])]
        
    def left_click(self, mouse):
    #    points = self.points
    #    x, y = mouse.x, mouse.y
    #    old_value = points[x]
    #    if old_value:
    #        new_value = (y + old_value) / 2
    #    else:
    #        new_value = y
    #        
    #    points[x] = new_value
    #    self.texture_invalid = True
        
        
        self.points[mouse.x] = (mouse.y + self.points[mouse.x]) / 2
        self.texture_invalid = True
        
    def draw_texture(self):
        self.draw("fill", self.area, self.background_color)
        coordinates = []
        # (0, 0) = self.x, (self.y - self.h)
        # (1, 1) = (self.x + (item[0] * x_spacing), (self.y - self.h - (item[1] * y_spacing)))
        self_x, self_y, self_w, self_h = self.area        
        x_spacing = self.x_spacing
        y_spacing = self.y_spacing
        for x_coord, y_coord in enumerate(self.points):
            coordinates.extend((self_x + (x_coord * x_spacing), (self_y - self_h - (y_coord * y_spacing))))
        self.draw("point", coordinates, color=self.color)
