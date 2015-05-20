import heapq
import ctypes
from operator import attrgetter
from sys import modules
from math import floor, sqrt

import mpre
import mpre.base as base
import mpre.vmlibrary as vmlibrary
import mpre.utilities as utilities
import mpre.gui
import mpre.gui.shapes
Instruction = mpre.Instruction
components = mpre.components

import sdl2
import sdl2.ext
SDL_Rect = sdl2.SDL_Rect

R, G, B, A = 0, 80, 255, 30
dark_color_scalar = .5
light_color_scalar = 1.5

def enable():
    components["Metapython"].create("mpre.gui.sdllibrary.SDL_Window")    
    components["Metapython"].create("mpre.gui.gui.Organizer")        

class Organizer(base.Base):
    
    def pack(self, item):
     #   self.alert("packing: {}, {} {}", [item, item.area, item.pack_mode], level=0)
        pack = getattr(self, "pack_{0}".format(item.pack_mode))
        parent = item.parent
        pack(parent, item, parent.children.index(item), len(parent.children))        
      #  self.alert("Finished packing {}: {}", [item, item.area], level=0)
        
    def pack_horizontal(self, parent, item, count, length):
        item.z = parent.z + 1
        #print "Setting {}.area to: ({} / {} (={}), {}".format(item, parent.w, length, parent.w / length, parent.h)
        item.size = (parent.w / length, parent.h)
        item.x = (item.w * count) + parent.x
        item.y = parent.y

    def pack_vertical(self, parent, item, count, length):
        item.z = parent.z + 1
        item.size = (parent.w, parent.h / length)
        item.y = (item.h * count) + parent.y
        item.x = parent.x

    def pack_grid(self, parent, item, count, length):
        grid_size = sqrt(length)

        if grid_size != floor(grid_size):
            grid_size = floor(grid_size) + 1
        position = (int(floor((count / grid_size))), (count % grid_size))

        item.z = parent.z + 1
        item.size = int(parent.w / grid_size), int(parent.h / grid_size)
        item.x = (item.w * position[1]) + parent.x
        item.y = (item.h * position[0]) + parent.y

    def pack_text(self, parent, item, count, length):
        item.z = parent.z + 1
        item.x = parent.x + parent.w + parent.x_spacing
        item.y = parent.y

    def pack_menu_bar(self, parent, item, count, length):
        item.z = parent.z + 1
        item.x = parent.x
        item.y = parent.y
        item.size = (parent.w, int(parent.h * .03))

    def pack_z(self, parent, item, count, length):
        item.z = parent.z + 1


class Window_Object(mpre.gui.shapes.Coordinate_Linked):

    defaults = mpre.gui.shapes.Coordinate_Linked.defaults.copy()
    defaults.update({'x' : 0,
                     'y' : 0,
                     'z' : 0,
                     'size' : mpre.gui.SCREEN_SIZE,
                     "background_color" : (0, 0, 0),
                     "color" : (R, G, B),
                     "outline_width" : 5,
                     "pack_mode" : '',
                     "held" : False,
                     "pack_modifier" : '',
                     "color_scalar" : .6,
                     "pack_on_init" : True,
                     "texture_invalid" : True,
                     "texture" : None,
                     "text" : '',
                     "sdl_window" : "SDL_Window"})
    Hotkeys = {}
    
    def _on_set(self, coordinate, value):
        self.texture_invalid = True     
        super(Window_Object, self)._on_set(coordinate, value)
        components["SDL_User_Input"]._update_coordinates(self, self.area, self.z)
                                                         
    def _set_z(self, value):
        components["SDL_Window"].set_layer(self, value)
        super(Window_Object, self)._set_z(value)
    z = property(mpre.gui.shapes.Coordinate_Linked._get_z, _set_z)
    
    def _get_outline_color(self):
        return (int(self.color[0]*self.color_scalar), int(self.color[1]*\
        self.color_scalar), int(self.color[2]*self.color_scalar))
    outline_color = property(_get_outline_color)

    def _get_rect(self):
        return sdl2.SDL_Rect(*self.area)
    rect = property(_get_rect)

    def __init__(self, **kwargs):
        self.children, self.draw_queue, self._draw_operations = [], [], []
        self.pack_count = {}
        self._layer_index = 0
        
        max_w, max_h = mpre.gui.SCREEN_SIZE
        self.x_range = (0, max_w)
        self.w_range = (0, max_w)
        self.y_range = (0, max_h)
        self.h_range = (0, max_h)
        self.z_range = (0, mpre.gui.MAX_LAYER)   
        super(Window_Object, self).__init__(**kwargs)
        
        self.texture = (components["SpriteFactory"].create_texture_sprite(
                        components["Renderer"].wrapped_object,
                        self.size,
                        access=sdl2.SDL_TEXTUREACCESS_TARGET))
                        
    def create(self, *args, **kwargs):
        kwargs["z"] = kwargs.get('z') or self.z + 1
        return super(Window_Object, self).create(*args, **kwargs)
                
    def add(self, instance):
        self.children.append(instance)
        self.linked_shapes.append(instance)
        super(Window_Object, self).add(instance)

    def remove(self, instance):
        self.children.remove(instance)
        self.linked_shapes.remove(instance)
        super(Window_Object, self).remove(instance)
        
    def press(self, mouse):
        self.held = True

    def release(self, mouse):
        self.held = False
        self.click(mouse)
        self.alert("Releasing", level=0)
        
    def click(self, mouse):
        if mouse.button == 3:
            self.create("mpre.gui.widgetlibrary.Right_Click_Menu", x=mouse.x, y=mouse.y)
            self.draw_texture()
    
    def mousewheel(self, x_amount, y_amount):
        pass

    def mousemotion(self, x_change, y_change):
        if self.held:
            self.x += x_change
            self.y += y_change

    def draw(self, figure, *args, **kwargs):
        # draw operations are enqueud and processed in batches
        self._draw_operations.append((figure, args, kwargs))
                                                               
    def _draw_texture(self):
        self.draw_texture()  
        components["Renderer"].draw(self.texture.texture, self._draw_operations)
        self._draw_operations = []
        self.texture_invalid = False            
        return self.texture.texture
        
    def draw_texture(self):
        self.draw("fill", self.area, color=(25, 25, 45))
        self.draw("rect", self.area, color=(155, 155, 255))
        if self.text:
            self.draw("text", self.text, bg_color=(25, 25, 45), color=(255, 155, 155))
        
    def pack(self, reset=False):
        if reset:
            self.x = self.y = 0
        components["Organizer"].pack(self)
        for item in self.children:
            item.pack()

    
class Window(Window_Object):

    defaults = Window_Object.defaults.copy()
    defaults.update({"pack_mode" : "z"})

    
class Container(Window_Object):

    defaults = Window_Object.defaults.copy()
    defaults.update({"alpha" : 1,
                     "pack_mode" : "vertical"})


class Button(Window_Object):

    defaults = Window_Object.defaults.copy()
    defaults.update({"shape" : "rect",
                     "text" : "Button",
                     "text_color" : (255, 130, 25)})

    def draw_texture(self):
        super(Button, self).draw_texture()
        self.draw("text", self.text, color=self.text_color)
