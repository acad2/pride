import pride.gui.gui

class Graph(pride.gui.gui.Application):
    
    defaults = {"background_color" : (0, 0, 0), "color" : (255, 255, 255),
                "minimum_color" : (0, 0, 255), "maximum_color" : (255, 0, 0),
                "average_color" : (0, 255, 0),
                "x_axis_range" : (0, 255), "y_axis_range" : (0, 255),
                "draw_lines" : True, "draw_points" : True, "draw_average" : True,
                "step_size" : None}
    mutable_defaults = {"points" : list}
    
    def _get_points(self):
        return self._points
    def _set_points(self, value):
        self._points = value        
        self.texture_invalid = True
    points = property(_get_points, _set_points)
    
    def __init__(self, **kwargs):
        super(Graph, self).__init__(**kwargs)
        self.x_spacing = self.w / self.x_axis_range[1]
        self.y_spacing = self.h / self.y_axis_range[1]        
        self.points = self.points or [0 for counter in range(self.x_axis_range[1])]             
        
    def left_click(self, mouse):
        x = (mouse.x - self.x) / self.x_spacing        
        y = self.points[x] = mouse.y - self.y
        self.alert("Inserted point at: ({}, {})", (x, y), level=0)
        self.texture_invalid = True
        
    def draw_texture(self):        
        self.draw("fill", self.area, self.background_color)
        lines, coordinates = [], []
        self_x, self_y, self_w, self_h = self.area        
        x_spacing = self.x_spacing
        y_spacing = self.y_spacing
        last_point = (self_x, self_y + self_h)
        color = self.color
        for x_coord, y_coord in enumerate(point for point in self.points[::self.step_size] if point):            
            point = (self_x + (x_coord * x_spacing), y_coord)
            coordinates.extend(point)
            lines.extend(last_point + point)
            last_point = point
        if self.draw_points:
            self.draw("point", coordinates, color=color)
        if self.draw_lines:
            self.draw("line", lines, color=color)            
        if self.draw_average:
            average_object = pride.datastructures.Average(values=self.points)
            minimum, _average, maximum = average_object.range
            _average = int(average_object.meta_average)
            right_side = self_x + self_w            
            self.draw("line", (self_x, minimum, right_side, minimum), color=self.color)
            self.draw("line", (self_x, _average, right_side, _average), color=self.color)
            self.draw("line", (self_x, maximum, right_side, maximum), color=self.color)
        
            
class Audio_Visualizer(Graph):
                
    defaults = {"audio_input" : "->Python->Audio_Manager->Audio_Input",
                "draw_average" : False, "draw_lines" : False, "step_size" : 8}
    
    def __init__(self, **kwargs):
        super(Audio_Visualizer, self).__init__(**kwargs)
        objects[self.audio_input].add_listener(self.reference)
        
    def handle_audio_input(self, samples):    
        self.points = bytearray(samples)
        
    def delete(self):
        objects[self.audio_input].remove_listener(self.reference)
        super(Audio_Visualizer, self).delete()
        