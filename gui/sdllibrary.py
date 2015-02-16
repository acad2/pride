import sys
import string
import heapq
import ctypes
import mmap
from operator import itemgetter

import sdl2
import sdl2.ext
import sdl2.sdlttf
sdl2.ext.init()
sdl2.sdlttf.TTF_Init()
font_module = sdl2.sdlttf

import mpre.base as base
import mpre.vmlibrary as vmlibrary
import mpre.utilities as utilities
import defaults
Instruction = base.Instruction


class Display_Wrapper(base.Wrapper):
    """used by the display internally to display all objects"""
    defaults = defaults.Window_Object

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

    def __init__(self, **kwargs):
        super(Display_Wrapper, self).__init__(**kwargs)

     #   Instruction("Organizer", "pack", wrapped_object).execute()
      #  Instruction("Display", "draw", wrapped_object).execute()

    def press(self):
        self.held = True

    #def release(self):
     #   self.held = False
      #  if Display.mouse_is_inside(self):
       #     self.click()

    def click(self):
        pass


class SDL_Component(base.Wrapper):

    defaults = defaults.SDL_Component

    def __init__(self, **kwargs):
        super(SDL_Component, self).__init__(**kwargs)


class SDL_Window(SDL_Component):

    defaults = defaults.SDL_Window

    def __init__(self, **kwargs):
        self.draw_queue = []
        self.coordinate_tracker = {}
        self.latency = utilities.Latency(name="framerate")
        self.queue_counter = 0
        self.running = False
        super(SDL_Window, self).__init__(**kwargs)

        window = sdl2.ext.Window(self.name, size=self.size)
        self.wraps(window)

        renderer = self.renderer = self.create(Renderer, window=self)
        self.user_input = self.create(User_Input)

        methods = ("point", "line", "rect", "rect_width", "text")
        names = ("draw_{0}".format(name) for name in methods)
        instructions = dict((name, getattr(renderer, name)) for name in names)
        instructions["draw_fill"] = renderer.fill
        self.instructions = instructions

        if self.showing:
            self.show()

    def create(self, *args, **kwargs):
        kwargs["sdl_window"] = self.instance_name
        instance = super(SDL_Window, self).create(*args, **kwargs)
        if hasattr(instance, "draw_texture"):
            instance_name = instance.instance_name
            if getattr(instance, "pack_on_init", False):#instance.pack_on_init:
                instance.pack()
            draw_instruction = Instruction(instance_name, "draw_texture")
            draw_instruction.priority = .05 # draw after being packed
            draw_instruction.component = instance
            draw_instruction.execute()
        return instance

    def run(self):
        renderer = self.renderer
        heappop = heapq.heappop
        instructions = self.instructions
        draw_queue = self.draw_queue

        while draw_queue:
            layer, entry_no, instruction, item = heappop(draw_queue)
            method, args, kwargs = instruction
            result = instructions[method](*args, **kwargs)
            if result:
                texture, rect = result
                renderer.copy(texture, None, rect)

        self.queue_counter = 0
        self.running = False
        renderer.present()

    def draw(self, item, mode, area, z, *args, **kwargs):
        self.user_input._update_coordinates(item, area, z)
        entry = (z, self.queue_counter, ("draw_{0}".format(mode), args, kwargs), item)
        heapq.heappush(self.draw_queue, entry)
        self.queue_counter += 1
        if not self.running:
            self.running = True
            Instruction(self.instance_name, "run").execute()

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


class User_Input(vmlibrary.Process):

    defaults = defaults.Process.copy()
    coordinate_tracker = {None : ((0, 0, 0, 0), 0)}

    def __init__(self, **kwargs):
        self.active_item = None
        self.popups = []
        super(User_Input, self).__init__(**kwargs)
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
        unhandled = self.handle_unhandled_instruction

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
        instructions = sdl2.ext.get_instructions()
        for instruction in instructions:
            self.instruction_mapping[instruction.type](instruction)
        self.process("run")

    def _update_coordinates(self, item, area, z):
        User_Input.coordinate_tracker[item] = (area, z)

    def mouse_is_inside(self, area, mouse_pos_x, mouse_pos_y):
        x, y, w, h = area
        if mouse_pos_x >= x and mouse_pos_x <= x + w:
            if mouse_pos_y >= y and mouse_pos_y <= y + h:
                return True

    def handle_unhandled_instruction(self, instruction):
        self.alert("{0} passed unhandled", [instruction.type], 'vv')

    def handle_quit(self, instruction):
        sys.exit()

    def handle_mousebuttondown(self, instruction):
        mouse = instruction.button
        mouse_x = mouse.x
        mouse_y = mouse.y
        check = self.mouse_is_inside
        possible = []
        for item, coords in self.coordinate_tracker.items():
            area, z = coords
            if check(area, mouse_x, mouse_y):
                possible.append((item, area, z))
        try:
            instance, area, z = sorted(possible, key=itemgetter(2))[-1]
        except IndexError:
            self.alert("IndexError on mouse button down (No window objects under mouse)", level="v")
        else:
            self.active_item = instance
            Instruction(instance, "press", mouse).execute()

    def handle_mousebuttonup(self, instruction):
        mouse = instruction.button
        area, z = self.coordinate_tracker[self.active_item]
        if self.mouse_is_inside(area, mouse.x, mouse.y):
            Instruction(self.active_item, "release", mouse).execute()
        self.active_item = None

    def handle_mousewheel(self, instruction):
        wheel = instruction.wheel
        Instruction(self.active_item, "mousewheel", wheel.x, wheel.y).execute()

    def handle_mousemotion(self, instruction):
        motion = instruction.motion
        if self.active_item:
            x_change = motion.xrel
            y_change = motion.yrel
            Instruction(self.active_item, "mousemotion", x_change, y_change).execute()
        if self.popups:
            popups = self.popups
            for item in popups:
                if not self.mouse_is_inside(item.area, motion.x, motion.y):
                    Instruction(item.parent.instance_name, "draw_texture").execute()
                    popups.remove(item)
                    item.delete()

    def handle_keydown(self, instruction):
        try:
            key = chr(instruction.key.keysym.sym)
        except ValueError:
            return # key was a modifier key
        else:
            if key == "\r":
                key = "\n"
            modifier = instruction.key.keysym.mod
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

    def handle_keyup(self, instruction):
        pass

    def add_popup(self, item):
        self.popups.append(item)


class Renderer(SDL_Component):

    defaults = defaults.Renderer

    def __init__(self, **kwargs):
        self.font_cache = {}
        kwargs["wrapped_object"] = sdl2.ext.Renderer(kwargs["window"])
        super(Renderer, self).__init__(**kwargs)

        self.sprite_factory = self.create(Sprite_Factory, renderer=self)
        self.font_manager = self.create(Font_Manager)

    def draw_text(self, text, rect, **kwargs):
        cache = self.font_cache
        if text in cache:
            results = cache[text]
        else:
            call = self.sprite_factory.from_text
            results = (call(text, fontmanager=self.font_manager, **kwargs), rect)
            if len(text) <= 3:
                cache[text] = results
        return results

    def draw_rect_width(self, area, **kwargs):
        width = kwargs.pop("width")
        x, y, w, h = area
        draw_rect = self.draw_rect
        print "drawing rect of width", width
        for rect_size in xrange(1, width + 1):
            new_x = x + rect_size
            new_y = y + rect_size
            new_w = w - rect_size
            new_h = h - rect_size
            draw_rect((new_x, new_y, new_w, new_h), **kwargs)


class Sprite_Factory(SDL_Component):

    defaults = defaults.Sprite_Factory

    def __init__(self, **kwargs):
        kwargs["wrapped_object"] = sdl2.ext.SpriteFactory(renderer=kwargs["renderer"])
        super(Sprite_Factory, self).__init__(**kwargs)


class Font_Manager(SDL_Component):

    defaults = defaults.Font_Manager

    def __init__(self, **kwargs):
        _defaults = self.defaults
        options = {"font_path" : _defaults["font_path"],
                   "size" : _defaults["default_font_size"],
                   "color" : _defaults["default_color"],
                   "bg_color" : _defaults["default_background"]}
        kwargs["wrapped_object"] = sdl2.ext.FontManager(**options)
        super(Font_Manager, self).__init__(**kwargs)
