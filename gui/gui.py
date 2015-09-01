from math import floor, sqrt, ceil

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

def create_texture(size, access=sdl2.SDL_TEXTUREACCESS_TARGET):
    _create_texture = objects["SpriteFactory"].create_texture_sprite
    return _create_texture(objects["Renderer"].wrapped_object, size, access=access)
    
class Organizer(base.Base):
    
    pack_verbosity = 'v'
    
    def __init__(self, **kwargs):
        super(Organizer, self).__init__(**kwargs)
        self.pack_modes, self._pack_modes, self._pack_index = {}, {}, {}        
        
    def get_pack_mode(self, instance):
        return self.pack_modes[instance]
     
    def set_pack_mode(self, instance, value): 
        if value is None:
            try:
                del self._pack_modes[instance]
            except KeyError: 
                pass
            del self.pack_modes[instance]
            del self._pack_index[instance]  
            
        parent = mpre.objects[instance].parent.instance_name
        old_pack_mode = self.pack_modes.get(instance, '')
        if old_pack_mode:
            self._pack_modes[parent][old_pack_mode].remove(instance)

        self.pack_modes[instance] = value
        try:
            self._pack_modes[parent][value].append(instance)
        except KeyError:
            if parent not in self._pack_modes:
                self._pack_modes[parent] = {value : [instance]}
            else:
                self._pack_modes[parent][value] = [instance]
        self._pack_index[instance] = self._pack_modes[parent][value].index(instance)
    
    def add_pack_method(self, name, callback):
        setattr(self, name, "pack_{}".format(name), callback)
        
    def pack(self, item):
        self.alert("packing: {}, {} {}", [item, item.area, item.pack_mode],
                   level=self.pack_verbosity)
        instance_name = item.instance_name
        pack_mode = self.pack_modes[instance_name]
        pack = getattr(self, "pack_{0}".format(pack_mode))
        parent = item.parent
        old_size = item.size

        pack(parent, item, self._pack_index[instance_name], 
             len(self._pack_modes[parent.instance_name][pack_mode]))
        self.alert("Finished packing {}: {}", [item, item.area], 
                   level=self.pack_verbosity)
        
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
        item.size = (parent.w,
                     parent.h / 5 if parent.h else 0)

    def pack_z(self, parent, item, count, length):
        item.z = parent.z + 1

    def pack_bottom(self, parent, item, count, length):
        self.pack_menu_bar(parent, item, count, length)
        item.y = parent.y + parent.h - item.h
     
    def pack_top(self, parent, item, count, length):
        self.pack_menu_bar(parent, item, count, length)
        item.y = parent.y - item.h
        print "Setting y to: {} - {} = {}".format(parent.y, item.h, item.y)
        
    def pack_right(self, parent, item, count, length):
        self.pack_vertical(parent, item, count, length)
        item.x = parent.x + parent.w - item.w
                
    def pack_left(self, parent, item, count, length):
        self.pack_vertical(parent, item, count, length)
        item.x = parent.x
        
        
class Window_Object(mpre.gui.shapes.Bounded_Shape):

    defaults = mpre.gui.shapes.Bounded_Shape.defaults.copy()
    defaults.update({'x' : 0,
                     'y' : 0,
                     'z' : 0,
                     'size' : mpre.gui.SCREEN_SIZE,
                     "texture_size" : mpre.gui.SCREEN_SIZE,
                     "background_color" : (25, 125, 225, 125),
                     "color" : (25, 235, 235, 255),
                     "text_color" : (145, 165, 235),
                     "pack_mode" : '',
                     "held" : False,
                     "texture" : None,
                     "text" : '',
                     "button_verbosity" : 'v',
                     "allow_text_edit" : False,
                     "_ignore_click" : False,
                     "sdl_window" : "SDL_Window",
                     "movable" : True,
                     "hidden" : False})
    Hotkeys = {}
    
    def _get_texture_invalid(self):
        return self._texture_invalid
    def _set_texture_invalid(self, value):
        if not self._texture_invalid and value:
            objects["SDL_Window"].invalidate_layer(self.z)
        self._texture_invalid = value
    texture_invalid = property(_get_texture_invalid, _set_texture_invalid)
    
    def _on_set(self, coordinate, value):
      #  coordinates = (('w', 'h', 'r', 'g', 'b', 'a') if not self. else
       #                ('w', 'h', 'r', 'g', 'b', 'a', 'x', 'y'))
        if not self.texture_invalid and coordinate in ('x', 'y', 'w', 'h', 'r', 'g', 'b', 'a'):
            self.texture_invalid = True           
        super(Window_Object, self)._on_set(coordinate, value)
                                                                 
    def _set_z(self, value):
        objects["SDL_Window"].set_layer(self, value)
        super(Window_Object, self)._set_z(value)
    z = property(mpre.gui.shapes.Bounded_Shape._get_z, _set_z)
    
    def _get_text(self):
        return self._text
    def _set_text(self, value):
        self._text = value
        self.texture_invalid = True
    text = property(_get_text, _set_text)
    
    def _get_bg_color(self):
        return self._background_color
    def _set_bg_color(self, color):
        self.texture_invalid = True
        self._background_color = sdl2.ext.Color(*color)
    background_color = property(_get_bg_color, _set_bg_color)
    
    def _get_color(self):
        return super(Window_Object, self)._get_color()
    def _set_color(self, colors):
        super(Window_Object, self)._set_color(colors)
        self.texture_invalid = True        
    color = property(_get_color, _set_color)
    
    def _get_text_color(self):
        return self._text_color
    def _set_text_color(self, colors):
        self._text_color = sdl2.ext.Color(*colors)
        self.texture_invalid = True
    text_color = property(_get_text_color, _set_text_color)
    
    def _get_texture_window_x(self):
        return self._texture_window_x
    def _set_texture_window_x(self, value):
        self._texture_window_x = max(self.x_range[0], min(value, self.w))
        self.texture_invalid = True
    texture_window_x = property(_get_texture_window_x, _set_texture_window_x)
    
    def _get_texture_window_y(self):
        return self._texture_window_y
    def _set_texture_window_y(self, value):
        self._texture_window_y = max(self.y_range[0], min(value, self.h))
        self.texture_invalid = True
    texture_window_y = property(_get_texture_window_y, _set_texture_window_y)
    
    def _get_pack_mode(self):      
        return objects["Organizer"].get_pack_mode(self.instance_name)
    def _set_pack_mode(self, value):
        objects["Organizer"].set_pack_mode(self.instance_name, value)
    pack_mode = property(_get_pack_mode, _set_pack_mode)
    
    def __init__(self, **kwargs):
        self._texture_invalid = False
        self.children, self.draw_queue, self._draw_operations = [], [], []
        self.pack_count = {}
        self._layer_index = 0        
        self._texture_window_x = self._texture_window_y = 0
        self._glow_modifier = 20
        max_w, max_h = mpre.gui.SCREEN_SIZE
        self.x_range = (0, max_w)
        self.w_range = (0, max_w)
        self.y_range = (0, max_h)
        self.h_range = (0, max_h)
        self.z_range = (0, mpre.gui.MAX_LAYER)   
        super(Window_Object, self).__init__(**kwargs)
        self.texture_window_x = self.texture_window_y = 0
        self.available_size = self.size
        self.texture = create_texture(self.texture_size)
        self.texture_invalid = True
        
    #    self.glow_instruction = Instruction(self.instance_name, "glow")
    #    self.glow_instruction.execute(.16)
    #    
    #def glow(self):
    #    #color = self.color
    #    #r, g, b = colors = (color.r, color.g, color.b)
    #    #max_color = max(colors)
    #    #glow = self._glow_modifier = (-20 if max_color == 255 else
    #    #                              20 if max_color == 0 else self._glow_modifier)
    #    #self.color = (r + glow, g + glow, b + glow, color.a)
    #  #  print "set color to", glow, self.color
    #    color = self.color
    #    a = color.a
    #    glow = self._glow_modifier = -20 if a == 255 else 20 if a == 0 else self._glow_modifier
    #    self.color = (color.r, color.g, color.b, a + glow)
    #    
    #  #  bg_color = self.background_color
    #  #  self.background_color = (bg_color.r, bg_color.g, bg_color.b, bg_color.a + glow)
    #    self.glow_instruction.execute(.16)
        
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
            self.alert("Button {} not yet implemented", 
                       [mouse.button])        
                    
    def left_click(self, mouse):
        pass
        
    def right_click(self, mouse):
        pass

    def mousewheel(self, x_amount, y_amount):
        pass

    def mousemotion(self, x_change, y_change, top_level=True):
        if self.movable and self.held:
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
     
    def toggle_hidden(self):
        if not self.hidden:
            sdl_user_input = mpre.objects["SDL_User_Input"]
            sdl_user_input._update_coordinates(self.instance_name,
                                               self.area, -1)            
        self.hidden = not self.hidden
       
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
            self.draw("text", self.area, self.text, 
                      bg_color=self.background_color, color=self.text_color)
        
    def pack(self, modifiers=None):
        objects["Organizer"].pack(self)
        if modifiers:
            for attribute, value in modifiers.items():
                setattr(self, attribute, value)
        
        size = self.available_size = self.size
        for item in self.children:
            item.pack()
            size = self.available_size = size[0] - item.x, size[1] - item.y
            
    def delete(self):
        self.pack_mode = None # clear Organizer cache
        super(Window_Object, self).delete()
        objects["SDL_Window"].remove_from_layer(self, self.z)
        objects["SDL_User_Input"]._remove_from_coordinates(self.instance_name) 

        
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
