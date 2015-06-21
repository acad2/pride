from math import floor, sqrt

import mpre
import mpre.base as base
import mpre.gui
import mpre.gui.shapes
Instruction = mpre.Instruction
objects = mpre.objects

import sdl2
import sdl2.ext
SDL_Rect = sdl2.SDL_Rect

R, G, B, A = 0, 80, 255, 30
dark_color_scalar = .5
light_color_scalar = 1.5  

def create_texture(size, access=sdl2.SDL_TEXTUREACCESS_TARGET):
    _create_texture = objects["SpriteFactory"].create_texture_sprite
    return _create_texture(objects["Renderer"].wrapped_object, size, access=access)
    
class Organizer(base.Base):
    
    pack_verbosity = 'v'
    
    def pack(self, item):
        self.alert("packing: {}, {} {}", [item, item.area, item.pack_mode], level=self.pack_verbosity)
        pack = getattr(self, "pack_{0}".format(item.pack_mode))
        parent = item.parent
        old_size = item.size

        pack(parent, item, parent.children.index(item), len(parent.children))
        self.alert("Finished packing {}: {}", [item, item.area], level=self.pack_verbosity)
        
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

    def pack_menu_bar(self, parent, item, count, length):
        item.z = parent.z + 1
        item.x = parent.x
        item.y = parent.y
        item.size = (parent.w, int(parent.h * .03))

    def pack_z(self, parent, item, count, length):
        item.z = parent.z + 1


class Window_Object(mpre.gui.shapes.Bounded_Shape):

    defaults = mpre.gui.shapes.Bounded_Shape.defaults.copy()
    defaults.update({'x' : 0,
                     'y' : 0,
                     'z' : 0,
                     'size' : mpre.gui.SCREEN_SIZE,
                     "background_color" : (25, 25, 45, 255),
                     "color" : (155, 155, 255, 255),
                     "text_color" : (145, 165, 235),
                     "outline_width" : 5,
                     "pack_mode" : '',
                     "held" : False,
                     "texture" : None,
                     "text" : '',
                     "button_verbosity" : 'v',
                     "edit_text_mode" : False,
                     "allow_text_edit" : False,
                     "_ignore_click" : False,
                     "sdl_window" : "SDL_Window"})
    Hotkeys = {}
    
    def _on_set(self, coordinate, value):
      #  coordinates = (('w', 'h', 'r', 'g', 'b', 'a') if not self. else
       #                ('w', 'h', 'r', 'g', 'b', 'a', 'x', 'y'))
        if not self.texture_invalid and coordinate in ('x', 'y', 'w', 'h', 'r', 'g', 'b', 'a'):
            self.texture_invalid = True   
        objects["SDL_Window"].invalidate_layer(self.z)
        super(Window_Object, self)._on_set(coordinate, value)
                                                                 
    def _set_z(self, value):
        objects["SDL_Window"].set_layer(self, value)
        super(Window_Object, self)._set_z(value)
    z = property(mpre.gui.shapes.Bounded_Shape._get_z, _set_z)
    
    def _get_text(self):
        return self._text
    def _set_text(self, value):
        self._text = value
        if not self.texture_invalid:
            objects["SDL_Window"].invalidate_layer(self.z)
            self.texture_invalid = True
    text = property(_get_text, _set_text)
    
    def _get_bg_color(self):
        return self._background_color
    def _set_bg_color(self, color):
        self.texture_invalid = True
        self._background_color = sdl2.ext.Color(*color)
        objects["SDL_Window"].invalidate_layer(self.z)
    background_color = property(_get_bg_color, _set_bg_color)
    
    def _get_color(self):
        return sdl2.ext.Color(*super(Window_Object, self)._get_color())
    def _set_color(self, colors):
        super(Window_Object, self)._set_color(colors)
    color = property(_get_color, _set_color)
        
    def __init__(self, **kwargs):
        self.children, self.draw_queue, self._draw_operations = [], [], []
        self.pack_count = {}
        self.texture_window_x = self.texture_window_y = self._layer_index = 0
        self.texture_invalid = True
        self._glow_modifier = 20
        max_w, max_h = mpre.gui.SCREEN_SIZE
        self.x_range = (0, max_w)
        self.w_range = (0, max_w)
        self.y_range = (0, max_h)
        self.h_range = (0, max_h)
        self.z_range = (0, mpre.gui.MAX_LAYER)   
        super(Window_Object, self).__init__(**kwargs)
        
        self.texture = create_texture(mpre.gui.SCREEN_SIZE)
        
        self.glow_instruction = Instruction(self.instance_name, "glow")
    #    self.glow_instruction.execute(.16)
        
    def glow(self):
        #color = self.color
        #r, g, b = colors = (color.r, color.g, color.b)
        #max_color = max(colors)
        #glow = self._glow_modifier = (-20 if max_color == 255 else
        #                              20 if max_color == 0 else self._glow_modifier)
        #self.color = (r + glow, g + glow, b + glow, color.a)
      #  print "set color to", glow, self.color
        color = self.color
        a = color.a
        glow = self._glow_modifier = -20 if a == 255 else 20 if a == 0 else self._glow_modifier
        self.color = (color.r, color.g, color.b, a + glow)
        
      #  bg_color = self.background_color
      #  self.background_color = (bg_color.r, bg_color.g, bg_color.b, bg_color.a + glow)
        self.glow_instruction.execute(.16)
        
    def create(self, *args, **kwargs):
        kwargs["z"] = kwargs.get('z') or self.z + 1
        return super(Window_Object, self).create(*args, **kwargs)
                
    def add(self, instance):
        self.children.append(instance)
        super(Window_Object, self).add(instance)

    def remove(self, instance):
        self.children.remove(instance)
        super(Window_Object, self).remove(instance)
        
    def press(self, mouse):
        self.alert("Pressing", level=self.button_verbosity)
        self.held = True
        for instance in self.children:
            instance.held = True        

    def release(self, mouse):
        self.alert("Releasing", level=self.button_verbosity)
        self.held = False
        if self._ignore_click:
            self._ignore_click = False
        elif mouse.button == 1:
            self.left_click(mouse)
        elif mouse.button == 3:
            self.right_click(mouse)
        else:
            self.alert("Button {} not yet implemented", [mouse.button], level=0)        
                    
    def left_click(self, mouse):
        pass
        
    def right_click(self, mouse):
        self.create("mpre.gui.widgetlibrary.Right_Click_Menu", x=mouse.x, y=mouse.y)
        self._texture_invalid = True
    
    def mousewheel(self, x_amount, y_amount):
        pass

    def mousemotion(self, x_change, y_change, top_level=True):
        if self.held:
            self._ignore_click = True
            #self.alert("Mousemotion {} {}", [x_change, y_change], level=0)
            _x, _y = self.position       
            self.x += x_change
            self.y += y_change
            
            if top_level:
                mouse_position = objects["SDL_Window"].get_mouse_position()            
                if not mpre.gui.point_in_area(self.parent.area, mouse_position):
                    if self in self.parent.children:
                    #    self.parent.alert("Removing {}; {} not in {}", [self, objects["SDL_Window"].get_mouse_position(), self.parent.area], level=0)
                        self.parent.remove(self)                    
                        self.parent.pack({"position" : self.parent.position})
                        self.z -= 1
                elif self not in self.parent.children: 
                 #   self.parent.alert("Adding {}", [self], level=0)
                    self.parent.add(self)
                    self.parent.pack({"position" : self.parent.position})
                    #self.held = False                    
            x_difference = self.x - _x
            y_difference = self.y - _y
            for instance in self.children:
                instance.held = True
                instance.mousemotion(x_difference, y_difference, top_level=False)
                instance.held = False
                
    def draw(self, figure, *args, **kwargs):
        # draw operations are enqueued and processed in batches by Renderer.draw
        self._draw_operations.append((figure, args, kwargs))
                                                               
    def _draw_texture(self):
        self.draw_texture()  
        objects["Renderer"].draw(self.texture.texture, self._draw_operations)
        self._draw_operations = []
        self.texture_invalid = False            
        return self.texture.texture
        
    def draw_texture(self):
        self.draw("fill", self.area, color=self.background_color)
        self.draw("rect", self.area, color=self.color)
        if self.text:
            self.draw("text", self.area, self.text, bg_color=self.background_color, color=self.text_color)
        
    def pack(self, modifiers=None):
        objects["Organizer"].pack(self)
        if modifiers:
            for attribute, value in modifiers.items():
                setattr(self, attribute, value)
        for item in self.children:
            item.pack()
              
    def delete(self):
        super(Window_Object, self).delete()
        objects["SDL_Window"].remove_from_layer(self, self.z)
        del objects["SDL_User_Input"].coordinate_tracker[self]
        
        
class Window(Window_Object):

    defaults = Window_Object.defaults.copy()
    defaults.update({"pack_mode" : "z"})

    
class Container(Window_Object):

    defaults = Window_Object.defaults.copy()
    defaults.update({"pack_mode" : "vertical"})


class Button(Window_Object):

    defaults = Window_Object.defaults.copy()
    defaults.update({"shape" : "rect",
                     "pack_mode" : "vertical"})
                     
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.text = self.text or self.instance_name