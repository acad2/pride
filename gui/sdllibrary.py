import os
import sys
import string
import heapq
import ctypes
import itertools
import operator
import collections
import pprint

import mpre
import mpre.base as base
import mpre.vmlibrary as vmlibrary
import mpre.utilities as utilities
import mpre.gui
Instruction = mpre.Instruction
components = mpre.components

import sdl2
import sdl2.ext
import sdl2.sdlttf
sdl2.ext.init()
sdl2.sdlttf.TTF_Init()
font_module = sdl2.sdlttf

class SDL_Component(base.Proxy):

    defaults = base.Proxy.defaults.copy()


class SDL_Window(SDL_Component):

    defaults = SDL_Component.defaults.copy()
    defaults.update({"size" : mpre.gui.SCREEN_SIZE,
                     "showing" : True,
                     'z' : 0,
                     "name" : "Metapython",
                     "priority" : .04})
    
    def __init__(self, **kwargs):
        self.coordinate_tracker = {}
        self.children = []
        self.layers = collections.OrderedDict((x, []) for x in xrange(100))
        self.latency = utilities.Latency(name="framerate")
        self.running = True
        super(SDL_Window, self).__init__(**kwargs)

        window = sdl2.ext.Window(self.name, size=self.size)
        self.wraps(window)

        renderer = self.renderer = self.create(Renderer, window=self)
        self.user_input = self.create(SDL_User_Input)
        self.run_instruction = Instruction(self.instance_name, "run")
        self.run_instruction.execute(self.priority)
        
        if self.showing:
            self.show()  

    def set_layer(self, instance, value):
        try:
            self.layers[instance.z].remove(instance)
        except ValueError:
            pass
        self.layers[value].append(instance)    
        
    def create(self, *args, **kwargs):
        instance = super(SDL_Window, self).create(*args, **kwargs)
        if hasattr(instance, 'pack'):
            instance.pack()
        return instance
    
    def add(self, instance):
        self.children.append(instance)
        super(SDL_Window, self).add(instance)
        
    def remove(self, instance):
        self.children.remove(instance)
        super(SDL_Window, self).remove(instance)
        
    def run(self):
        renderer = self.renderer
        renderer.set_render_target(None)
        renderer.clear()
     #   raw_input("\nwaiting at loop entry...")
      #  pprint.pprint(self.layers)
        for layer, instances in self.layers.items():
        #    self.alert("Drawing layer: {}", [layer], level=0)
          #  components["Drawing_Surface"].draw(
            for instance in instances:
         #       print "Copying: ", instance
                #if instance.texture_invalid:
                #    print "Updating texture of: ", instance
                texture = (instance._draw_texture() if instance.texture_invalid else 
                           instance.texture)
                renderer.copy(texture, dstrect=instance.area)
            if not self.layers[layer + 1]:
                break
          #  self.layer_cache[layer] = renderer
      #  raw_input("waiting before present...")       
        renderer.present()
        if self.running:
            self.run_instruction.execute(self.priority)
                            
    def get_mouse_state(self):
        mouse = sdl2.mouse
        x = ctypes.c_long(0)
        y = ctypes.c_long(0)
        buttons = mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

        states = ("BUTTON_LMASK", "BUTTON_RMASK", "BUTTON_MMASK", "BUTTON_X1MASK", "BUTTON_X2MASK")
        states = (getattr(mouse, "SDL_{0}".format(state)) for state in states)
        button_state = map(lambda mask: buttons & mask, states)
        return ((x, y), button_state)

    def get_mouse_position(self):
        return self.get_mouse_state()[0]


"""class Font(SDL_Component):

    defaults = defaults.Font

    def __init__(self, **kwargs):
        super(Font, self).__init__(**kwargs)
        self.wraps(font_module.TTF_OpenFont(self.font_path, self.size))"""


class SDL_User_Input(vmlibrary.Process):

    defaults = vmlibrary.Process.defaults.copy()
    
    def __init__(self, **kwargs):
        self.active_item = None
        self.coordinate_tracker = {}
        self.popups = []
        super(SDL_User_Input, self).__init__(**kwargs)
        self.uppercase_modifiers = (sdl2.KMOD_SHIFT, sdl2.KMOD_CAPS,
                                    sdl2.KMOD_LSHIFT, sdl2.KMOD_RSHIFT)
        uppercase = self.uppercase = {'1' : '!',
                                      '2' : '@',
                                      '3' : '#',
                                      '4' : '$',
                                      '5' : '%',
                                      '6' : '^',
                                      '7' : '&',
                                      '8' : '*',
                                      '9' : '(',
                                      '0' : ')',
                                      ";" : ':',
                                      '\'' : '"',
                                      '[' : ']',
                                      ',' : '<',
                                      '.' : '>',
                                      '/' : "?",
                                      '-' : "_",
                                      '=' : "+",
                                      '\\' : "|",
                                      '`' : "~"}
        letters = string.ascii_letters
        for index, character in enumerate(letters[:26]):
            uppercase[character] = letters[index+26]

        # for not yet implemented features
        unhandled = self.handle_unhandled_event

        self.instruction_mapping = {sdl2.SDL_DOLLARGESTURE : unhandled,
                              sdl2.SDL_DROPFILE : unhandled,
                              sdl2.SDL_FINGERMOTION : unhandled,
                              sdl2.SDL_FINGERDOWN : unhandled,
                              sdl2.SDL_FINGERUP : unhandled,
                              sdl2.SDL_FINGERMOTION :unhandled,
                              sdl2.SDL_KEYDOWN : self.handle_keydown,
                              sdl2.SDL_KEYUP : self.handle_keyup,
                              sdl2.SDL_JOYAXISMOTION : unhandled,
                              sdl2.SDL_JOYBALLMOTION : unhandled,
                              sdl2.SDL_JOYHATMOTION : unhandled,
                              sdl2.SDL_JOYBUTTONDOWN : unhandled,
                              sdl2.SDL_JOYBUTTONUP : unhandled,
                              sdl2.SDL_MOUSEMOTION : self.handle_mousemotion,
                              sdl2.SDL_MOUSEBUTTONDOWN : self.handle_mousebuttondown,
                              sdl2.SDL_MOUSEBUTTONUP : self.handle_mousebuttonup,
                              sdl2.SDL_MOUSEWHEEL : self.handle_mousewheel,
                              sdl2.SDL_MULTIGESTURE : unhandled,
                              sdl2.SDL_QUIT : self.handle_quit,
                              sdl2.SDL_SYSWMEVENT : unhandled,
                              sdl2.SDL_TEXTEDITING : unhandled,
                              sdl2.SDL_TEXTINPUT : unhandled,
                              sdl2.SDL_USEREVENT : unhandled,
                              sdl2.SDL_WINDOWEVENT : unhandled}

    def run(self):
        events = sdl2.ext.get_events()
      #  self.run_instruction.execute(self.priority)
        for event in events:
            self.instruction_mapping[event.type](event)        

    def _update_coordinates(self, item, area, z):
        self.coordinate_tracker[item] = (area, z)

    def mouse_is_inside(self, area, mouse_pos_x, mouse_pos_y):
        x, y, w, h = area
        if mouse_pos_x >= x and mouse_pos_x <= x + w:
            if mouse_pos_y >= y and mouse_pos_y <= y + h:
                return True

    def handle_unhandled_event(self, event):
        self.alert("{0} passed unhandled", [event.type], 'vv')

    def handle_quit(self, event):
        sys.exit()

    def handle_mousebuttondown(self, event):
        mouse = event.button
        mouse_x = mouse.x
        mouse_y = mouse.y
        check = self.mouse_is_inside
        possible = []
        for item, coords in self.coordinate_tracker.items():
            area, z = coords
            if check(area, mouse_x, mouse_y):
                possible.append((item, area, z))
        try:
            instance, area, z = sorted(possible, key=operator.itemgetter(2))[-1]
        except IndexError:
            self.alert("IndexError on mouse button down (No window objects under mouse)", level="v")
        else:
            self.active_item = instance
            instance.press(mouse)

    def handle_mousebuttonup(self, event):
        mouse = event.button
        area, z = self.coordinate_tracker[self.active_item]
        if self.mouse_is_inside(area, mouse.x, mouse.y):
            self.active_item.release(mouse)
        self.active_item = None

    def handle_mousewheel(self, event):
        wheel = event.wheel
        Instruction(self.active_item, "mousewheel", wheel.x, wheel.y).execute()

    def handle_mousemotion(self, event):
        motion = event.motion
        if self.active_item:
            x_change = motion.xrel
            y_change = motion.yrel
            self.active_item.mousemotion(x_change, y_change)
            
        if self.popups:
            popups = self.popups
            for item in popups:
                if not self.mouse_is_inside(item.area, motion.x, motion.y):
                    Instruction(item.parent.instance_name, "draw_texture").execute()
                    popups.remove(item)
                    item.delete()

    def handle_keydown(self, event):
        try:
            key = chr(event.key.keysym.sym)
        except ValueError:
            return # key was a modifier key
        else:
            if key == "\r":
                key = "\n"
            modifier = event.key.keysym.mod
            if modifier:
                if modifier in self.uppercase_modifiers:
                    try:
                        key = self.uppercase[key]
                    except KeyError:
                        pass
                    raise NotImplementedError
                    #stdin.write(key)
                else:
                    hotkey = self.get_hotkey(self.active_item, (key, modifier))
                    if hotkey:
                        hotkey.execute()
            else:
                raise NotImplementedError
                #stdin.write(key)
            #sys.stdout.write(key)

    def get_hotkey(self, instance, key_press):
        try:
            hotkey = instance.hotkeys.get(key_press)
            if not hotkey:
                hotkey = self.get_hotkey(instance.parent, key_press)
        except AttributeError:
            hotkey = None
        return hotkey

    def handle_keyup(self, event):
        pass

    def add_popup(self, item):
        self.popups.append(item)


class Renderer(SDL_Component):

    defaults = SDL_Component.defaults.copy()
    defaults.update({"componenttypes" : tuple()})

    def __init__(self, **kwargs):
        self.font_cache = {}        
        kwargs["wrapped_object"] = sdl2.ext.Renderer(kwargs["window"])
        super(Renderer, self).__init__(**kwargs)
        
        self.sprite_factory = self.create(Sprite_Factory, renderer=self)
        self.font_manager = self.create(Font_Manager)
        self.instructions = dict((name, getattr(self, "draw_" + name)) for 
                                  name in ("point", "line", "rect", "rect_width", "text"))
        self.instructions["fill"] = self.fill
        
    def draw_text(self, text, **kwargs):
        self.copy(self.sprite_factory.from_text(text, fontmanager=self.font_manager, 
                                                **kwargs))

    def draw_rect_width(self, area, **kwargs):
        width = kwargs.pop("width")
        x, y, w, h = area        
        
        for rect_size in xrange(1, width + 1):
            new_x = x + rect_size
            new_y = y + rect_size
            new_w = w - rect_size
            new_h = h - rect_size
            self.draw_rect((new_x, new_y, new_w, new_h), **kwargs)

    def merge_layers(self, textures):
        self.clear()
        for texture in textures:
            self.copy(texture)
        return self.sprite_factory.from_surface(self.rendertarget.get_surface())
    
    def set_render_target(self, texture):
        code = sdl2.SDL_SetRenderTarget(self.wrapped_object.renderer, texture)
        if code < 0:
            raise ValueError("error code {}. Could not set render target of renderer {} to texture {}".format(code, self.wrapped_object.renderer, texture))
            
    def draw(self, texture, draw_instructions, background=None):
        self.set_render_target(texture)
       # sdl2.SDL_SetRenderTarget(self.wrapped_object.renderer, texture)
        self.clear()
        if background:
            self.copy(background)               

        instructions = self.instructions
        for shape, args, kwargs in draw_instructions:
            self.alert("Performing: draw_{}({}{})", [shape, args, kwargs], level='v')
            instructions[shape](*args, **kwargs)     
        return texture
        
        
class Sprite_Factory(SDL_Component):

    defaults = SDL_Component.defaults.copy()

    def __init__(self, **kwargs):
        kwargs["wrapped_object"] = sdl2.ext.SpriteFactory(renderer=kwargs["renderer"])
        super(Sprite_Factory, self).__init__(**kwargs)


class Font_Manager(SDL_Component):

    defaults = SDL_Component.defaults.copy()
    defaults.update({"font_path" : os.path.join(mpre.gui.PACKAGE_LOCATION, "resources",
                                                "fonts", "Aero.ttf"),
                     "default_font_size" : 14,
                     "default_color" : (10, 150, 180),
                     "default_background" : (0, 0, 0)})

    def __init__(self, **kwargs):
        _defaults = self.defaults
        options = {"font_path" : _defaults["font_path"],
                   "size" : _defaults["default_font_size"],
                   "color" : _defaults["default_color"],
                   "bg_color" : _defaults["default_background"]}
        kwargs["wrapped_object"] = sdl2.ext.FontManager(**options)
        super(Font_Manager, self).__init__(**kwargs)
        

if __name__ == "__main__":
    import mpre.gui.gui
    mpre.gui.gui.enable()
    mpre.components["SDL_Window"].create("mpre.gui.widgetlibrary.Homescreen")
    source =\
    """def draw(shape, *args, **kwargs):
    Instruction("Homescreen", "draw", shape, *args, **kwargs).execute()

white = (255, 255, 255)
green = (0, 115, 5)
area100 = (100, 100, 200, 200)
    """
    mpre.components["Metapython"].create("mpre._metapython.Shell", startup_definitions=source)
    #Instruction("Metapython", "create", "metapython.Shell", startup_definitions=source).execute()