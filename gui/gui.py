from math import floor, sqrt, ceil

import pride
import pride.base as base
import pride.gui
import pride.gui.shapes
Instruction = pride.Instruction
objects = pride.objects

import sdl2
import sdl2.ext
SDL_Rect = sdl2.SDL_Rect

R, G, B, A = 0, 80, 255, 30

MAX_W, MAX_H = pride.gui.SCREEN_SIZE
_OPPOSING_SIDE = {"left" : "right", "right" : "left", "top" : "bottom", "bottom" : "top"}

def create_texture(size, access=sdl2.SDL_TEXTUREACCESS_TARGET,
                   factory="->Python->SDL_Window->Renderer->SpriteFactory",
                   renderer="->Python->SDL_Window->Renderer"):
    return objects[factory].create_texture_sprite(objects[renderer].wrapped_object,
                                                  size, access=access)
    
class Organizer(base.Base):
    
    verbosity = {"packing" : 'vvv'}
    
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
            old_pack_mode = self.pack_modes.pop(instance)
            del self._pack_index[instance]  
            
            _instance = pride.objects[instance]
            parent = _instance.parent_name
            if parent in self._pack_modes:
            #    print "removing : ", _instance, self._pack_modes[parent][old_value]
                self._pack_modes[parent][old_pack_mode].remove(instance)
            return
        parent = pride.objects[instance].parent.instance_name
        old_pack_mode = self.pack_modes.get(instance, '')
        if old_pack_mode:
            self._pack_modes[parent][old_pack_mode].remove(instance)

        self.pack_modes[instance] = value
        try:
            self._pack_modes[parent][value].append(instance)
        except KeyError:
            if parent not in self._pack_modes:
                self._pack_modes[parent] = dict((key, []) for key in ("top", "bottom", "left", "right", "main"))
                self._pack_modes[parent][value] = [instance]
            else:
                self._pack_modes[parent][value] = [instance]
        self._pack_index[instance] = self._pack_modes[parent][value].index(instance)
    
    def add_pack_method(self, name, callback):
        setattr(self, name, "pack_{}".format(name), callback)
        
    def pack(self, item):
        self.alert("packing: {}, {} {} {}", 
                  [item, item.area, item.z, item.pack_mode],
                   level=self.verbosity["packing"])
        instance_name = item.instance_name
        pack_mode = self.pack_modes[instance_name]
        pack = getattr(self, "pack_{0}".format(pack_mode))
        parent = item.parent
        old_size = item.size
        pack(parent, item, self._pack_index[instance_name], 
             len(self._pack_modes[parent.instance_name][pack_mode]))
        self.alert("Finished packing {}: {} {}", [item, item.area, item.z], 
                   level=self.verbosity["packing"])
    
    def pack_main(self, parent, item, count, length):
        item.z = parent.z + 1
        pack_modes = self._pack_modes[parent.instance_name]
        sides = [[objects[name] for name in pack_modes[side]] for side in ("top", "bottom", "left", "right")]
        top, bottom, left, right = sides
        top_count, bottom_count, left_count, right_count = (len(item) for item in sides)
        item_x, item_y, item_w, item_h = parent_x, parent_y, parent_w, parent_h = parent.area

        try:
            width_spacing = parent_w / (left_count + right_count)
        except ZeroDivisionError:
            width_spacing = parent_w
        try:
            height_spacing = parent_h / (top_count + bottom_count)
        except ZeroDivisionError:
            height_spacing = parent_h
        
        width_of = lambda side: sum(item.w or min(width_spacing, item.w_range[1]) for item in side)
        height_of = lambda side: sum(item.h or min(height_spacing, item.h_range[1]) for item in side)

        item.area = (item_x + width_of(left), item_y + height_of(top), 
                     item_w - width_of(right), item_h - height_of(bottom))                         
        
    def pack_left(self, parent, item, count, length):
        item.z = parent.z + 1       
        pack_modes = self._pack_modes[parent.instance_name]
        space_per_object = parent.w / (length + len(pack_modes["right"]))
        left_items = [objects[name] for name in pack_modes["left"][:count]]
        if left_items:
            required_space = lambda item: item.w or min(space_per_object, item.w_range[1])
            left_total = sum(required_space(item) for item in left_items)
        else:
            left_total = 0
        top_items = [objects[name] for name in pack_modes["top"]]
        bottom_objects = [objects[name] for name in pack_modes["bottom"]]
        height_per_object = parent.h / (len(top_items) + len(bottom_objects) or 1)
        item.position = parent.x + left_total, parent.y + sum(item.h or min(height_spacing, item.h_range[1]) for item in top_items)     
        
        item_height = parent.h - sum(item.h or min(height_per_object, item.h_range[1]) for item in bottom_objects)
        if count == length - 1:
            item_w = parent.w - item.x
            if pack_modes["right"]:
                right_items = [objects[name] for name in pack_modes["right"]]
                required_space = lambda item: item.w or min(space_per_object, item.w_range[1])
                item_w -= sum(required_space(item) for item in right_items)
            item.size = (max(item_w, 0) or space_per_object, item_height)    
        else:
            item.size = (space_per_object, item_height)             
   
    def pack_top(self, parent, item, count, length):
        item.z = parent.z + 1
        assert parent.w
        top_size = parent.h / length
        if count:
            top_items = (objects[name] for name in self._pack_modes[parent.instance_name]["top"][:count])
            
            item.y = parent.y + sum(top_item.h or min(top_size, top_item.h_range[1]) for
                                    top_item in top_items)
        else:
            item.y = parent.y
        item.x = parent.x
        
        if count == length - 1:
            bottom_objects = [objects[name] for name in self._pack_modes[parent.instance_name]["bottom"]]
            item_h = parent.h - item.y
            if bottom_objects:
                width_spacing = parent.h / len(bottom_objects)
                item_h - sum(bottom_object.h or min(width_spacing, bottom_object.h_range[1]) for
                             bottom_object in bottom_objects)
            item.size = (parent.w, item_h)
        else:
            item.size = (parent.w, top_size)  
        assert item.w, (item.size, item)
            
    def pack_grid(self, parent, item, count, length):
        grid_size = sqrt(length)

        if grid_size != floor(grid_size):
            grid_size = floor(grid_size) + 1
        position = (int(floor((count / grid_size))), (count % grid_size))

        item.z = parent.z + 1
        item.size = int(parent.w / grid_size), int(parent.h / grid_size)
        item.x = (item.w * position[1]) + parent.x
        item.y = (item.h * position[0]) + parent.y

    def pack_z(self, parent, item, count, length):
        item.z = parent.z + 1

    def pack_bottom(self, parent, item, count, length):
        item.z = parent.z + 1       
        assert parent.w
        bottom_size = parent.h / length
        item.size = (parent.w, bottom_size)
        if count:
            pack_modes = self._pack_modes[parent.instance_name]
            bottom_objects = (objects[name] for name in pack_modes["bottom"][:count])            
            item.y = parent.y + parent.h - sum(item.h or min(bottom_size, item.h_range[1]) for 
                                               item in bottom_objects)
            if count == length - 1:
                top_objects = [objects[name] for name in pack_modes["top"]]
                top_size = parent.h / len(top_objects)
                item.h = parent.y - sum(item.h or min(top_size, item.h_range[1]) for item in top_objects)
        else:
            item.y = parent.y + parent.h - item.h         
        item.x = parent.x
                
    def pack_right(self, parent, item, count, length):  
        pack_modes = self._pack_modes[parent.instance_name]
        left_objects = [objects[name] for name in pack_modes["left"]]
        bottom_objects = [objects[name] for name in pack_modes["bottom"]]
        top_objects = [objects[name] for name in pack_modes["top"]]
        height_spacing = parent.h / (len(top_objects) + len(bottom_objects) or 1)
        item_height = parent.h - sum(item.h or min(height_spacing, item.h_range[1]) for item in bottom_objects)
        if left_objects:
            left_unit = parent.w / len(left_objects)
            required_space = lambda item: item.w or min(left_unit, item.w_range[1])
            left_size = sum(required_space(item) for item in left_objects)        
            if count == length - 1:                
                item.size = (parent.w - left_size, item_height)
        #      print "Set item size: ", item, item.size, parent.w
#                assert item.w, (item, item.size, parent.w / length, parent.h, sum(($item._pack_width for item in self._pack_modes[parent.instance_name]["left"])))
        else:
            item.size = (parent.w / length, item_height)
            left_size = 0
            
        right_objects = (objects[name] for name in self._pack_modes[parent.instance_name]["right"][:count + 1])
        right_unit = (parent.w - left_size) / length
        required_space = lambda item: item.w or min(right_unit, item.w_range[1])
        item.x = parent.x + parent.w - sum(required_space(item) for item in right_objects)        
        item.y = parent.y + sum(_item.h or min(height_spacing, _item.h_range[1]) for _item in top_objects if
                                _item.x > item.x and _item.x <= item.x + item.w)
        item.z = parent.z + 1
                
    def pack_drop_down_menu(self, parent, item, count, length): 
        SCREEN_SIZE = pride.gui.SCREEN_SIZE
        item.area = (parent.x, parent.y + parent.h,
                     SCREEN_SIZE[0] / 5, min(120, SCREEN_SIZE[1] / length))
        item.z = parent.z + 1
        
        
        
class Window_Object(pride.gui.shapes.Bounded_Shape):

    defaults = {'x' : 0, 'y' : 0, 'z' : 0, "size" : (0, 0),
                "texture_size" : pride.gui.SCREEN_SIZE,
                "background_color" : (0, 0, 0, 0), #(25, 125, 225, 125),
                "color" : (15, 165, 25, 255), "text_color" : (15, 165, 25, 255),
                "held" : False, "allow_text_edit" : False,
                "_ignore_click" : False, "hidden" : False, "movable" : True, 
                "texture" : None, "text" : '', "pack_mode" : '' ,      
                "sdl_window" : "->Python->SDL_Window",
                "scroll_bars_enabled" : False, "_scroll_bar_h" : None,
                "_scroll_bar_w" : None}    
        
    flags = {"x_range" : (0, MAX_W), "y_range" : (0, MAX_H), "z_range" : (0, pride.gui.MAX_LAYER),
             "scale_to_text" : False, "_texture_invalid" : False,
             "_layer_index" : 0, "_texture_window_x" : 0, "_texture_window_y" : 0,
             "sdl_window" : "->Python->SDL_Window", "_text" : '', "_pack_mode" : ''}.items()
    
    mutable_defaults = {"children" : list, "draw_queue" : list, "_draw_operations" : list,
                        "pack_count" : dict}
    verbosity = {"texture_resized" : "vvv", "press" : "vv", "release" : "vv"} 
    
    Hotkeys = {}
    
    def _get_texture_invalid(self):
        return self._texture_invalid
    def _set_texture_invalid(self, value):
        if not self._texture_invalid and value:
            objects[self.sdl_window].invalidate_layer(self.z)
        self._texture_invalid = value
    texture_invalid = property(_get_texture_invalid, _set_texture_invalid)
    
    def _on_set(self, coordinate, value):
        if not self.texture_invalid and coordinate in ('x', 'y', 'w', 'h', 'r', 'g', 'b', 'a'):
            self.texture_invalid = True           
        super(Window_Object, self)._on_set(coordinate, value)
                                                                 
    def _set_z(self, value):
        objects[self.sdl_window].set_layer(self, value)
        super(Window_Object, self)._set_z(value)
    z = property(pride.gui.shapes.Bounded_Shape._get_z, _set_z)
    
    def _get_text(self):
        return self._text
    def _set_text(self, value):
        if self.text_entry:
            self.text_entry(value)
        else:
            self._text = value
        if value and self.scale_to_text:
            w, h = objects[self.sdl_window].renderer._get_text_size(self.area, value)
            w += 2
            self.w_range = (0, w)
            self.w = w            
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
        self._texture_window_x = value#max(self.x_range[0], min(value, self.w))
        self.texture_invalid = True
    texture_window_x = property(_get_texture_window_x, _set_texture_window_x)
    
    def _get_texture_window_y(self):
        return self._texture_window_y
    def _set_texture_window_y(self, value):
        self._texture_window_y = value#max(self.y_range[0], min(value, self.h))
        self.texture_invalid = True
    texture_window_y = property(_get_texture_window_y, _set_texture_window_y)
    
    def _get_pack_mode(self):      
        return self._pack_mode
    def _set_pack_mode(self, value):
        self._pack_mode = value
        objects[self.sdl_window + "->Organizer"].set_pack_mode(self.instance_name, value)
    pack_mode = property(_get_pack_mode, _set_pack_mode)
    
    def _get_parent_application(self):
        result = None
        instance = self
        while not result:
            if isinstance(instance, Application):
                result = instance
            else:
                try:
                    instance = instance.parent
                except AttributeError:
                    raise ValueError("Unable to find parent application of {}".format(self))
        return result
    parent_application = property(_get_parent_application)
        
    def __init__(self, **kwargs):               
        super(Window_Object, self).__init__(**kwargs)        
        self.texture_window_x = self.texture_window_y = 0
        self.texture = create_texture(self.texture_size)
        self.texture_invalid = True
        
    def create(self, *args, **kwargs):
        kwargs["z"] = kwargs.get('z') or self.z + 1
        return super(Window_Object, self).create(*args, **kwargs)
                
    def add(self, instance):
        if hasattr(instance, "pack"):
            self.children.append(instance)
        super(Window_Object, self).add(instance)

    def remove(self, instance):
        if instance in self.children:
            self.children.remove(instance)            
        super(Window_Object, self).remove(instance)
        
    def press(self, mouse):
        self.alert("Pressing", level=self.verbosity["press"])
        self.held = True
        for instance in self.children:
            instance.held = True        

    def release(self, mouse):
        self.alert("Releasing", level=self.verbosity["release"])
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
                mouse_position = objects[self.sdl_window].get_mouse_position()            
                if not pride.gui.point_in_area(self.parent.area, mouse_position):
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
    
    text_entry = None
    #def text_entry(self, value):
    #    pass
        
    def toggle_hidden(self):
        if not self.hidden:
            sdl_user_input = pride.objects[self.sdl_window + "->SDL_User_Input"]
            sdl_user_input._update_coordinates(self.instance_name,
                                               self.area, -1)            
        self.hidden = not self.hidden
       
    def draw(self, figure, *args, **kwargs):
        """ Draws the specified figure on self. figure can be any shape supported
            by the renderer, namely: "rect", "line", "point", "text", and "rect_width".
            The first argument(s) will include the destination of the shape in the
            form appropriate for the figure specified (i.e. an area for a rect, a
            pair of points for a point). For a full list of arguments for a 
            particular figure, see the appropriate draw method of the renderer. """
        # draw operations are enqueued and processed in batches by Renderer.draw
        self._draw_operations.append((figure, args, kwargs))
                                                               
    def _draw_texture(self):
        self.draw_texture()  
        objects[self.sdl_window + "->Renderer"].draw(self.texture.texture, self._draw_operations)
        self._draw_operations = []
        self.texture_invalid = False            
        return self.texture.texture
        
    def draw_texture(self):
        area = self.area
        self.draw("fill", area, color=self.background_color)
        self.draw("rect", area, color=self.color)
        if self.text:
            self.draw("text", area, self.text, 
                      bg_color=self.background_color, color=self.text_color)
        
    def pack(self, modifiers=None):
        organizer = objects[self.sdl_window + "->Organizer"]
        organizer.pack(self)
        if modifiers:
            for attribute, value in modifiers.items():
                setattr(self, attribute, value)
        
        for item in self.children:
            item.pack()
        try:
            pack_modes = organizer._pack_modes[self.instance_name]
        except KeyError:
            pass
        else:
            total_height = sum((objects[name].h for name in pack_modes["top"] + pack_modes["bottom"]))
            total_width = sum((objects[name].w for name in pack_modes["right"] + pack_modes["left"]))
            if total_height > self.h:
                if total_width > self.w:
                    self.texture_size = (total_width, total_height)
                else:
                    self.texture_size = (self.texture_size[0], total_height)
                self.texture = create_texture(self.texture_size)
                self.alert("Resized texture to: {}".format(self.texture_size), level=0)
            elif total_width > self.w:
                self.texture_size = (total_width, self.texture_size[1])
                
            if self.scroll_bars_enabled:
                excess_height = total_height > self.h
                excess_width = total_width > self.w
                if not self._scroll_bar_h:
                    if excess_height:
                        bar = self.create("pride.gui.widgetlibrary.Scroll_Bar", pack_mode="right",
                                        target=(self.instance_name, "texture_window_y"))
                        self._scroll_bar_h = bar.instance_name
                        bar.pack()
                elif not excess_height:
                    objects[self._scroll_bar_h].delete()
                    self._scroll_bar_h = None
                    
                if not self._scroll_bar_w:
                    if excess_width:
                        bar = self.create("pride.gui.widgetlibrary.Scroll_Bar",
                                        pack_mode="bottom", target=(self.instance_name,
                                                                    "texture_window_x"))
                        self._scroll_bar_w = bar.instance_name
                        bar.pack()
                elif not excess_width:
                    objects[self._scroll_bar_w].delete()
                    self._scroll_bar_w = None
                
    def delete(self):
        self.pack_mode = None # clear Organizer cache
        super(Window_Object, self).delete()
        objects[self.sdl_window].remove_from_layer(self, self.z)
        objects[self.sdl_window + "->SDL_User_Input"]._remove_from_coordinates(self.instance_name) 
        self.texture_invalid = True
        
        
class Window(Window_Object):

    defaults = {"pack_mode" : "z", "size" : pride.gui.SCREEN_SIZE}

    
class Container(Window_Object):

    defaults = {"pack_mode" : "top"}


class Button(Window_Object):

    defaults = {"shape" : "rect", "pack_mode" : "top"}


class Application(Window):
    
    defaults = {"startup_components" : ("pride.gui.widgetlibrary.Task_Bar", )}
    