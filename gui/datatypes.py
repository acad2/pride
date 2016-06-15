import pride.gui.gui
       

class Outline(pride.gui.gui.Button):
    
    defaults = {"background_color" : (0, 0, 0, 0)}
    
    def mousemotion(self, x_change, y_change, top_level=True):
        mouse_position = objects[self.sdl_window].get_mouse_position()
        x, y, w, h = self.area
        outline_width = self.outline_width
        left_edge = x + outline_width
        right_edge = left_edge + w
        top_edge = y + outline_width
        bottom_edge = top_edge + h
        
        if mouse_position[0] in (left_edge, right_edge):
            if mouse_position[1] in (top_edge, bottom_edge):
                

       
class Python_Datatype_Button(pride.gui.gui.Button):

    def __init__(self, value, **kwargs):
        super(Python_Datatype_Button, self).__init__(**kwargs)
        self.value = value
        self.text = str(value)

        
class int_Button(Python_Datatype_Button): pass
    
   
class str_Button(Python_Datatype_Button): pass

        
class List(pride.gui.gui.Container):
    
    mutable_defaults = {"list" : list}
    
    def append(self, value):
        self.list.append(value)
        self.create("pride.gui.datatypes.{}_Button".format(value.__class__.__name__), value)
        
    def pop(self, index=-1):
        self.list.pop(index)
        self.stored_objects[index].delete()