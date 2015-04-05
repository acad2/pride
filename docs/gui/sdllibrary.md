mpre.gui.sdllibrary
========
No documentation available

Display_Wrapper
--------
	used by the display internally to display all objects

Default values for newly created instances:

- layer                    1
- popup                    False
- memory_mode              -1
- deleted                  False
- outline_width            5
- pack_modifier            
- held                     False
- pack_mode                
- memory_size              4096
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     [800, 600]
- color_scalar             0.6
- verbosity                
- sdl_window               SDL_Window
- color                    (0, 115, 10)
- update_flag              False
- y                        0
- x                        0

This object defines the following non-private methods:


- **press**(self):

		  No documentation available



- **click**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.sdllibrary.Display_Wrapper', class 'mpre.base.Wrapper', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Font_Manager
--------
	No docstring found

Default values for newly created instances:

- default_font_size        14
- memory_mode              -1
- deleted                  False
- verbosity                
- default_color            (15, 180, 35)
- default_background       (0, 0, 0)
- memory_size              4096
- font_path                c:\users\_\pythonbs\mpre\gui\resources\fonts\Aero.ttf
- update_flag              False

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.sdllibrary.Font_Manager', class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Proxy', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Instruction
--------
 usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority)
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. The same instruction object can be executed 
        any number of times.
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism.

Renderer
--------
	No docstring found

Default values for newly created instances:

- memory_size              4096
- memory_mode              -1
- update_flag              False
- deleted                  False
- verbosity                
- componenttypes           ()

This object defines the following non-private methods:


- **draw_rect_width**(self, area, **kwargs):

		  No documentation available



- **draw_text**(self, text, rect, **kwargs):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.sdllibrary.Renderer', class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Proxy', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


SDL_Component
--------
	No docstring found

Default values for newly created instances:

- deleted                  False
- verbosity                
- memory_size              4096
- memory_mode              -1
- update_flag              False

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Proxy', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


SDL_User_Input
--------
	No docstring found

Default values for newly created instances:

- priority                 0.04
- memory_size              4096
- memory_mode              -1
- auto_start               True
- update_flag              False
- deleted                  False
- verbosity                

This object defines the following non-private methods:


- **handle_unhandled_event**(self, event):

		  No documentation available



- **run**(self):

		  No documentation available



- **handle_mousebuttonup**(self, event):

		  No documentation available



- **handle_mousemotion**(self, event):

		  No documentation available



- **handle_quit**(self, event):

		  No documentation available



- **handle_mousebuttondown**(self, event):

		  No documentation available



- **handle_mousewheel**(self, event):

		  No documentation available



- **handle_keydown**(self, event):

		  No documentation available



- **mouse_is_inside**(self, area, mouse_pos_x, mouse_pos_y):

		  No documentation available



- **add_popup**(self, item):

		  No documentation available



- **handle_keyup**(self, event):

		  No documentation available



- **get_hotkey**(self, instance, key_press):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.sdllibrary.SDL_User_Input', class 'mpre.vmlibrary.Process', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


SDL_Window
--------
	No docstring found

Default values for newly created instances:

- layer                    0
- name                     Metapython
- memory_mode              -1
- deleted                  False
- verbosity                
- color                    (0, 0, 0)
- memory_size              4096
- update_flag              False
- y                        0
- x                        0
- showing                  True
- size                     [800, 600]

This object defines the following non-private methods:


- **draw**(self, item, mode, area, z, *args, **kwargs):

		  No documentation available



- **run**(self):

		  No documentation available



- **get_mouse_state**(self):

		  No documentation available



- **create**(self, *args, **kwargs):

		  No documentation available



- **get_mouse_position**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.sdllibrary.SDL_Window', class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Proxy', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


Sprite_Factory
--------
	No docstring found

Default values for newly created instances:

- deleted                  False
- verbosity                
- memory_size              4096
- memory_mode              -1
- update_flag              False

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.sdllibrary.Sprite_Factory', class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Proxy', class 'mpre.base.Reactor', class 'mpre.base.Base', type 'object')


itemgetter
--------
itemgetter(item, ...) --> itemgetter object

Return a callable object that fetches the given item(s) from its operand.
After f = itemgetter(2), the call f(r) returns r[2].
After g = itemgetter(2, 5, 3), the call g(r) returns (r[2], r[5], r[3])