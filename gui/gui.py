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
    components["Metapython"].create("mpre.gui.gui.Drawing_Surface")
    
# provides the pack() functionality
class Organizer(base.Base):

    def __init__(self, *args, **kwargs):
        super(Organizer, self).__init__(*args, **kwargs)

    def pack(self, item):
        pack = getattr(self, "pack_{0}".format(item.pack_mode))
       # raise NotImplementedError
        siblings = item.parent.objects[item.__class__.__name__]
        pack(item, siblings.index(item), len(siblings))

    def pack_horizontal(self, item, count, length):
        parent = item.parent
        item.z = parent.z + 1
        item.size = (parent.size[0]/length, parent.size[1])
        item.x = (item.size[0]*count)+parent.x
        item.y = parent.y

    def pack_vertical(self, item, count, length):
        parent = item.parent
        item.z = parent.z + 1
        item.size = (parent.size[0], parent.size[1]/length)
        item.y = (item.size[1]*count)+parent.y
        item.x = parent.x

    def pack_grid(self, item, count, length):
        grid_size = sqrt(length)

        if grid_size != floor(grid_size):
            grid_size = floor(grid_size)+1

        position = (int(floor((count / grid_size))), (count % grid_size))

        parent = item.parent
        item.z = parent.z + 1
        item.size = int(parent.size[0]/grid_size), int(parent.size[1]/grid_size)
        item.x = (item.size[0]*position[1])+parent.x
        item.y = (item.size[1]*position[0])+parent.y

    def pack_text(self, item, count, length):
        parent = item.parent
        item.z = parent.z + 1
        item.x = parent.x + parent.x_width + parent.x_spacing
        item.y = parent.y

    def pack_menu_bar(self, item, count, length):
        parent = item.parent
        item.z = parent.z + 1
        item.x = parent.x
        item.y = parent.y
        item.size = (parent.size[0], int(parent.size[1]*.03))

    def pack_z(self, item, count, length):
        parent = item.parent
        item.z = parent.z + 1

        
# provides an interface to draw primitives onto a surface
class Drawing_Surface(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"size" : mpre.gui.SCREEN_SIZE,
                     "bpp" : 32,
                     "masks" : None})
                     
    def __init__(self, **kwargs):
        #self.renderers = {}
        super(Drawing_Surface, self).__init__(**kwargs)
        sprite = components["SpriteFactory"].create_software_sprite(self.size, self.bpp, self.masks)
        renderer = self.renderer = self.create("mpre.gui.sdllibrary.Renderer", window=sprite)
        self.sprite = sprite
        
        self.instructions = dict((name, getattr(renderer, "draw_" + name)) for 
                                  name in ("point", "line", "rect", "rect_width", "text"))
        self.instructions["fill"] = renderer.fill
        
    def draw(self, draw_instructions, textures=tuple()):
        renderer = self.renderer
        renderer.clear()
        
        instructions = self.instructions
        for shape, args, kwargs in draw_instructions:
            instructions[shape](*args, **kwargs)
            
        if textures:
            for texture in textures:
                renderer.copy(texture)
        return components["SpriteFactory"].from_surface(renderer.rendertarget)
                                
 
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
                     "sdl_window" : "SDL_Window"})
    Hotkeys = {}
    
    def _on_set(self, coordinate, value):
        self.texture_invalid = True
        super(Window_Object, self)._on_set(coordinate, value)    
    
    def _set_z(self, value):
        components["SDL_Window"].draw(self)
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
        self._draw_operations = []
        self.draw_queue = []   
        super(Window_Object, self).__init__(**kwargs)
        max_w, max_h = mpre.gui.SCREEN_SIZE
        self.x_range = (0, max_w)
        self.w_range = (0, max_w)
        self.y_range = (0, max_h)
        self.h_range = (0, max_h)
        self.z_range = (0, mpre.gui.MAX_LAYER)    
        kwargs.update(self.defaults)
        self.x = kwargs['x']# if 'x' in kwargs else 0
        self.y = kwargs['y']# if 'y' in kwargs else 0
        self.z = kwargs['z']# if 'z' in kwargs else 0
        if 'size' in kwargs:
            self.size = kwargs['size']
        else:
            self.w = kwargs['w']# if 'w' in kwargs else 0
            self.h = kwargs['h']# if 'h' in kwargs else 0
            
    def create(self, *args, **kwargs):
        kwargs["z"] = kwargs.get('z') or self.z + 1
        return super(Window_Object, self).create(*args, **kwargs)
                
    def add(self, instance):
        self.linked_shapes.append(instance)
        super(Window_Object, self).add(instance)

    def remove(self, instance):
        self.linked_shapes.remove(instance)
        super(Window_Object, self).remove(instance)
        
    def press(self, mouse):
        self.held = True

    def release(self, mouse):
        self.held = False
        self.click(mouse)

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
        self._draw_operations.append((figure, args, kwargs))
      #  self.texture = mpre.components["Drawing_Surface"].draw((figure, args, kwargs), 
      #                                                         background=self.texture)
                                                              
    def _draw_texture(self):
        textures = [child._draw_texture() for child in self.linked_shapes]
        if self.texture_invalid:
            self.draw_texture()       
            self.texture = components["Drawing_Surface"].draw(self._draw_operations, textures)
            self._draw_operations = []
            self.texture_invalid = False            
        return self.texture
        
    def draw_texture(self):
      #  print "filling area: ", self.area
        self.draw("fill", self.area, color=(0, 0, 0))
        self.draw("rect", (0, 0, 100, 150), color=(200, 15, 15))
        self.draw("text", "yus", size=self.w, color=(255, 155, 155))
        
    def pack(self, reset=False):
        if reset:
            self.x = self.y = 0
        components["Organizer"](pack, self)
        #for item in self.linked_shapes:
         #   item.pack()

    def remove(self, item):
        self.linked_shapes.remove(item)
        super(Window_Object, self).remove(item)

    
class Window(Window_Object):

    defaults = Window_Object.defaults.copy()
    defaults.update({"show_title_bar" : False,
                     "pack_mode" : "z"})

    def __init__(self, **kwargs):
        super(Window, self).__init__(**kwargs)

        #if getattr(self, "title_bar", None):
        self.create("mpre.gui.widgetlibrary.Title_Bar")

    
class Container(Window_Object):

    defaults = Window_Object.defaults.copy()
    defaults.update({"alpha" : 1,
                     "pack_mode" : "vertical"})

    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)


class Button(Window_Object):

    defaults = Window_Object.defaults.copy()
    defaults.update({"shape" : "rect",
                     "text" : "Button",
                     "text_color" : (255, 130, 25)})

    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)

    def draw_texture(self):
        super(Button, self).draw_texture()
        self.draw("text", self.text, self.area, color=self.text_color)
