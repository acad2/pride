from math import floor, sqrt, ceil

import pride
import pride.base as base
import pride.gui
import pride.gui.shapes
Instruction = pride.Instruction
#objects = pride.objects

import sdl2
import sdl2.ext
SDL_Rect = sdl2.SDL_Rect

R, G, B, A = 0, 80, 255, 30

MAX_W, MAX_H = pride.gui.SCREEN_SIZE
_OPPOSING_SIDE = {"left" : "right", "right" : "left", "top" : "bottom", "bottom" : "top"}

def create_texture(size, access=sdl2.SDL_TEXTUREACCESS_TARGET,
                   factory="/Python/SDL_Window/Renderer/SpriteFactory",
                   renderer="/Python/SDL_Window/Renderer"):
    return objects[factory].create_texture_sprite(objects[renderer].wrapped_object,
                                                  size, access=access)
    
class Organizer(base.Base):
    
    mutable_defaults = {"pack_modes" : dict, "_pack_modes" : dict, "_pack_index" : dict}

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
        parent = pride.objects[instance].parent.reference
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
   #     self.alert("packing: {}, {} {} {}", 
   #               [item, item.area, item.z, item.pack_mode],
   #                level=self.verbosity["packing"])
        reference = item.reference
        pack_mode = self.pack_modes[reference]
        pack = getattr(self, "pack_{0}".format(pack_mode))
        parent = item.parent
        old_size = item.size
        pack(parent, item, self._pack_index[reference], 
             len(self._pack_modes[parent.reference][pack_mode]))
        item.alert("Packed into: {} {}", [item.area, item.z], 
                   level=item.verbosity["packed"])
    
    def pack_main(self, parent, item, count, length):
        item.z = parent.z + 1
        pack_modes = self._pack_modes[parent.reference]
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
        height_of_top = height_of(top)
        
      #  print "Setting: ", item, item_x, width_of(left), item_y, height_of_top, item_w, width_of(right), item_h, (height_of(bottom) + height_of_top)
        item.area = (item_x + width_of(left), item_y + height_of_top, 
                     item_w - width_of(right), item_h - (height_of(bottom) + height_of_top))                         
        
    def pack_left(self, parent, item, count, length):
        item.z = parent.z + 1       
        pack_modes = self._pack_modes[parent.reference]
        space_per_object = parent.w / (length + len(pack_modes["right"]) + len(pack_modes["main"]))        
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
        if count == length - 1 and not self._pack_modes[parent.reference]["main"]:
            item_w = parent.w - item.x # (parent.x + parent.w) - item.x ?
            if pack_modes["right"]:
                right_items = [objects[name] for name in pack_modes["right"]]
                required_space = lambda item: item.w or min(space_per_object, item.w_range[1])
                item_w -= sum(required_space(item) for item in right_items)
            item.size = (max(item_w, 0) or space_per_object, item_height)    
        else:
            item.size = (space_per_object, item_height)             
   
    def pack_top(self, parent, item, count, length):
        item.z = parent.z + 1
      #  assert parent.w, (parent, item)
        top_items = [objects[name] for name in self._pack_modes[parent.reference]["top"][:count]]
        sizing = parent.h / length
        occupied_space = sum(min(top_item.h, top_item.h_range[1]) or min(top_item.h_range[0], sizing) for top_item in top_items)  ## bug hiding right here!        
        if count:                       
            item.y = parent.y + occupied_space
        else:
            item.y = parent.y
        item.x = parent.x
        
        if count == length - 1 and not self._pack_modes[parent.reference]["main"]:
            bottom_objects = [objects[name] for name in self._pack_modes[parent.reference]["bottom"]]
            item_h = (parent.y + parent.h) - item.y         
            if bottom_objects:
                width_spacing = parent.h / len(bottom_objects)
                item_h - sum(bottom_object.h or min(width_spacing, bottom_object.h_range[1]) for
                             bottom_object in bottom_objects)
            item.size = (parent.w, item_h)
        else:
            item.size = (parent.w, (parent.h - occupied_space) / (length - count))  
       # assert item.w, (item.size, item)
            
    def pack_grid(self, parent, item, count, length):
        grid_size = sqrt(length)

        if grid_size != floor(grid_size):
            grid_size = floor(grid_size) + 1
        position = (int(floor((count / grid_size))), int(count % grid_size))

        item.z = parent.z + 1        
        
        pack_modes = self._pack_modes[parent.reference]
        right_objects = [pride.objects[reference] for reference in pack_modes["right"]]
        left_objects = [pride.objects[reference] for reference in pack_modes["left"]]
        main_objects = [pride.objects[reference] for reference in pack_modes["main"]]
        horizontal_spacing = parent.w / ((len(left_objects) + len(right_objects) + len(main_objects)) or 1)
        occupied_left_area =  sum((item.w or min(item.w_range[1], horizontal_spacing) for item in left_objects))
        occupied_right_area = sum((item.w or min(item.w_range[1], horizontal_spacing) for item in right_objects))
        
        top_objects = [pride.objects[reference] for reference in pack_modes["top"]]
        bottom_objects = [pride.objects[reference] for reference in pack_modes["bottom"]]
        vertical_spacing = parent.h / ((len(top_objects) + len(bottom_objects) + len(main_objects)) or 1)
        occupied_top_area = sum((item.h or min(item.h_range[1], vertical_spacing) for item in top_objects))
        occupied_bottom_area = sum((item.h or min(item.h_range[1], vertical_spacing) for item in bottom_objects))
        
        available_width = parent.w - occupied_left_area - occupied_right_area
        available_height = parent.h - occupied_top_area - occupied_bottom_area
        item.size = int(available_width / grid_size), int(available_height / grid_size)
        item.x = (item.w * position[1]) + parent.x + occupied_left_area
        item.y = (item.h * position[0]) + parent.y + occupied_top_area
        
    def pack_z(self, parent, item, count, length):
        item.z = parent.z + 1

    def pack_bottom(self, parent, item, count, length):
        item.z = parent.z + 1       
        assert parent.w
        bottom_size = parent.h / length        
        item.size = (parent.w, bottom_size)
        if count:
            pack_modes = self._pack_modes[parent.reference]
            bottom_objects = (objects[name] for name in pack_modes["bottom"][:count])            
            item.y = parent.y + parent.h - sum(item.h or min(bottom_size, item.h_range[1]) for 
                                               item in bottom_objects)            
            if count == length - 1:
                top_objects = [objects[name] for name in pack_modes["top"]]
                top_size = parent.h / len(top_objects)
                item.h = min(item.h_range[1], parent.h - sum(item.h or min(top_size, item.h_range[1]) for item in top_objects))
    #            print "Adjusted height", item, item.h, item.h_range, parent.h, sum(item.h or min(top_size, item.h_range[1]) for item in top_objects)
        else:
            item.y = parent.y + parent.h - item.h         
        item.x = parent.x
                
    def pack_right(self, parent, item, count, length):  
        pack_modes = self._pack_modes[parent.reference]
        left_objects = [objects[name] for name in pack_modes["left"]]
        bottom_objects = [objects[name] for name in pack_modes["bottom"]]
        top_objects = [objects[name] for name in pack_modes["top"]]
        main_size = sum(objects[item].w for item in pack_modes["main"])
        height_spacing = parent.h / (len(top_objects) + len(bottom_objects) or 1)
        item_height = parent.h - sum(item.h or min(height_spacing, item.h_range[1]) for item in bottom_objects)
        if left_objects:
            left_unit = parent.w / len(left_objects)
            required_space = lambda item: item.w or min(left_unit, item.w_range[1])
            left_size = sum(required_space(item) for item in left_objects) + main_size
            if count == length - 1:                
                item.size = (parent.w - left_size, item_height)
        #      print "Set item size: ", item, item.size, parent.w
#                assert item.w, (item, item.size, parent.w / length, parent.h, sum(($item._pack_width for item in self._pack_modes[parent.reference]["left"])))
        else:
            item.size = (parent.w / length, item_height)
            left_size = 0
            
        right_objects = (objects[name] for name in self._pack_modes[parent.reference]["right"][:count + 1])
        available_w = parent.w - left_size - main_size
        right_unit = available_w / length
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
        
    def pack_popup_menu(self, parent, item, count, length):        
        item.z = max(pride.objects[item.sdl_window + "/SDL_User_Input"]._coordinate_tracker.keys())
        w, h = pride.gui.SCREEN_SIZE
        item.position = (w / 4, h / 4)                         
        
        
class Theme(pride.base.Wrapper):
    
    def draw_texture(self):
        raise NotImplementedError
        
        
class Minimal_Theme(Theme):
            
    def draw_texture(self):
        area = self.area
        self.draw("fill", area, color=self.background_color)
        self.draw("rect_width", area, color=self.color, width=self.outline_width)        
        if self.text:
            width = self.w if self.wrap_text else None
            assert width is not None, (self, width, self.w, self.wrap_text, self.text)
            self.draw("text", area, self.text, width=self.w if self.wrap_text else None,
                      bg_color=self.background_color, color=self.text_color)

                                
class Window_Object(pride.gui.shapes.Bounded_Shape):

    defaults = {'x' : 0, 'y' : 0, 'z' : 0, "size" : (0, 0),
                "texture_size" : pride.gui.SCREEN_SIZE, "outline_width" : 1,
                "background_color" : (0, 0, 0, 0), #(25, 125, 225, 125),
                "color" : (15, 165, 25, 255), "text_color" : (15, 165, 25, 255),
                "held" : False, "allow_text_edit" : False, "wrap_text" : True,
                "_ignore_click" : False, "hidden" : False, "movable" : False, 
                "texture" : None, "text" : '', "pack_mode" : '' ,      
                "sdl_window" : '', "scroll_bars_enabled" : False, 
                "_scroll_bar_h" : None, "_scroll_bar_w" : None,
                "theme_type" : "pride.gui.gui.Minimal_Theme"}    
        
    flags = {"scale_to_text" : False, "_texture_invalid" : False,
             "_texture_window_x" : 0, "_texture_window_y" : 0,
             "_text" : '', "_pack_mode" : '', "_sdl_window" : ''}
    
    mutable_defaults = {"_draw_operations" : list, "pack_count" : dict, "_children" : list}
    verbosity = {"texture_resized" : "vvv", "press" : "vv", "release" : "vv", "packed" : "packed"} 
    
    hotkeys = {("\b", None) : "handle_backspace", ("\n", None) : "handle_return"}
    
    def _get_texture_invalid(self):
        return self._texture_invalid
    def _set_texture_invalid(self, value):
        if not self._texture_invalid and value:
            assert self.sdl_window
            objects[self.sdl_window].invalidate_object(self)
        self._texture_invalid = value
    texture_invalid = property(_get_texture_invalid, _set_texture_invalid)
    
    def _on_set(self, coordinate, value):
        if not self.texture_invalid and coordinate in ('z', 'x', 'y', 'w', 'h', 'r', 'g', 'b', 'a'):
            self.texture_invalid = True           
        super(Window_Object, self)._on_set(coordinate, value)
                                                                 
    def _get_text(self):
        return self._text
    def _set_text(self, value):
        self._text = value
        if value and self.scale_to_text:
            assert self.sdl_window
            w, h = objects[self.sdl_window].renderer.get_text_size(self.area, value)
            w += 2
            self.w_range = (0, w)
            self.w = w            
        self.texture_invalid = True
    text = property(_get_text, _set_text)
    
    def _get_bg_color(self):
        return self._background_color
    def _set_bg_color(self, color):
        self.texture_invalid = True
        self._background_color = color if self.transparency_enabled else color[:3] + (255, )#sdl2.ext.Color(*color)
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
        self._text_color = colors#sdl2.ext.Color(*colors)
        self.texture_invalid = True
    text_color = property(_get_text_color, _set_text_color)
    
    def _get_texture_window_x(self):
        return self._texture_window_x
    def _set_texture_window_x(self, value):
        self._texture_window_x = value
        self.texture_invalid = True
    texture_window_x = property(_get_texture_window_x, _set_texture_window_x)
    
    def _get_texture_window_y(self):
        return self._texture_window_y
    def _set_texture_window_y(self, value):
        self._texture_window_y = value
        self.texture_invalid = True
    texture_window_y = property(_get_texture_window_y, _set_texture_window_y)
    
    def _get_pack_mode(self):      
        return self._pack_mode
    def _set_pack_mode(self, value):
        self._pack_mode = value
        objects[(self.sdl_window  or self.parent.sdl_window)+ "/Organizer"].set_pack_mode(self.reference, value)
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
        
    def _get_children(self):
        return self._children
    def _set_children(self, value):
        self._children = value
    children = property(_get_children, _set_children)
    
    def _get_sdl_window(self):
        return (self._sdl_window or getattr(self.parent, "sdl_window", self.parent_name))
    def _set_sdl_window(self, value):
        self._sdl_window = value
    sdl_window = property(_get_sdl_window, _set_sdl_window)
    
    def __init__(self, **kwargs):               
        super(Window_Object, self).__init__(**kwargs)       
        self.texture_window_x = self.texture_window_y = 0
        self.texture = None
        self.texture_invalid = True
        
        self.theme = self.create(self.theme_type, wrapped_object=self)
        self._children.remove(self.theme)
        pride.objects[self.sdl_window + "/SDL_User_Input"]._update_coordinates(self.reference, self.area, self.z)
        
    def create(self, *args, **kwargs):
        kwargs.setdefault('z', self.z + 1)
        kwargs.setdefault("sdl_window", self.sdl_window)
        return super(Window_Object, self).create(*args, **kwargs)
        
    def add(self, _object):
        self._children.append(_object)
        super(Window_Object, self).add(_object)
        
    def remove(self, _object):
        try:
            self._children.remove(_object)
        except ValueError:
            if _object is not self.theme:
                raise
        super(Window_Object, self).remove(_object)
        
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
                parent = self.parent
                if not pride.gui.point_in_area(parent.area, mouse_position):
                    if self in parent.children:
                    #    self.parent.alert("Removing {}; {} not in {}", [self, objects["SDL_Window"].get_mouse_position(), self.parent.area], level=0)
                        parent.remove(self)                    
                        parent.pack({"position" : parent.position})
                        self.z -= 1
                elif self not in parent.children: 
                 #   self.parent.alert("Adding {}", [self], level=0)
                    parent.add(self)
                    parent.pack({"position" : parent.position})
                    #self.held = False                    
            x_difference = self.x - _x
            y_difference = self.y - _y
            for instance in self.children:
                instance.held = True
                instance.mousemotion(x_difference, y_difference, top_level=False)
                instance.held = False
            
    def toggle_hidden(self):
        if not self.hidden:
            sdl_user_input = pride.objects[self.sdl_window + "/SDL_User_Input"]
            sdl_user_input._update_coordinates(self.reference,
                                               self.area, -1)            
        self.hidden = not self.hidden
       
    def draw(self, figure, *args, **kwargs):
        """ Draws the specified figure on self. figure can be any shape supported
            by the renderer, namely: "rect", "line", "point", "text", and "rect_width".
            The first argument(s) will include the destination of the shape in the
            form appropriate for the figure specified (i.e. an area for a rect, a
            pair of points for a point). For a full list of arguments for a 
            particular figure, see the appropriate draw method of the renderer. """
        # draw operations are enqueued and processed in batches by the Renderer
        self._draw_operations.append((figure, args, kwargs))
                                                               
    def _draw_texture(self):    
        if self.hidden:
            return []
        pride.objects[self.sdl_window + "/SDL_User_Input"]._update_coordinates(self.reference, self.area, self.z)
        self.draw_texture()
        instructions = self._draw_operations[:]

        for child in self.children:
            instructions.extend(child._draw_texture())
            
        if self._texture_window_x or self._texture_window_y:
            x, y, w, h = self.area
            source_rect = (x + self.texture_window_x,
                           y + self.texture_window_y, w, h)  
            
            if x + w > MAX_W:
                w = MAX_W - x
            if y + h > MAX_H:
                h = MAX_H - y
            destination = (x, y, w, h)        
          #  assert destination == self.area
            instructions.append(("copy", (objects[self.sdl_window]._texture.texture, source_rect, destination), {}))
            
            # less readable, less code though, need to find way to do this automagically            
            #instructions.append(("copy", (self.texture.texture,
            #                              (x + self.texture_window_x, y + self.texture_window_y, w, h), 
            #                              (x, y, MAX_W - x if x + w > MAX_W else w,
            #                                     MAX_H - y if y + h > MAX_H else h)), 
            #                     {})) # empty kwargs
                                          
        self.texture_invalid = False
        del self._draw_operations[:]
        return instructions
        
    def draw_texture(self):
        self.theme.draw_texture()
        
    def pack(self, modifiers=None):        
        organizer = objects[self.sdl_window + "/Organizer"]
        organizer.pack(self)
        if modifiers:
            for attribute, value in modifiers.items():
                setattr(self, attribute, value)
        
        for item in self.children:
            item.pack()
        try:
            pack_modes = organizer._pack_modes[self.reference]
        except KeyError:
            pass
        else:
            total_height = sum((objects[name].h for name in pack_modes["top"] + pack_modes["bottom"]))
            total_width = sum((objects[name].w for name in pack_modes["right"] + pack_modes["left"]))
         #   if total_height > self.h:
         #       if total_width > self.w:
         #           self.texture_size = (total_width, total_height)
         #       else:
         #           self.texture_size = (self.texture_size[0], total_height)
         #       self.texture = create_texture(self.texture_size)
         #       self.alert("Resized texture to: {}".format(self.texture_size), level=0)
         #   elif total_width > self.w:
         #       self.texture_size = (total_width, self.texture_size[1])
                
            if self.scroll_bars_enabled:
                excess_height = total_height > self.h
                excess_width = total_width > self.w
                if not self._scroll_bar_h:
                    if excess_height:
                        bar = self.create("pride.gui.widgetlibrary.Scroll_Bar", pack_mode="right",
                                        target=(self.reference, "texture_window_y"))
                        self._scroll_bar_h = bar.reference
                        bar.pack()
                elif not excess_height:
                    objects[self._scroll_bar_h].delete()
                    self._scroll_bar_h = None
                    
                if not self._scroll_bar_w:
                    if excess_width:
                        bar = self.create("pride.gui.widgetlibrary.Scroll_Bar",
                                        pack_mode="bottom", target=(self.reference,
                                                                    "texture_window_x"))
                        self._scroll_bar_w = bar.reference
                        bar.pack()
                elif not excess_width:
                    objects[self._scroll_bar_w].delete()
                    self._scroll_bar_w = None
                
    def delete(self):
        self.pack_mode = None # clear Organizer cache        
        objects[self.sdl_window + "/SDL_User_Input"]._remove_from_coordinates(self.reference) 
        self.texture_invalid = True
        self.theme.delete()
        super(Window_Object, self).delete()                
                
    def deselect(self, mouse, next_active_object):
        pass
        
    def select(self, mouse):
        pass    
    
    def text_entry(self, text):
        if self.allow_text_edit:
            self.text += text        
        
    def handle_return(self):
        pass
        
    def handle_backspace(self):
        if self.allow_text_edit:
            self.text = self.text[:-1]
        
class Window(Window_Object):

    defaults = {"pack_mode" : "main", "size" : pride.gui.SCREEN_SIZE}

    
class Container(Window_Object):

    defaults = {"pack_mode" : "top"}


class Button(Window_Object):

    defaults = {"shape" : "rect", "pack_mode" : "top"}


class Application(Window):
    
    defaults = {"startup_components" : ("pride.gui.widgetlibrary.Task_Bar", 
                                        "pride.gui.gui.Window")}
    flags = {"transparency_enabled" : False}
    
    def _get_application_window(self):  
        try:
            return self.objects["Window"][0]
        except KeyError:
            print self, self.objects.keys()
            raise
    application_window = property(_get_application_window)
    
    def draw_texture(self):
        assert not self.deleted
        super(Application, self).draw_texture()
        self.application_window.texture_invalid = True
        