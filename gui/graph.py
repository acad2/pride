import itertools

import pride.gui.gui
import pride.vmlibrary

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
    
    @pride.preprocess
    def _generate_draw_x_descriptors():
        source = []
        for draw_type in ("lines", "points", "average"):
            source.append("    def _get_draw_{}(self): return self._draw_{}\n".format(draw_type, draw_type))
            source.append("    def _set_draw_{}(self, value):".format(draw_type))
            source.append("        self._draw_{} = value; self.texture_invalid = True".format(draw_type))
            source.append("    draw_{} = property(_get_draw_{}, _set_draw_{})\n".format(draw_type, draw_type, draw_type))
        return '\n'.join(source)[4:]
        
    def __init__(self, **kwargs):
        super(Graph, self).__init__(**kwargs)     
        self.points = self.points or [0 for counter in range(self.x_axis_range[1])]             
        
    def left_click(self, mouse):
        x = (mouse.x - self.x) / self.x_spacing        
        y = self.points[x] = mouse.y - self.y
        self.alert("Inserted point at: ({}, {})", (x, y), level=0)
        self.texture_invalid = True
        
    def draw_texture(self):   
        super(Graph, self).draw_texture()        
        lines, coordinates = [], []
        scalar = 1.0 / ((max(self.points) / self.h) or 1)    
        assert scalar <= 1.0, (scalar, max(self.points), self.h)
        if scalar < 1.0:
            points = [int(point * scalar) for point in self.points[::self.step_size]]
        else:
            points = self.points[::self.step_size]
                 
        self_x, self_y, self_w, self_h = self.area          
        point_count = len(points)
        x_spacing = float(self_w) / (point_count or 1)
        
        max_point = max(points)
        self.y_axis_range = (self.y_axis_range[0], max_point)      
        y_spacing = float(self_h) / (max_point or 1)
        #if point_count > self_w:       
        #    x_spacing = float(self_w) / (point_count or 1)
        #    #x_spacing, extra = divmod(len(points), self_w)
        #    #x_spacing = x_spacing + 1 if extra else (x_spacing or 1)
        #else:
        #    x_spacing = float(
        #    x_spacing, extra = divmod(self_w, len(points))
        #    x_spacing = x_spacing + 1 if extra else (x_spacing or 1)
        

      #      
      #  if max_point < self_h:
      #      y_spacing, extra = divmod(max_point, self_h)
      #      y_spacing = y_spacing + 1 if extra else (y_spacing or 1)
      #  else:
      #      y_spacing = float(self_h) / (max_point or 1)
            
        last_point = (self_x, self_y + self_h)
        color = self.color
        for x_coord, y_coord in enumerate(point for point in points if point):            
            point = (self_x + int(x_coord * x_spacing), (self_y + self_h) - int(y_coord * y_spacing)) 
            print point
            coordinates.extend(point)
            lines.extend(last_point + point)
            last_point = point
            
        window = self.application_window
        window.draw("fill", self.area, self.background_color)
        if self.draw_points:
            window.draw("point", coordinates, color=color)
        if self.draw_lines:
            window.draw("line", lines, color=color)            
        if self.draw_average:
            average_object = pride.datastructures.Average(values=self.points)
            minimum, _average, maximum = average_object.range
            _average = self_h - int(average_object.meta_average)
            minimum = self_h - minimum
            maximum = self_h - maximum
            right_side = self_x + self_w            
            window.draw("line", (self_x, minimum, right_side, minimum), color=self.color)
            window.draw("line", (self_x, _average, right_side, _average), color=self.color)
            window.draw("line", (self_x, maximum, right_side, maximum), color=self.color)
        
            
class Audio_Visualizer(Graph):
                
    defaults = {"audio_input" : "/Python/Audio_Manager/Audio_Input",
                "draw_average" : False, "draw_lines" : False, "step_size" : 8}
    
    def __init__(self, **kwargs):
        super(Audio_Visualizer, self).__init__(**kwargs)
        objects[self.audio_input].add_listener(self.reference)
        
    def handle_audio_input(self, samples):    
        self.points = bytearray(samples)
        
    def delete(self):
        objects[self.audio_input].remove_listener(self.reference)
        super(Audio_Visualizer, self).delete()
                
                
class Grapher(pride.vmlibrary.Process):
    
    defaults = {"priority" : .02}
    mutable_defaults = {"counter" : itertools.count, "graph" : Graph}
    
    def run(self):
        graph = self.graph
        graph.points.append(self.function(next(self.counter)))
        del graph.points[0]
        graph.texture_invalid = True        

    def function(self, function_input):
        raise NotImplementedError
                
        