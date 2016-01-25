import pride.gui.gui

class Graph(pride.gui.gui.Application):
    
    defaults = {"background_color" : (0, 0, 0), "color" : (255, 255, 255),
                "x_axis_range" : (0, 100), "y_axis_range" : (0, 100)}
    mutable_defaults = {"points" : list}
    
    def __init__(self, **kwargs):
        super(Graph, self).__init__(**kwargs)
        self.x_spacing = self.w / self.x_axis_range[1]
        self.y_spacing = self.h / self.y_axis_range[1]        
        self.points = self.points or [[] for counter in range(self.x_axis_range[1])]
        
    def left_click(self, mouse):
        x = (mouse.x - self.x) / self.x_spacing        
        self.points[x].append((mouse.y - self.y))
        self.alert("Inserted point at: ({}, {})", (x, self.points[x][-1]), level=0)
        self.texture_invalid = True
        
    def draw_texture(self):
        self.draw("fill", self.area, self.background_color)
        coordinates = []
        self_x, self_y, self_w, self_h = self.area        
        x_spacing = self.x_spacing
        y_spacing = self.y_spacing
        last_point = (self_x, self_y + self_h)
        for x_coord, y_points in enumerate(self.points):
            if y_points:                
                for y_coord in y_points:
                    point = (self_x + (x_coord * x_spacing), y_coord)
                    coordinates.extend(point)
                    self.draw("line", last_point + point, color=self.color)
                    last_point = point
        self.draw("point", coordinates, color=self.color)
