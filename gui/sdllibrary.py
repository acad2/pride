import itertools
import operator
import os
import sys
import string
import ctypes
import collections
import traceback

import pride
import pride.base as base
import pride.vmlibrary as vmlibrary
import pride.utilities as utilities
import pride.gui
Instruction = pride.Instruction
#objects = pride.objects

import sdl2
import sdl2.ext
import sdl2.sdlttf
sdl2.ext.init()
sdl2.sdlttf.TTF_Init()
font_module = sdl2.sdlttf

class SDL_Component(base.Proxy): pass
    
        
class SDL_Window(SDL_Component):

    defaults = {"size" : pride.gui.SCREEN_SIZE, "showing" : True,
                'position' : (0, 0), 'x' : 0, 'y' : 0, 'z' : 0,
                'w' : pride.gui.SCREEN_SIZE[0], 'h' : pride.gui.SCREEN_SIZE[1],
                "area" : (0, 0) + pride.gui.SCREEN_SIZE, "priority" : .04,
                "name" : "/Python", "texture_access_flag" : sdl2.SDL_TEXTUREACCESS_TARGET,            
                "renderer_flags" : sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_TARGETTEXTURE,
                "window_flags" : None} #sdl2.SDL_WINDOW_BORDERLESS, # | sdl2.SDL_WINDOW_RESIZABLE   
    
    mutable_defaults = {"on_screen" : list}
    
    flags = {"max_layer" : 1, "invalid_layer" : 0, "running" : False}
    
    def _get_size(self):
        return (self.w, self.h)
    def _set_size(self, size):
        self.w, self.h = size
    size = property(_get_size, _set_size)
    
    def __init__(self, **kwargs):
        super(SDL_Window, self).__init__(**kwargs)
        self.run_instruction = Instruction(self.reference, "run")
        
        window = sdl2.ext.Window(self.name, size=self.size, flags=self.window_flags)
        
        self.wraps(window)
        self.window_handler = self.create(Window_Handler)
        
        self.renderer = self.create(Renderer, self, flags=self.renderer_flags)
        self.user_input = self.create(SDL_User_Input)
        self.organizer = self.create("pride.gui.gui.Organizer")
        
              
        if self.showing:
            self.show()  

        create_texture = self.renderer.sprite_factory.create_texture_sprite 
        self._texture = create_texture(self.renderer.wrapped_object,
                                       (self.size[0] * 10, self.size[1] * 10),
                                       access=self.texture_access_flag)
        
        objects["/Finalizer"].add_callback((self.reference, "delete"))
                        
    def invalidate_object(self, instance):
        if not self.running:
            self.running = True                        
            self.run_instruction.execute(priority=self.priority)
                
    def create(self, *args, **kwargs):  
        kwargs.setdefault("sdl_window", self.reference)
        instance = super(SDL_Window, self).create(*args, **kwargs)
        if hasattr(instance, 'pack'):
            try:
                instance.pack()
            except TypeError:
                if instance.__class__.__name__ != "Organizer":
                    raise
            else:
                self.on_screen.append(instance)        
        return instance
        
    def remove(self, instance):        
        try:
            self.on_screen.remove(instance)
        except ValueError:
            if hasattr(instance, "pack") and instance.__class__.__name__ != "Organizer":
                raise ValueError("Unable to remove {} from on_screen".format(instance))
        #except AttributeError:            
        #    print "That was weird"
        #    import pprint
        #    pprint.pprint(dict((key, getattr(self, key)) for key in sorted(self.__dict__)))
        #    raise
        super(SDL_Window, self).remove(instance)
        
    def run(self):        
        instructions = []
        for child in sorted(self.on_screen, key=operator.attrgetter('z')):            
            instructions.extend(child._draw_texture())          
        
        self.draw(instructions)
        self.running = False

    def draw(self, instructions):
        renderer = self.renderer
        draw_procedures = renderer.instructions
        texture = self._texture.texture
        renderer.set_render_target(texture)
        renderer.clear()
        
        for operation, args, kwargs in instructions:
            if operation == "text":
                if not args[0]:
                    continue                                
            draw_procedures[operation](*args, **kwargs)        
        
        renderer.set_render_target(None)
        area = (0, 0, self.size[0], self.size[1])
        renderer.copy(texture, area, area)
        renderer.present()
        
    def get_mouse_state(self):
        mouse = sdl2.mouse
        x = ctypes.c_long(0)
        y = ctypes.c_long(0)
        buttons = mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))

        states = (mouse.SDL_BUTTON_LMASK, mouse.SDL_BUTTON_RMASK, mouse.SDL_BUTTON_MMASK,
                  mouse.SDL_BUTTON_X1MASK, mouse.SDL_BUTTON_X2MASK)
        return ((x.value, y.value), map(lambda mask: buttons & mask, states))

    def get_mouse_position(self):
        return self.get_mouse_state()[0]

    def pack(self, modifiers=None):
        pass
            
    def delete(self):
        # delete window objects before sdl components
        for child in self.children:
            if hasattr(child, "pack") and child is not self.organizer:
                child.delete()
        super(SDL_Window, self).delete()
        objects["/Finalizer"].remove_callback((self.reference, "delete"))
        pride.Instruction.purge(self.reference)

        
class Window_Context(SDL_Window):
           
    defaults = {"showing" : False}
    
    def run(self):
        instructions = []
        for child in sorted(self.on_screen, key=operator.attrgetter('z')):            
            instructions.extend(child._draw_texture())              
        self.running = False
        return instructions        
        
    def invalidate_object(self, item):
        pass
        
        
class Window_Handler(pride.base.Base):
    
    def __init__(self, **kwargs):
        super(Window_Handler, self).__init__(**kwargs)
        self.event_switch = {sdl2.SDL_WINDOWEVENT_SHOWN : self.handle_shown,
                             sdl2.SDL_WINDOWEVENT_HIDDEN : self.handle_hidden,
                             sdl2.SDL_WINDOWEVENT_EXPOSED : self.handle_exposed,
                             sdl2.SDL_WINDOWEVENT_MOVED :  self.handle_moved,
                             sdl2.SDL_WINDOWEVENT_RESIZED : self.handle_resized,
                             sdl2.SDL_WINDOWEVENT_SIZE_CHANGED : self.handle_size_changed,
                             sdl2.SDL_WINDOWEVENT_MINIMIZED : self.handle_minimized,
                             sdl2.SDL_WINDOWEVENT_MAXIMIZED : self.handle_maximized,
                             sdl2.SDL_WINDOWEVENT_RESTORED : self.handle_restored,
                             sdl2.SDL_WINDOWEVENT_ENTER : self.handle_enter,
                             sdl2.SDL_WINDOWEVENT_LEAVE : self.handle_leave,
                             sdl2.SDL_WINDOWEVENT_FOCUS_GAINED : self.handle_focus_gained,
                             sdl2.SDL_WINDOWEVENT_FOCUS_LOST : self.handle_focus_lost,
                             sdl2.SDL_WINDOWEVENT_CLOSE : self.handle_close}
    
    def handle_event(self, event):
     #   self.alert("Handling {}", [self.event_switch[event.window.event]], level=0)
        self.event_switch[event.window.event](event)
        
    def handle_shown(self, event):
        pass
        
    def handle_hidden(self, event):
        pass
        
    def handle_exposed(self, event):
        pass
        
    def handle_moved(self, event):
        pass
        
    def handle_resized(self, event):
        pass
        
    def handle_size_changed(self, event):
        pass
        
    def handle_minimized(self, event):
        pass
        
    def handle_maximized(self, event):
        pass
        
    def handle_restored(self, event):
        pass
        
    def handle_enter(self, event):
        pass
        
    def handle_leave(self, event):
        try:
            self.parent.user_input.active_item.held = False
        except AttributeError:
            pass
        
    def handle_focus_gained(self, event):
        self.parent.user_input._ignore_click = True
        
    def handle_focus_lost(self, event):
        try:
            self.parent.user_input.active_item.held = False
        except AttributeError:
            pass
                
    def handle_close(self, event):
        pass
        
        
class SDL_User_Input(vmlibrary.Process):

    defaults = {"event_verbosity" : 0, "_ignore_click" : False, "active_item" : None}
    mutable_defaults = {"coordinate_tracker" : dict, "_coordinate_tracker" : collections.OrderedDict}
    
    verbosity = {"handle_text_input" : "vvv"}
    
    def _get_active_item(self):
        return self._active_item
    def _set_active_item(self, value):
        self._active_item = value
        
    def __init__(self, **kwargs):
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
        
        self.setup_event_handler()
        
    def setup_event_handler(self):
        unhandled = self.handle_unhandled_event
        self.handlers = {"sdl2.SDL_DOLLARGESTURE" : unhandled,
                         "sdl2.SDL_DROPFILE" : unhandled,
                         "sdl2.SDL_FINGERMOTION" : unhandled,
                         "sdl2.SDL_FINGERDOWN" : unhandled,
                         "sdl2.SDL_FINGERUP" : unhandled,
                         "sdl2.SDL_FINGERMOTION" :unhandled,
                         "sdl2.SDL_KEYDOWN" : self.handle_keydown,
                         "sdl2.SDL_KEYUP" : self.handle_keyup,
                         "sdl2.SDL_JOYAXISMOTION" : unhandled,
                         "sdl2.SDL_JOYBALLMOTION" : unhandled,
                         "sdl2.SDL_JOYHATMOTION" : unhandled,
                         "sdl2.SDL_JOYBUTTONDOWN" : unhandled,
                         "sdl2.SDL_JOYBUTTONUP" : unhandled,
                         "sdl2.SDL_MOUSEMOTION" : self.handle_mousemotion,
                         "sdl2.SDL_MOUSEBUTTONDOWN" : self.handle_mousebuttondown,
                         "sdl2.SDL_MOUSEBUTTONUP" : self.handle_mousebuttonup,
                         "sdl2.SDL_MOUSEWHEEL" : self.handle_mousewheel,
                         "sdl2.SDL_MULTIGESTURE" : unhandled,
                         "sdl2.SDL_QUIT" : self.handle_quit,
                         "sdl2.SDL_SYSWMEVENT" : unhandled,
                         "sdl2.SDL_TEXTEDITING" : unhandled,
                         "sdl2.SDL_TEXTINPUT" : self.handle_textinput,
                         "sdl2.SDL_USEREVENT" : unhandled,
                         "sdl2.SDL_WINDOWEVENT" : self.parent.window_handler.handle_event}        
        self.event_names = dict((resolve_string(key), key) for key, value in self.handlers.items())
        self.handlers = dict((resolve_string(key), value) for key, value in self.handlers.items())
        
    def run(self):
        handlers = self.handlers
        for event in sdl2.ext.get_events():
            try:
                handlers[event.type](event)
            except KeyError:
                if event.type in handlers:
                    self.alert("Exception handling {};\n{}", (self.event_names[event.type], 
                                                            traceback.format_exc()), 
                            level=0)                
                    #raise
                else:
                    self.alert("Unhandled event: {}".format(event.type))
            except Exception as error:
                self.alert("Exception handling {};\n{}", (self.event_names[event.type], 
                                                          traceback.format_exc()), 
                           level=0)
                
    def _update_coordinates(self, item, area, z):
        try:
            _, old_z = self.coordinate_tracker[item]
        except KeyError:
            pass
        else:            
            self._coordinate_tracker[old_z].remove(item)            
        try:
            self._coordinate_tracker[z].append(item)
        except KeyError:
            self._coordinate_tracker[z] = [item]
            
        self.coordinate_tracker[item] = (area, z)
        
    def _remove_from_coordinates(self, item):        
        _, old_z = self.coordinate_tracker[item]
        self._coordinate_tracker[old_z].remove(item)
        del self.coordinate_tracker[item]
        if self.active_item == item:
            self.active_item = None
    
    def handle_textinput(self, event):
        text = event.edit.text
        cursor = event.edit.start
        selection_length = event.edit.length
        self.alert("Handling textinput {} {} {}",
                   (text, cursor, selection_length), level=self.verbosity["handle_text_input"])
        if self.active_item:
            instance = objects[self.active_item]            
            instance.text_entry(text)
            #if instance.allow_text_edit:
            #    instance.text += text
        
    def handle_unhandled_event(self, event):        
        self.alert("{0} passed unhandled", [event.type], 'vv')

    def handle_quit(self, event):
        self.parent.delete()
        if "/User/Shell" not in pride.objects:
            raise SystemExit()
            
    def handle_mousebuttondown(self, event):        
        mouse = event.button
        mouse_position = (mouse.x, mouse.y)
        self.alert("mouse button down at {}", [mouse_position], level='v')        
        active_item = None
        max_z = 0
        coordinates = self.coordinate_tracker
        possible = []
        for layer_number, layer in reversed(self._coordinate_tracker.items()):
            for item in layer:
                assert item in pride.objects
                area, z = coordinates[item]
                if pride.gui.point_in_area(area, mouse_position):
                    possible.append((item, area[0]))
            if len(possible) > 1:
                active_item = sorted(possible, key=operator.itemgetter(1))[-1][0]
            elif possible:
                active_item = possible[0][0]
            if active_item:
                break
                
        old_active_item = self.active_item
        if old_active_item:
            try:
                pride.objects[old_active_item].deselect(mouse, active_item)
            except KeyError:
                if old_active_item in pride.objects:
                    raise
                    
        self.active_item = active_item
        try:
            pride.objects[active_item].select(mouse)        
        except KeyError:
            if active_item in pride.objects:
                raise              
        
        if active_item:
            if self._ignore_click:
                self._ignore_click = False
            else:
                try:
                    pride.objects[active_item].press(mouse)
                except KeyError:
                    if active_item in pride.objects:
                        raise
                    else:                        
                        self.alert("Active item has been deleted {}", (active_item, ), level=0)
                        self.active_item = None

    def handle_mousebuttonup(self, event):
        active_item = self.active_item
        if active_item:            
            instance = pride.objects[active_item]
            if instance.held:
                area, z = self.coordinate_tracker[active_item]
                mouse = event.button
                if pride.gui.point_in_area(area, (mouse.x, mouse.y)):
                    instance.release(mouse)
       
    def handle_mousewheel(self, event):
        if self.active_item:
            wheel = event.wheel
            pride.objects[self.active_item].mousewheel(wheel.x, wheel.y)

    def handle_mousemotion(self, event):        
        if self.active_item:
            motion = event.motion
            pride.objects[self.active_item].mousemotion(motion.xrel, motion.yrel)

    def handle_keydown(self, event):
        try:
            instance = pride.objects[self.active_item]
        except KeyError:
            if self.active_item is not None:
                self.alert("No instance of '{}' to handle keystrokes".format(self.active_item), level='v')
            else:
                self.alert("Active item is None; unable to handle keystrokes", level='v')
            return
            
        key_value = event.key.keysym.sym
        modifier = event.key.keysym.mod
        
      #  if key_value < 256 or key_value > 0: # in ascii range
            
        try:
            key = chr(key_value)
        except ValueError:      
            return # key was a modifier key
        else:      
            if key == "\r":
                key = "\n"
            key_press = [key, None]
            
            if modifier in self.uppercase_modifiers:
                try:
                    key = self.uppercase[key]
                except KeyError:
                    pass            
            elif modifier:
                key_press[1] = modifier
                            
            if ord(key) < 32 or key_press[1] is not None:                            
                reference, method = self.get_hotkey(instance, tuple(key_press))
                if reference is not None:                    
                    getattr(pride.objects[reference], method)()
                
    def get_hotkey(self, instance, key_press):
        if key_press in instance.hotkeys:
            callback_info = (instance.reference, instance.hotkeys[key_press])
        else:
            try:
                callback_info = self.get_hotkey(instance.parent, key_press)
            except AttributeError:
                callback_info = (None, None)
        return callback_info

    def handle_keyup(self, event):
        pass

    def save(self):        
        with pride.contextmanagers.backup(self, "handlers", "_coordinate_tracker"):
            self.handlers = None
            self._coordinate_tracker = self._coordinate_tracker.items()
            attributes = super(SDL_User_Input, self).save()
        return attributes
        
    def on_load(self, attributes):
        super(SDL_User_Input, self).on_load(attributes)
        self.setup_event_handler()
        
        
class Renderer(SDL_Component):

    defaults = {"flags" : sdl2.SDL_RENDERER_ACCELERATED,
                "blendmode_flag" : sdl2.SDL_BLENDMODE_BLEND}
                
    def __init__(self, window, **kwargs):      
        super(Renderer, self).__init__(**kwargs)
        
        self.wraps(sdl2.ext.Renderer(window, flags=self.flags))
        
        self.blendmode = self.blendmode_flag
        
        self.sprite_factory = self.create(Sprite_Factory)
        self.font_manager = self.create(Font_Manager)
        self.instructions = dict((name, getattr(self, "draw_" + name)) for 
                                  name in ("point", "line", "rect", "rect_width", "text"))
        self.instructions["fill"] = self.fill
        self.instructions["copy"] = self.copy
        self.clear()
    
    def _get_text_size(self, area, text, **kwargs):
        x, y, w, h = area
        kwargs.setdefault("width", w)
        return self.sprite_factory.from_text(text, fontmanager=self.font_manager,
                                             **kwargs).size
                                             
    def draw_text(self, area, text, **kwargs):           
        x, y, w, h = area
        texture = self.sprite_factory.from_text(text, fontmanager=self.font_manager, **kwargs)             
        _w, _h = texture.size   
        assert kwargs.get("width", None) is not None, (area, text, kwargs)
        if kwargs.get("width", None) is None and _w > w:
            self.copy(texture, dstrect=(x + 2, y + 2, 
                                        w - 2, _h),
                      srcrect=(0, 0, w, _h))
        else:
            self.copy(texture, dstrect=(x + 2, y + 2, 
                                        _w - 2, _h))        
        
    def get_text_size(self, area, text, **kwargs):
        x, y, w, h = area
        kwargs.setdefault("width", w)
        texture = self.sprite_factory.from_text(text, 
                                                fontmanager=self.font_manager, 
                                                **kwargs)        
        return texture.size        
        
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
            
    def draw(self, texture, draw_instructions, background=None, clear=True):
        self.set_render_target(texture)
        if clear:
            self.clear()
        if background:
            self.copy(background)               

        instructions = self.instructions
        for shape, args, kwargs in draw_instructions:
            instructions[shape](*args, **kwargs)     
        self.set_render_target(None)
        return texture
        
        
class Sprite_Factory(SDL_Component):

    def __init__(self, **kwargs):        
        super(Sprite_Factory, self).__init__(**kwargs)
        self.wraps(sdl2.ext.SpriteFactory(renderer=self.parent))
        
    def save(self):
        sprite_factory = self.wrapped_object
        self.wraps(None)
        attributes = super(Sprite_Factory, self).save()
        self.wraps(sprite_factory)
        print "\n\n\nReturning: ", attributes
        return attributes
        
        
class Font_Manager(SDL_Component):

    defaults = {"font_path" : os.path.join(pride.gui.PACKAGE_LOCATION,
                                           "resources", "fonts", "Aero.ttf"),
                "default_font_size" : 14, "default_color" : (150, 150, 255),
                "default_background" : (0, 0, 0)}

    def __init__(self, **kwargs):
        _defaults = self.defaults
        options = {"font_path" : _defaults["font_path"],
                   "size" : _defaults["default_font_size"],
                   "color" : _defaults["default_color"],
                   "bg_color" : _defaults["default_background"]}
        kwargs["wrapped_object"] = sdl2.ext.FontManager(**options)
        super(Font_Manager, self).__init__(**kwargs)
        
    def save(self):        
        raise NotImplementedError()
        with pride.contextmanagers.backup(self, "_bgcolor", "_textcolor", "_default_font", "fonts"):
            color = self._bgcolor
            self._bgcolor = (color.r, color.g, color.b, color.a)
            
            text_color = self._textcolor
            self._textcolor = (color.r, color.g, color.b, color.a)
            
            self.fonts = {}
            
            default_font = self._default_font
            self._default_font = self.defaults["font_path"]
            attributes = super(Font_Manager, self).save()                
        return attributes
        
    def on_load(self, attributes):
        color = attributes["_bgcolor"]
        attributes["_bgcolor"] = sdl2.ext.Color(*color)
        
        text_color = attributes["_textcolor"]
        attributes["_textcolor"] = sdl2.ext.Color(*text_color)
        raise NotImplementedError()       
        #options = {"font_path" : attributes["font_path"],
        #           "size" : attributes["default_font_size"],
        #           "color" : attributes["default_color"],
        #           "bg_color" : attributes["default_background"]}
        #attributes["wrapped_object"] = sdl2.ext.FontManager(**options)
        
        super(Font_Manager, self).on_load(attributes)
        