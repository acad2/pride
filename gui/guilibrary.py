import heapq
import ctypes
from operator import attrgetter
from sys import modules

import base
import defaults
import utilities
Event = base.Event

import sdl2
import sdl2.ext


R, G, B, A = 0, 80, 255, 30
dark_color_scalar = .5
light_color_scalar = 1.5


# provides the pack() functionality
class Organizer(base.Process):
    """a component to adjust the position/size of gui objects, either by pre defined
    pack modes or an attribute-setting pack_modifier attribute.
    
    usage: self.create("guilibrary.Organizer") or
    Event("organizer", "pack", self).post()"""
    def __init__(self, *args, **kwargs):
        super(Organizer, self).__init__(*args, **kwargs)
        self.queue = []
        self.display = self.parent.objects["Display"][0]
        self.running = False
        
    def pack(self, item):
        """called to schedule an item to be packed for display graphically.
        resolves the item to a display wrapper and places it in the queue."""
        try:
            display_wrapper = self.display.Display_Wrappers[item]
        except KeyError:
            display_wrapper = self.display.create(Display_Wrapper, item)
            self.display.Display_Wrappers[item] = display_wrapper
        finally:
            self.queue.put(display_wrapper)
            if not self.running:
                self.running = True
                Event("Organizer", "run").post()
            
    def _pack(self, packed_object):
        wrapped_object = super(type(packed_object), packed_object).__getattribute__("wrapped_object")
        pack_mode = packed_object.pack_mode
        try:
            parent = Display.Display_Wrappers[wrapped_object.parent_weakref()]
        except KeyError:
            parent = self.display
        # a list of all the siblings that have the same pack mode
        siblings = [item for item in parent.get_children() if (getattr(item, "pack_mode", None) == pack_mode)]
        length = len(siblings)
        call = Organizer.call_switch.get(pack_mode)

        try:
            count = siblings.index(wrapped_object)
        except ValueError:
            count = siblings.index(packed_object)
        if call:
            call(parent, packed_object, count, length)
            modifier = getattr(packed_object, "pack_modifier", None)
            if modifier:
                modifier(parent, packed_object)
            
    def run(self):
        while not self.queue.empty():
            self._pack(self.queue.get_nowait())
        self.running = False
        
    # self will be the calling_object supplied to __call__
    # not the organizer object
    def pack_horizontal(self, child, count, length):
        child.layer = self.layer + 1
        child.size = (self.size[0]/length, self.size[1])
        child.x = (child.size[0]*count)+self.x
        child.y = self.y

        if child.size != child.surface.get_size():
            child.surface = sdl2.SDL_Surface(size=child.size)

    def pack_vertical(self, child, count, length):
        child.layer = self.layer + 1
        child.size = (self.size[0], self.size[1]/length)
        child.y = (child.size[1]*count)+self.y
        child.x = self.x

        if child.size != child.surface.get_size():
            child.surface = sdl2.SDL_Surface(size=child.size)

    def pack_grid(self, child, count, length):
        grid_size = sqrt(length)

        if grid_size != floor(grid_size):
            grid_size = floor(grid_size)+1

        position = (int(floor((count / grid_size))), (count % grid_size))

        child.layer = self.layer + 1
        child.size = int(self.size[0]/grid_size), int(self.size[1]/grid_size)
        child.x = (child.size[0]*position[1])+self.x
        child.y = (child.size[1]*position[0])+self.y

        if child.size != child.surface.get_size():
            child.surface = sdl2.SDL_Surface(size=child.size)

    def pack_text(self, child, count, length):
        child.layer = self.layer + 1
        child.x = self.x + self.x_width + self.x_spacing
        child.y = self.y
        
    def pack_menu_bar(self, child, count, length):
        child.layer = self.layer + 1
        child.x = self.x
        child.y = self.y
        child.size = (self.size[0], int(self.size[1]*.03))

        if child.size != child.surface.get_size():
            child.surface = sdl2.SDL_Surface(size=child.size)

    def pack_layer(self, child, count, length):
        try:
            child.layer = self.layer+count
        except AttributeError:
            child.layer = count
            
    def pack_None(self, child, count, length):
        child.layer = self.layer + 1

    def center(self, child):
        child.x = Display.SCREEN_SIZE[0]/2
        child.y = Display.SCREEN_SIZE[1]/2

    call_switch = {'horizontal' : pack_horizontal, \
    'vertical' : pack_vertical, \
    'grid' : pack_grid, \
    'text' : pack_text, \
    'menu_bar' : pack_menu_bar, \
    "layer" : pack_layer, \
    None : pack_None}


class Display(base.Hardware_Device):

    # new instance default values
    defaults = defaults.Display
    
    def _get_position(self):
        return (self.x, self.y)
    def _set_position(self, position):
        self.x, self.y = position
    position = property(_get_position, _set_position)

    def _get_area(self):
        return (self.position, self.size)
    def _set_area(self, rect):
        self.position, self.size = rect
    area = property(_get_area, _set_area)
    
    def __init__(self, *args, **kwargs):
        super(Display, self).__init__(*args, **kwargs)
        self.popups = []
        self.under_mouse = []
        self.draw_buffer = {}
        self.surface_cache = {}
        self.draw_queue = []
        self.active_item = None
        self.objects["Display_Wrapper"] = []
        # creates the OS level window that everything will be inside
        self.surface = sdl2.ext.Window(self.name, self.size)    
        self.surface.show()
        Event(self.instance_name, "run", component=self).post()
        
    def add_popup(self, instance):
        self.popups.append(instance)
        
    def set_active_item(self, instance):
        self.active_item = instance
        
    def delete(self, *args):
        super(Display, self).delete(*args)
        for instance in args:
            if type(instance) != Display_Wrapper:
                del self.objects["Display_Wrapper"][instance]
            
    def run(self):       
        print self.get_mouse_state()
        Event(self.instance_name, "run", component=self).post()
        """for item in self.draw_queue:
            #surface = self.surface_cache[item]
            sdl2.SDL_Blit(self.surface, (item.position))
        self.surface.update()  """           
            
    def draw(self, item):
        heapq.heappush(item, self.draw_queue)
        """ try:
            item = self.Display_Wrappers[item]           
        except KeyError:
            self.Display_Wrappers[item] = self.create(Display_Wrapper, item)
            item = self.Display_Wrappers[item]
        finally:
            if item.layer > self.max_layer:
                self.max_layer = item.layer
            self.surface_cache[item] = self._draw(item)            
            if not self.running:
                self.running = True
                Event("Display", "run").post()"""
                
    def _draw(self, item):
        if hasattr(item, "_draw"):
            try:
                return item._draw()
            except:
                self.warning("%s._draw() failed, using default. %s may have a bug" % (item, item))
                raise
    
    def get_mouse_state(self):
        x = ctypes.c_long(0)
        y = ctypes.c_long(0)
        buttons = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))        
        
        states = ("BUTTON_LMASK", "BUTTON_RMASK", "BUTTON_MMASK", "BUTTON_X1MASK", "BUTTON_X2MASK")
        states = (getattr(sdl2.mouse, "SDL_{0}".format(state)) for state in states)
        button_state = map(lambda mask: buttons & mask, states)
        return ((x, y), button_state)
     
    def get_mouse_position(self):
        return self.get_mouse_state[0]
        
    @staticmethod
    def mouse_is_inside(instance):
        mouse_pos_x, mouse_pos_y = self.get_mouse_position()

        if mouse_pos_x >= int(instance.x) and mouse_pos_x <= int(instance.x)+instance.size[0]:
            if mouse_pos_y >= int(instance.y) and mouse_pos_y <= int(instance.y)+instance.size[1]:
                return True
      
        
class Gui_Object(base.Base):

    # default values
    defaults = defaults.Gui_Object
    Hotkeys = {}
    # enables reference to self.position, referring to the objects x+y at once
    def _get_position(self):
        return (self.x, self.y)
    def _set_position(self, position):
        self.x, self.y = position
    position = property(_get_position, _set_position)

    # enables reference to self.area, which returns the objects x+y coords and size
    def _get_area(self):
        return (self.position, self.size)
    def _set_area(self, rect):
        self.position, self.size = rect
    area = property(_get_area, _set_area)

    # calculates the outline color
    def _get_outline_color(self):
        return (int(self.color[0]*self.color_scalar), int(self.color[1]*\
        self.color_scalar), int(self.color[2]*self.color_scalar))
        
    outline_color = property(_get_outline_color)
    
    def __init__(self, *args, **kwargs):
        # assign default attributes
        super(Gui_Object, self).__init__(*args, **kwargs)
        # derived attributes
        self.surface = sdl2.SDL_Surface(size=self.size)
        Event("Organizer", "pack", self).post()
        Event("Display", "draw", self).post()
        
    def _draw(self):
        draw_order = []
        for child in self.get_children():
            heapq.heappush(draw_order)
                
        if hasattr(self, "background"):
            sdl2.SDL_Blit(self.surface, self.background, (0, 0))
        else:
            self.surface.fill(self.color)
            pygame.draw.rect(self.surface, self.outline_color, self.area, self.outline)
        for child in draw_order:
            self.surface.blit(child._draw(), child.position)
                        
        return self.surface
        
    def press(self):
        self.held = True
    
    def release(self):
        self.held = False
        if Display.mouse_is_inside(self):
            self.click()        
        
    def click(self):
        pass
        
# adapter that enables drawing arbitrary objects
class Display_Wrapper(base.Wrapper):
    """adatper that enables drawing arbitrary objects while preserving original
    functionality. essentially  a wrapper with Gui_Object attributes. for more
    extensive documentation, refer to those."""
    defaults = defaults.Gui_Object
    
    def _get_position(self):
        return (self.x, self.y)
    def _set_position(self, position):
        self.x, self.y = position
    position = property(_get_position, _set_position)

    def _get_area(self):
        return (self.position, self.size)
    def _set_area(self, rect):
        self.position, self.size = rect
    area = property(_get_area, _set_area)   
    
    def _get_outline_color(self):
        return (int(self.color[0]*self.color_scalar), int(self.color[1]*\
        self.color_scalar), int(self.color[2]*self.color_scalar))
    outline_color = property(_get_outline_color)
    
    def __init__(self, wrapped_object, *args, **kwargs):
        super(Display_Wrapper, self).__init__(wrapped_object, *args, **kwargs)
        self.surface = pygame.Surface((self.size), pygame.SRCALPHA, 32)
        Event("Organizer", "pack", wrapped_object).post()
        Event("Display", "draw", wrapped_object).post()
        
    def press(self):
        self.held = True
    
    def release(self):
        self.held = False
        if Display.mouse_is_inside(self):
            self.click()        
        
    def click(self):
        pass               
        
    def __del__(self):
        Event("Display", "delete", self.wrapped_object).post()       
    
        
class Window(Gui_Object):

    defaults = defaults.Window
    
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        if getattr(self, "title_bar", None):
            self.create("widgetlibrary.Title_Bar")


class Container(Gui_Object):

    defaults = defaults.Container

    def __init__(self, *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)


class Button(Gui_Object):

    defaults = defaults.Button

    def __init__(self, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)
        self.font = pygame.font.SysFont(*self.typeface)

                
class Gui_Object(base.Base):

    # default values
    defaults = defaults.Gui_Object
    Hotkeys = {}
     
    def _get_position(self):
        return (self.x, self.y)
    def _set_position(self, position):
        self.x, self.y = position
    position = property(_get_position, _set_position)

    def _get_area(self):
        return (self.position, self.size)
    def _set_area(self, rect):
        self.position, self.size = rect
    area = property(_get_area, _set_area)

    # calculates the outline color
    def _get_outline_color(self):
        return (int(self.color[0]*self.color_scalar), int(self.color[1]*\
        self.color_scalar), int(self.color[2]*self.color_scalar))
        
    outline_color = property(_get_outline_color)
    
    def __init__(self, *args, **kwargs):
        super(Gui_Object, self).__init__(*args, **kwargs)
                
        #Event("Organizer0", "pack", self).post()
        #Event(self.parent_window, "draw", self).post()
        
    def _draw(self):
        draw_order = []
        for child in self.get_children():
            if Gui_Object in type(child).__mro__:
                draw_order.append(child)
        draw_order = sorted(draw_order, key=attrgetter("layer"))
                
        if hasattr(self, "background"):
            self.surface.blit(self.background, (0, 0))
        else:
            self.surface.fill(self.color)
            pygame.draw.rect(self.surface, self.outline_color, self.area, self.outline)
        for child in draw_order:
            self.surface.blit(child._draw(), child.position)
                        
        return self.surface
        
    def press(self):
        self.held = True
    
    def release(self):
        self.held = False
        if Display.mouse_is_inside(self):
            self.click()        
        
    def click(self):
        pass   
   
    
class Window(Gui_Object):
                
    defaults = defaults.Window
    
    def __init__(self, **kwargs):
        super(Window, self).__init__(**kwargs)
        #if self.show_title_bar:
          #  self.create("widgetlibrary.Title_Bar")

class Container(Window):

    defaults = defaults.Container

    def __init__(self, *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)


class Button(Container):

    defaults = defaults.Button

    def __init__(self, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)
        
        self.font = pygame.font.SysFont(*self.typeface)   

        
