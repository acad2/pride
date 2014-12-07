import ctypes

import sdl2
import sdl2.ext
sdl2.ext.init()

import base
import utilities
import defaults
Event = base.Event
                   
    
class Display(base.Hardware_Device):
                    
    defaults = defaults.Display
    
    def __init__(self, **kwargs):
        self.draw_queue = []
        self.window_info = {}
        super(Display, self).__init__(**kwargs)
        self.latency = utilities.Latency(name="framerate")
                  
        for window_options in self.windows:
            window = self.create("sdllibrary.Window", **window_options) 
            renderer = window.create("sdllibrary.Renderer", window=window)
            sprite_factory = renderer.create("sdllibrary.Sprite_Factory", renderer=renderer)
            font_manager = window.create("sdllibrary.Font_Manager")
            
            self.window_info[window] = {"renderer" : renderer.instance_name,
                                        "sprite_factory" : sprite_factory.instance_name,
                                        "font_manager" : font_manager.instance_name}
            Event("World", "add_system", renderer).post()
        Event(self.instance_name, "run").post()
        
    def run(self):
        self.world.process()
        
        Event(self.instance_name, "run", component=self).post()
        
    def _draw(self, item):
        pass
   
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
  

class SDL_Component(base.Wrapper):
    
    defaults = defaults.SDL_Component
    
    def __init__(self, sdl_component, **kwargs):
        super(SDL_Component, self).__init__(sdl_component, **kwargs)

        
class World(SDL_Component):
            
    defaults = defaults.World
    
    def __init__(self, **kwargs):
        world = sdl2.ext.World()
        super(World, self).__init__(world, **kwargs)
        for display_options in self.displays:
            display = self.create(Display, **display_options)

            
class Window(SDL_Component):
            
    defaults = defaults.SDL_Window
    
    def __init__(self, **kwargs):        
        super(Window, self).__init__(**kwargs)
        window = sdl2.ext.Window(self.name, size=self.size)
        self.wraps(window)
        self.renderer = sdl2.ext.Renderer(window)
                
        if self.showing:
            self.show()
            
    def refresh(self):
        self.refresh()
        
        
class Renderer(SDL_Component):
               
    defaults = defaults.Renderer
    
    def __init__(self, **kwargs):
        super(Renderer, self).__init__(**kwargs)
        self.renderer = sdl2.ext.Renderer(self.window.window)
    
    def process(self):
        pass
        
        
class Sprite_Factory(SDL_Component):
                
    defaults = defaults.Sprite_Factory

    def __init__(self, **kwargs):
        super(Sprite_Factory, self).__init__(**kwargs)
        self.factory = sdl2.ext.SpriteFactory(renderer=self.renderer)
        
        
class Font_Manager(SDL_Component):
    
    defaults = defaults.Font_Manager

    def __init__(self, **kwargs):
        super(Font_Manager, self).__init__(**kwargs)
        options = {"font_path" : self.font_path,
                   "size" : self.default_font_size}
        self.font_manager = sdl2.ext.FontManager(**options)
    

class User_Input(base.Process):
    
    defaults = defaults.Process.copy()
    
    def __init__(self, **kwargs):
        super(User_Input, self).__init__(**kwargs)
        #self.modifiers = (sdl2.SDLK_LCTRL, 
        self.event_mapping = {sdl2.SDL_QUIT : self.handle_quit,
                              sdl2.SDL_KEYDOWN : self.handle_keydown,
                              sdl2.SDL_KEYUP : self.handle_keyup}
                              
    def run(self):
        events = sdl2.ext.get_events()
        for event in events:
            self.event_mapping[event.type](event)
            
    def handle_quit(self, event):
        pass # to do: on exit cleanup
        
    def handle_keydown(self, event):    
        keycode = event.key.keysym.scancode
        modifier = event.mod
        
        print keycode, modifier
        #for buffer in self.buffer_list:
         #   key_code = event.key.keysym.sym
          #  buffer.write(event.key.keysym.sym)
            
    def get_hotkey(self, instance, event):
        if instance is None:
            return None

        hotkey = instance.hotkeys.get((event.key, event.mod))
        if not hotkey:
            try:
                hotkey = self.get_hotkey(getattr(instance, "parent"), event)
            except AttributeError:
                self.warning("could not find hotkey from %s or parent" % instance, "Audit: ")

        return hotkey

    def handle_KEYUP(self, event):
        active_item = self.parent.active_item
        hotkey = self.get_hotkey(active_item, event)
        
        # hotkey will be None if no match was found
        if hotkey:
            hotkey.post()      