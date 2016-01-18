import pride.gui.gui

class Graph(pride.gui.gui.Window):
    
    defaults = {"background_color" : (255, 255, 255), "color" : (0, 0, 0)}
    mutable_defaults = {"points" : lambda: [0 for counter in range(pride.gui.gui.MAX_W)]}
    
    def left_click(self, mouse):
        self.points[mouse.x] = (mouse.y + self.points[mouse.x]) / 2
        self.texture_invalid = True
        
    def draw_texture(self):
        self.draw("fill", self.area, self.background_color)
        coordinates = []
        for x_coord, y_coord in enumerate(self.points):
            coordinates.extend((x_coord, y_coord))
        self.draw("point", coordinates, color=self.color)
